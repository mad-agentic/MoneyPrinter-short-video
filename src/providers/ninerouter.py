import base64
import os
from typing import Any
from urllib.parse import urlencode

import requests

from providers.schemas import GeneratedFile, SearchResult


class NineRouterError(RuntimeError):
    pass

NOAUTH_TTS_MODELS = (
    "edge-tts/vi-VN-HoaiMyNeural",
    "edge-tts/vi-VN-NamMinhNeural",
    "google-tts/vi",
    "google-tts/en",
    "local-device",
)

EDGE_TTS_FALLBACK_VOICES = (
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "ja-JP-NanamiNeural",
    "ja-JP-KeitaNeural",
    "ko-KR-SunHiNeural",
    "ko-KR-InJoonNeural",
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural",
    "th-TH-PremwadeeNeural",
    "th-TH-NiwatNeural",
    "id-ID-GadisNeural",
    "id-ID-ArdiNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-HenriNeural",
    "de-DE-KatjaNeural",
    "de-DE-ConradNeural",
    "es-ES-ElviraNeural",
    "es-ES-AlvaroNeural",
    "pt-BR-FranciscaNeural",
    "pt-BR-AntonioNeural",
    "hi-IN-SwaraNeural",
    "hi-IN-MadhurNeural",
)

GOOGLE_TTS_FALLBACK_VOICES = ("vi", "en", "ja", "ko", "zh", "th", "id", "fr", "de", "es", "pt", "hi")


