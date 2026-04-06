import os
import re
import unicodedata
import numpy as np
import soundfile as sf
from typing import List, Tuple, Optional

from config import (
    ROOT_DIR,
    get_tts_voice,
    get_tts_engine,
    get_tts_fallback_engine,
    get_tts_language,
    get_tts_sample_rate,
    get_tts_strict_mode,
    get_omnivoice_model,
    get_omnivoice_device_map,
    get_omnivoice_dtype,
    get_omnivoice_instruct,
)
from status import warning, info

KITTEN_MODEL = "KittenML/kitten-tts-mini-0.8"
KITTEN_SAMPLE_RATE = 24000
OMNIVOICE_SAMPLE_RATE = 24000


def _resolve_omnivoice_dtype(dtype_name: str):
    if dtype_name == "float16":
        try:
            import torch
            return torch.float16
        except Exception:
            return None
    if dtype_name == "float32":
        try:
            import torch
            return torch.float32
        except Exception:
            return None
    return None


def _voice_to_omnivoice_instruct(voice_name: str) -> str:
    voice_key = str(voice_name or "").strip().lower()
    mapping = {
        "jasper": "male, medium pitch",
        "milo": "male, low pitch",
        "luna": "female, medium pitch",
        "ava": "female, high pitch",
        "emma": "female, soft",
    }
    return mapping.get(voice_key, "")

