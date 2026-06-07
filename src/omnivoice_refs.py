import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from config import ROOT_DIR

OMNIVOICE_REF_SAMPLE_RATE = 24000
OMNIVOICE_REF_DIR = Path(ROOT_DIR) / "assets" / "omnivoice_refs"
OMNIVOICE_REF_REGISTRY = OMNIVOICE_REF_DIR / "voices.json"

DEFAULT_OMNIVOICE_REFERENCE_VOICES = [
    {
        "id": "vi_female_ref",
        "name": "VI Female Ref",
        "language": "vietnamese",
        "filename": "vi_female_ref.wav",
        "ref_text": "Xin chao, day la giong nu tieng Viet on dinh cho video ngan.",
        "instruct": "Vietnamese female narrator, young adult, clear voice, calm stable tone, natural pacing",
    },
    {
        "id": "vi_male_ref",
        "name": "VI Male Ref",
        "language": "vietnamese",
        "filename": "vi_male_ref.wav",
        "ref_text": "Xin chao, day la giong nam tieng Viet on dinh cho video ngan.",
        "instruct": "Vietnamese male narrator, young adult, clear voice, calm stable tone, natural pacing",
    },
    {
        "id": "en_female_ref",
        "name": "EN Female Ref",
        "language": "english",
        "filename": "en_female_ref.wav",
        "ref_text": "Hello, this is a stable English female reference voice for short videos.",
        "instruct": "English female narrator, young adult, clear voice, calm stable tone, natural pacing",
    },
]


def _to_numpy_audio(audio) -> np.ndarray:
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    elif hasattr(audio, "cpu") and hasattr(audio, "numpy"):
        audio = audio.cpu().numpy()
    np_audio = np.asarray(audio, dtype=np.float32)
    if np_audio.ndim == 2:
        np_audio = np_audio[0]
    return np_audio


def create_default_reference_voices(model, output_dir: Path | str = OMNIVOICE_REF_DIR) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    voices: list[dict[str, Any]] = []

    for spec in DEFAULT_OMNIVOICE_REFERENCE_VOICES:
        audio_path = output_path / spec["filename"]
        audio = model.generate(text=spec["ref_text"], instruct=spec["instruct"])
        sf.write(str(audio_path), _to_numpy_audio(audio), OMNIVOICE_REF_SAMPLE_RATE)
        voices.append(
            {
                "id": spec["id"],
                "name": spec["name"],
                "language": spec["language"],
                "ref_audio": str(audio_path),
                "ref_text": spec["ref_text"],
                "instruct": spec["instruct"],
            }
        )

    registry = {"voices": voices}
    registry_path = output_path / "voices.json"
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry


def load_reference_voice_registry(registry_path: Path | str = OMNIVOICE_REF_REGISTRY) -> dict[str, Any]:
    path = Path(registry_path)
    if not path.exists():
        return {"voices": []}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_omnivoice_reference_voice(voice_id: str, registry_path: Path | str = OMNIVOICE_REF_REGISTRY) -> dict[str, Any] | None:
    requested = str(voice_id or "").strip().lower()
    if not requested:
        return None

    registry = load_reference_voice_registry(registry_path)
    for voice in registry.get("voices", []):
        if str(voice.get("id", "")).strip().lower() != requested:
            continue
        ref_audio = str(voice.get("ref_audio", "")).strip()
        if not ref_audio or not os.path.exists(ref_audio):
            return None
        ref_text = str(voice.get("ref_text", "")).strip()
        if not ref_text:
            return None
        return voice
    return None


def list_reference_voices(registry_path: Path | str = OMNIVOICE_REF_REGISTRY) -> list[dict[str, Any]]:
    return list(load_reference_voice_registry(registry_path).get("voices", []))