class NineRouterProvider:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.base_url = str(config.get("base_url", "http://localhost:20128")).rstrip("/")
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]
        self.api_key = str(config.get("api_key", "none") or "none").strip()
        self.timeout = int(config.get("timeout", 300) or 300)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/v1/{path.lstrip('/')}"

    def _headers(self, content_type: str | None = "application/json", include_auth: bool = True) -> dict[str, str]:
        headers: dict[str, str] = {}
        if content_type:
            headers["Content-Type"] = content_type
        if include_auth and self.api_key and self.api_key.lower() != "none":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _is_noauth_tts_provider(self, provider: str) -> bool:
        return provider.strip().lower() in {"edge-tts", "google-tts", "local-device"}

    def _is_noauth_tts_model(self, model: str) -> bool:
        provider = model.split("/", 1)[0].strip().lower()
        return provider in {"edge-tts", "google-tts", "local-device"}

    def _fallback_voices(self, provider: str, language: str = "") -> list[str]:
        provider_key = provider.strip().lower()
        lang = language.strip().lower()
        if provider_key == "edge-tts":
            voices = list(EDGE_TTS_FALLBACK_VOICES)
            if lang:
                prefix = f"{lang}-"
                voices = sorted(voices, key=lambda voice: (not voice.lower().startswith(prefix), voice.lower()))
            return voices
        if provider_key == "google-tts":
            return list(GOOGLE_TTS_FALLBACK_VOICES)
        if provider_key == "local-device":
            return ["local-device"]
        return []

    def _raise_for_response(self, response: requests.Response) -> None:
        if response.ok:
            return
        detail = response.text[:500].replace(self.api_key, "***") if self.api_key else response.text[:500]
        raise NineRouterError(f"9Router HTTP {response.status_code}: {detail}")

    def _get_model_items(self, path: str) -> list[dict[str, Any]]:
        response = requests.get(self._url(path), headers=self._headers(None), timeout=60)
        self._raise_for_response(response)
        body = response.json()
        data = body.get("data", body if isinstance(body, list) else [])
        items: list[dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                items.append(item)
            elif isinstance(item, str):
                items.append({"id": item})
        return items

    def _get_models(self, path: str) -> list[str]:
        data = self._get_model_items(path)
        models = []
        for item in data:
            model_id = item.get("id") or item.get("name") or item.get("model")
            if model_id:
                models.append(str(model_id))
        return sorted(set(models))

    def get_model_info(self, model_id: str) -> dict[str, Any]:
        model_id = str(model_id or "").strip()
        if not model_id:
            raise NineRouterError("model id is required")
        response = requests.get(
            self._url(f"models/info?{urlencode({'id': model_id})}"),
            headers=self._headers(None),
            timeout=60,
        )
        self._raise_for_response(response)
        body = response.json()
        return body if isinstance(body, dict) else {"data": body}

    def list_chat_models(self) -> list[str]:
        return self._get_models("models")

    def list_image_models(self) -> list[str]:
        return self._get_models("models/image")

    def list_tts_models(self) -> list[str]:
        try:
            return sorted(set([*self._get_models("models/tts"), *NOAUTH_TTS_MODELS]))
        except NineRouterError as exc:
            message = str(exc).lower()
            if "401" in message or "unauthorized" in message or "api key required" in message:
                return list(NOAUTH_TTS_MODELS)
            raise

    def list_stt_models(self) -> list[str]:
        return self._get_models("models/stt")

    def list_embedding_models(self) -> list[str]:
        return self._get_models("models/embedding")

    def list_web_models(self) -> list[str]:
        items = self._get_model_items("models/web")
        search_models = []
        fallback_models = []
        for item in items:
            model_id = item.get("id") or item.get("name") or item.get("model")
            if not model_id:
                continue
            model = str(model_id)
            fallback_models.append(model)
            kind = str(item.get("kind", "") or "").lower()
            if kind == "websearch" or model.endswith("/search") or model in {"search-combo", "tavily", "brave-search", "serper", "exa", "perplexity"}:
                search_models.append(model)
        return sorted(set(search_models or fallback_models))

    def list_voices(self, provider: str = "edge-tts", language: str = "") -> list[str]:
        provider = str(provider or "edge-tts").strip()
        params: dict[str, str] = {"provider": provider}
        if language:
            params["lang"] = language
        response = requests.get(
            self._url(f"audio/voices?{urlencode(params)}"),
            headers=self._headers(None, include_auth=not self._is_noauth_tts_provider(provider)),
            timeout=60,
        )
        try:
            self._raise_for_response(response)
        except NineRouterError as exc:
            fallback = self._fallback_voices(provider, language)
            message = str(exc).lower()
            if fallback and ("401" in message or "unauthorized" in message or "api key required" in message):
                return fallback
            raise
        body = response.json()
        data = body.get("data") or body.get("voices") or (body if isinstance(body, list) else [])
        voices = []
        for item in data:
            if isinstance(item, dict):
                voice_id = item.get("model") or item.get("id") or item.get("voice") or item.get("voice_id") or item.get("name")
                if voice_id:
                    voices.append(str(voice_id))
            elif isinstance(item, str):
                voices.append(item)
        return sorted(set(voices)) or self._fallback_voices(provider, language)

    def _select_web_model(self, configured_model: str = "") -> str:
        configured_model = configured_model.strip()
        models = self.list_web_models()
        if configured_model and configured_model in models:
            return configured_model

        preferred = (
            "tavily/search",
            "tavily",
            "brave-search/search",
            "brave-search",
            "serper/search",
            "serper",
            "exa/search",
            "exa",
            "perplexity/search",
            "perplexity",
            "search-combo",
        )
        for model in preferred:
            if model in models:
                return model
        if models:
            return models[0]
        if configured_model:
            return configured_model
        raise NineRouterError("9Router has no web search models in /v1/models/web")

    def chat_completion(self, messages: list[dict], stream: bool = False):
        model = str(self.config.get("chat_model", "") or "").strip()
        if not model:
            raise NineRouterError("providers.ninerouter.chat_model is empty")
        payload = {"model": model, "messages": messages, "stream": stream}
        response = requests.post(self._url("chat/completions"), headers=self._headers(), json=payload, stream=stream, timeout=self.timeout)
        self._raise_for_response(response)
        return response

    def generate_image(self, prompt: str, output_path: str) -> GeneratedFile:
        model = str(self.config.get("image_model", "") or "").strip()
        if not model:
            raise NineRouterError("providers.ninerouter.image_model is empty")
        image_size = str(self.config.get("image_size", "1024x1792") or "1024x1792")
        payload = {
            "model": model,
            "prompt": prompt,
            "size": image_size,
        }
        response = requests.post(
            self._url("images/generations?response_format=binary"),
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        self._raise_for_response(response)
        self._write_media_response(response, output_path, "image")
        return GeneratedFile(path=output_path, provider="ninerouter", model=model)

    def synthesize_speech(self, text: str, output_path: str, voice: str = "", language: str = "") -> GeneratedFile:
        model = str(self.config.get("tts_model", "") or "").strip()
        if not model:
            raise NineRouterError("providers.ninerouter.tts_model is empty")
        output_ext = os.path.splitext(output_path)[1].lstrip(".").lower()
        response_format = str(self.config.get("tts_response_format", "") or output_ext or "mp3").strip().lower()
        selected_voice = str(voice or self.config.get("tts_voice", "") or "").strip()
        if selected_voice and model.lower().startswith("edge-tts"):
            model = selected_voice if selected_voice.lower().startswith("edge-tts/") else f"edge-tts/{selected_voice}"
        payload = {
            "model": model,
            "input": text,
        }
        if selected_voice:
            payload["voice"] = selected_voice
        path = "audio/speech"
        if response_format:
            path = f"{path}?{urlencode({'response_format': response_format})}"
        response = requests.post(
            self._url(path),
            headers=self._headers(include_auth=not self._is_noauth_tts_model(model)),
            json=payload,
            timeout=self.timeout,
        )
        self._raise_for_response(response)
        self._write_media_response(response, output_path, "audio")
        return GeneratedFile(path=output_path, provider="ninerouter", model=model)

    def transcribe_audio(self, audio_path: str, output_path: str, language: str = "") -> GeneratedFile:
        model = str(self.config.get("stt_model", "") or "").strip()
        if not model:
            raise NineRouterError("providers.ninerouter.stt_model is empty")
        response_format = str(self.config.get("stt_response_format", "srt") or "srt")
        data = {"model": model, "response_format": response_format}
        if language and language != "auto":
            data["language"] = language
        with open(audio_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_path), audio_file)}
            response = requests.post(
                self._url("audio/transcriptions"),
                headers=self._headers(None),
                data=data,
                files=files,
                timeout=self.timeout,
            )
        self._raise_for_response(response)
        text = self._extract_text_response(response)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
        return GeneratedFile(path=output_path, provider="ninerouter", model=model)

    def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        payload: dict[str, Any] = {
            "query": query,
            "max_results": max_results,
        }
        model = self._select_web_model(str(self.config.get("search_model", "") or ""))
        if model:
            payload["model"] = model
        response = requests.post(self._url("search"), headers=self._headers(), json=payload, timeout=120)
        self._raise_for_response(response)
        body = response.json()
        raw_results = body.get("results") or body.get("data") or body.get("items") or []
        results: list[SearchResult] = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("name") or "").strip()
            url = str(item.get("url") or item.get("href") or item.get("link") or "").strip()
            body_text = str(item.get("body") or item.get("snippet") or item.get("content") or item.get("text") or "").strip()
            published = str(item.get("published") or item.get("date") or "").strip()
            if title or url or body_text:
                results.append(SearchResult(title=title, url=url, body=body_text, published=published))
        return results

    def _extract_text_response(self, response: requests.Response) -> str:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            return response.text
        body = response.json()
        if isinstance(body, str):
            return body
        for key in ("text", "srt", "transcript", "content"):
            if body.get(key):
                return str(body[key])
        return response.text

    def _write_media_response(self, response: requests.Response, output_path: str, media_key: str) -> None:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            with open(output_path, "wb") as file:
                file.write(response.content)
            return

        body = response.json()
        data = body.get("data")
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                b64_value = first.get("b64_json") or first.get("base64") or first.get(media_key)
                if b64_value:
                    with open(output_path, "wb") as file:
                        file.write(base64.b64decode(str(b64_value)))
                    return
                url = first.get("url")
                if url:
                    media_response = requests.get(str(url), timeout=self.timeout)
                    self._raise_for_response(media_response)
                    with open(output_path, "wb") as file:
                        file.write(media_response.content)
                    return

        for key in ("b64_json", "base64", media_key):
            if body.get(key):
                with open(output_path, "wb") as file:
                    file.write(base64.b64decode(str(body[key])))
                return

        raise NineRouterError("9Router media response did not include binary, base64, or URL data")