class TTS:
    def __init__(self, voice: Optional[str] = None, language: Optional[str] = None) -> None:
        self._voice = (voice or get_tts_voice() or "Jasper").strip()
        self._language = (language or get_tts_language() or "auto").strip().lower()
        self._engine = (get_tts_engine() or "kitten").strip().lower()
        self._fallback_engine = (get_tts_fallback_engine() or "kitten").strip().lower()
        self._kitten_model = None
        self._omnivoice_model = None
        self._strict_mode = get_tts_strict_mode()

    @property
    def voice_name(self) -> str:
        return self._voice

    @property
    def language(self) -> str:
        return self._language

    @property
    def primary_engine(self) -> str:
        return self._engine

    @property
    def fallback_engine(self) -> str:
        return self._fallback_engine

    def _check_engine_available(self, engine: str) -> Tuple[bool, str]:
        if engine == "omnivoice":
            try:
                from omnivoice import OmniVoice  # type: ignore[reportMissingImports]  # noqa: F401
                return True, "omnivoice package importable"
            except Exception as exc:
                return False, f"omnivoice unavailable: {exc}"
        if engine == "kitten":
            try:
                from kittentts import KittenTTS  # noqa: F401
                return True, "kittentts package importable"
            except Exception as exc:
                return False, f"kittentts unavailable: {exc}"
        return False, f"unsupported engine '{engine}'"

    def runtime_status(self) -> dict:
        primary_engine = self._engine if self._engine in {"kitten", "omnivoice"} else "kitten"
        fallback_engine = self._fallback_engine if self._fallback_engine in {"kitten", "omnivoice"} else "kitten"
        primary_ready, primary_detail = self._check_engine_available(primary_engine)
        fallback_ready, fallback_detail = self._check_engine_available(fallback_engine)

        return {
            "primary_engine": primary_engine,
            "fallback_engine": fallback_engine,
            "primary_ready": primary_ready,
            "fallback_ready": fallback_ready,
            "primary_detail": primary_detail,
            "fallback_detail": fallback_detail,
            "language": self._language,
            "voice": self._voice,
        }

    def warmup(self) -> dict:
        """Warm up configured TTS engine to reduce first synthesis latency."""
        status = self.runtime_status()
        primary = status["primary_engine"]

        if primary == "omnivoice":
            if not status["primary_ready"]:
                return {
                    "ok": False,
                    "engine": primary,
                    "detail": status["primary_detail"],
                }
            self._get_omnivoice_model()
            return {
                "ok": True,
                "engine": primary,
                "detail": "OmniVoice model preloaded",
            }

        # Kitten warmup path
        if not status["primary_ready"]:
            return {
                "ok": False,
                "engine": primary,
                "detail": status["primary_detail"],
            }
        self._get_kitten_model()
        return {
            "ok": True,
            "engine": primary,
            "detail": "KittenTTS model preloaded",
        }

    def _get_kitten_model(self):
        if self._kitten_model is None:
            from kittentts import KittenTTS as KittenModel
            self._kitten_model = KittenModel(KITTEN_MODEL)
        return self._kitten_model

    def _get_omnivoice_model(self):
        if self._omnivoice_model is not None:
            return self._omnivoice_model

        try:
            from omnivoice import OmniVoice  # type: ignore[reportMissingImports]
        except Exception as exc:
            raise RuntimeError(
                "OmniVoice package is not installed. Install with: pip install omnivoice"
            ) from exc

        model_id = get_omnivoice_model() or "k2-fsa/OmniVoice"
        device_map = get_omnivoice_device_map() or "auto"
        dtype = _resolve_omnivoice_dtype(get_omnivoice_dtype())

        kwargs = {"device_map": device_map}
        if dtype is not None:
            kwargs["dtype"] = dtype

        self._omnivoice_model = OmniVoice.from_pretrained(model_id, **kwargs)
        return self._omnivoice_model

    def _normalize_tts_text(self, text: str) -> str:
        """Normalize and sanitize text for more stable ONNX inference."""
        normalized = unicodedata.normalize("NFKC", str(text))

        # Replace common typography variants with model-friendly equivalents.
        replacements = {
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "–": "-",
            "—": "-",
            "…": "...",
            "\u00a0": " ",
        }
        for src, dst in replacements.items():
            normalized = normalized.replace(src, dst)

        # Remove unsupported control chars but keep Vietnamese and punctuation.
        normalized = "".join(ch for ch in normalized if ch == "\n" or (ord(ch) >= 32 and unicodedata.category(ch) != "Cf"))
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _split_text_for_tts(self, text: str, max_chars: int = 140) -> list[str]:
        """Split text into safer chunks for KittenTTS/ONNX runtime."""
        text = self._normalize_tts_text(text)
        if not text:
            return []

        sentence_like_parts = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""

        for part in sentence_like_parts:
            part = part.strip()
            if not part:
                continue

            candidate = part if not current else f"{current} {part}"
            if len(candidate) <= max_chars:
                current = candidate
                continue

            if current:
                chunks.append(current)
                current = ""

            if len(part) <= max_chars:
                current = part
                continue

            words = part.split()
            subchunk = ""
            for word in words:
                word_candidate = word if not subchunk else f"{subchunk} {word}"
                if len(word_candidate) <= max_chars:
                    subchunk = word_candidate
                else:
                    if subchunk:
                        chunks.append(subchunk)
                    subchunk = word
            if subchunk:
                current = subchunk

        if current:
            chunks.append(current)

        return chunks

    def _render_chunk_with_fallback(self, chunk: str, depth: int = 0) -> List[np.ndarray]:
        """Render one chunk, recursively splitting when ONNX rejects shape/length."""
        safe_chunk = self._normalize_tts_text(chunk)
        if not safe_chunk:
            return []

        try:
            chunk_audio = self._get_kitten_model().generate(safe_chunk, voice=self._voice)
            return [np.asarray(chunk_audio, dtype=np.float32)]
        except Exception as chunk_exc:
            # Limit recursion depth to avoid pathological loops.
            if depth >= 3 or len(safe_chunk) <= 40:
                raise chunk_exc

            warning(
                f"TTS chunk failed at depth {depth}, splitting further ({len(safe_chunk)} chars): {chunk_exc}"
            )

            # Adaptive split strategy:
            # 1) Split by model-safe chunk size (gets stricter on deeper recursion)
            # 2) Fallback to punctuation split
            # 3) Final fallback to hard midpoint split
            adaptive_max_chars = max(40, 90 - (depth * 20))
            subchunks = self._split_text_for_tts(safe_chunk, max_chars=adaptive_max_chars)

            if len(subchunks) <= 1:
                subchunks = re.split(r"(?<=[,;:.!?])\s+", safe_chunk)
                subchunks = [s.strip() for s in subchunks if s and s.strip()]

            if len(subchunks) <= 1:
                midpoint = len(safe_chunk) // 2
                subchunks = [safe_chunk[:midpoint].strip(), safe_chunk[midpoint:].strip()]

            rendered: List[np.ndarray] = []
            for sub in subchunks:
                if not sub:
                    continue
                rendered.extend(self._render_chunk_with_fallback(sub, depth + 1))
            return rendered

    def _render_chunks(self, chunks: List[str]) -> Tuple[List[np.ndarray], int]:
        """Render chunk list and return successful chunks + fail count."""
        rendered_chunks: List[np.ndarray] = []
        failed_chunks = 0

        for idx, chunk in enumerate(chunks, start=1):
            try:
                rendered_chunks.extend(self._render_chunk_with_fallback(chunk))
            except Exception as chunk_exc:
                failed_chunks += 1
                warning(f"Skipping failed TTS chunk {idx}/{len(chunks)}: {chunk_exc}")

        return rendered_chunks, failed_chunks

    def _synthesize_with_kitten(self, normalized_text: str, output_file: str) -> str:
        if not normalized_text:
            raise ValueError("TTS input text is empty after normalization")

        try:
            audio = self._get_kitten_model().generate(normalized_text, voice=self._voice)
            sf.write(output_file, audio, KITTEN_SAMPLE_RATE)
            return output_file
        except Exception as exc:
            warning(
                f"KittenTTS single-pass generation failed ({exc}). Retrying with chunked synthesis to continue without regenerating content..."
            )

        chunks = self._split_text_for_tts(normalized_text)
        if not chunks:
            raise RuntimeError("TTS chunking produced no chunks")

        rendered_chunks, failed_chunks = self._render_chunks(chunks)

        # If too many chunks fail, reduce chunk size and retry one additional pass.
        failed_ratio = (failed_chunks / len(chunks)) if chunks else 1.0
        too_many_failures = failed_chunks > 0 and (failed_chunks >= 2 or failed_ratio >= 0.4)

        if too_many_failures:
            warning(
                f"TTS chunk failures are high ({failed_chunks}/{len(chunks)}). "
                "Reducing chunk size and retrying one additional pass..."
            )
            retry_chunks = self._split_text_for_tts(normalized_text, max_chars=80)
            retry_rendered_chunks, retry_failed_chunks = self._render_chunks(retry_chunks)

            # Prefer retry output when it successfully renders more chunks.
            if retry_rendered_chunks and len(retry_rendered_chunks) >= len(rendered_chunks):
                rendered_chunks = retry_rendered_chunks
                failed_chunks = retry_failed_chunks
                chunks = retry_chunks

        if not rendered_chunks:
            raise RuntimeError("All TTS chunks failed to render")

        if failed_chunks:
            message = f"TTS finished with partial chunk success ({len(chunks) - failed_chunks}/{len(chunks)} chunks rendered)."
            if self._strict_mode:
                raise RuntimeError(f"{message} Strict mode enabled, aborting run.")
            warning(message)

        merged_audio = np.concatenate(rendered_chunks)
        sf.write(output_file, merged_audio, KITTEN_SAMPLE_RATE)
        return output_file

    def _to_numpy_audio(self, audio) -> np.ndarray:
        if hasattr(audio, "detach"):
            audio = audio.detach().cpu().numpy()
        elif hasattr(audio, "cpu") and hasattr(audio, "numpy"):
            audio = audio.cpu().numpy()

        np_audio = np.asarray(audio, dtype=np.float32)
        if np_audio.ndim == 2:
            np_audio = np_audio[0]
        return np_audio

    def _synthesize_with_omnivoice(self, normalized_text: str, output_file: str) -> str:
        model = self._get_omnivoice_model()
        omni_instruct = get_omnivoice_instruct() or _voice_to_omnivoice_instruct(self._voice)

        kwargs = {
            "text": normalized_text,
        }
        if omni_instruct:
            kwargs["instruct"] = omni_instruct

        audio = model.generate(**kwargs)
        np_audio = self._to_numpy_audio(audio)
        sample_rate = get_tts_sample_rate() or OMNIVOICE_SAMPLE_RATE
        sf.write(output_file, np_audio, sample_rate)
        info(f"OmniVoice synthesis complete (language={self._language}, voice={self._voice})")
        return output_file

    def _synthesize_with_engine(self, engine: str, normalized_text: str, output_file: str) -> str:
        if engine == "omnivoice":
            return self._synthesize_with_omnivoice(normalized_text, output_file)
        return self._synthesize_with_kitten(normalized_text, output_file)

    def synthesize(self, text, output_file=os.path.join(ROOT_DIR, ".mp", "audio.wav")):
        normalized_text = self._normalize_tts_text(str(text))
        if not normalized_text:
            raise ValueError("TTS input text is empty after normalization")

        status = self.runtime_status()
        primary_engine = status["primary_engine"]
        fallback_engine = status["fallback_engine"]

        primary_error = None
        try:
            return self._synthesize_with_engine(primary_engine, normalized_text, output_file)
        except Exception as exc:
            primary_error = exc
            warning(f"Primary TTS engine '{primary_engine}' failed: {exc}")

        if fallback_engine == primary_engine:
            raise RuntimeError(f"TTS failed on engine '{primary_engine}': {primary_error}") from primary_error

        warning(f"Retrying TTS with fallback engine '{fallback_engine}'...")
        try:
            return self._synthesize_with_engine(fallback_engine, normalized_text, output_file)
        except Exception as fallback_exc:
            raise RuntimeError(
                f"TTS failed on both engines ({primary_engine} -> {fallback_engine}). "
                f"Primary error: {primary_error}; fallback error: {fallback_exc}"
            ) from fallback_exc
