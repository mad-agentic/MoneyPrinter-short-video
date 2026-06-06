#!/usr/bin/env python3
import json
import os
import sys
from typing import Tuple

import requests


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def check_url(url: str, timeout: int = 3) -> Tuple[bool, str]:
    try:
        response = requests.get(url, timeout=timeout)
        return True, f"HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)

def mask_secret(value: str) -> str:
    text = str(value or "")
    if len(text) <= 8:
        return "***" if text else ""
    return f"{text[:4]}...{text[-4:]}"

def fetch_ninerouter_models(base_url: str, api_key: str, path: str) -> tuple[bool, list[str], str]:
    url = f"{base_url.rstrip('/')}/v1/{path.lstrip('/')}"
    headers = {}
    if api_key and api_key.lower() != "none":
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if not response.ok:
            detail = response.text[:200].replace(api_key, "***") if api_key else response.text[:200]
            return False, [], f"HTTP {response.status_code}: {detail}"
        body = response.json()
        data = body.get("data", body if isinstance(body, list) else [])
        models = []
        for item in data:
            if isinstance(item, str):
                models.append(item)
            elif isinstance(item, dict):
                model_id = item.get("id") or item.get("name") or item.get("model")
                if model_id:
                    models.append(str(model_id))
        return True, sorted(set(models)), "ok"
    except Exception as exc:
        detail = str(exc).replace(api_key, "***") if api_key else str(exc)
        return False, [], detail


def main() -> int:
    if not os.path.exists(CONFIG_PATH):
        fail(f"Missing config file: {CONFIG_PATH}")
        return 1

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    failures = 0

    stt_provider = str(cfg.get("stt_provider", "local_whisper")).lower()

    ok(f"stt_provider={stt_provider}")

    imagemagick_path = cfg.get("imagemagick_path", "")
    if imagemagick_path and os.path.exists(imagemagick_path):
        ok(f"imagemagick_path exists: {imagemagick_path}")
    else:
        warn(
            "imagemagick_path is not set to a valid executable path. "
            "MoviePy subtitle rendering may fail."
        )

    firefox_profile = cfg.get("firefox_profile", "")
    if firefox_profile:
        if os.path.isdir(firefox_profile):
            ok(f"firefox_profile exists: {firefox_profile}")
        else:
            warn(f"firefox_profile does not exist: {firefox_profile}")
    else:
        warn("firefox_profile is empty. Twitter/YouTube automation requires this.")

    # Ollama (LLM)
    base = str(cfg.get("ollama_base_url", "http://127.0.0.1:11434")).rstrip("/")
    reachable, detail = check_url(f"{base}/api/tags")
    if not reachable:
        fail(f"Ollama is not reachable at {base}: {detail}")
        failures += 1
    else:
        ok(f"Ollama reachable at {base}")
        try:
            tags = requests.get(f"{base}/api/tags", timeout=5).json()
            models = [m.get("name") for m in tags.get("models", [])]
            if models:
                ok(f"Ollama models available: {', '.join(models[:10])}")
            else:
                warn("No models found on Ollama. Pull a model first (e.g. 'ollama pull llama3.2:3b').")
        except Exception as exc:
            warn(f"Could not validate Ollama model list: {exc}")

    # Nano Banana 2 (image generation)
    api_key = cfg.get("nanobanana2_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
    nb2_base = str(
        cfg.get(
            "nanobanana2_api_base_url",
            "https://generativelanguage.googleapis.com/v1beta",
        )
    ).rstrip("/")
    if api_key:
        ok("nanobanana2_api_key is set")
    else:
        fail("nanobanana2_api_key is empty (and GEMINI_API_KEY is not set)")
        failures += 1

    reachable, detail = check_url(nb2_base, timeout=8)
    if not reachable:
        warn(f"Nano Banana 2 base URL could not be reached: {detail}")
    else:
        ok(f"Nano Banana 2 base URL reachable: {nb2_base}")

    ai_provider = cfg.get("ai_provider", {}) if isinstance(cfg.get("ai_provider"), dict) else {}
    providers = cfg.get("providers", {}) if isinstance(cfg.get("providers"), dict) else {}
    nr = providers.get("ninerouter", {}) if isinstance(providers.get("ninerouter"), dict) else {}
    ninerouter_active = ai_provider.get("active") == "ninerouter" and bool(nr.get("enabled", False))

    if ninerouter_active:
        nr_base = str(nr.get("base_url", cfg.get("openai_base_url", "http://localhost:20128"))).rstrip("/")
        if nr_base.endswith("/v1"):
            nr_base = nr_base[:-3]
        nr_key = str(nr.get("api_key", cfg.get("openai_api_key", "none")) or "none")
        ok(f"9Router active at {nr_base} with key={mask_secret(nr_key)}")

        capability_checks = [
            ("models/tts", "tts_model", str(nr.get("tts_model", ""))),
            ("models/stt", "stt_model", str(nr.get("stt_model", ""))),
            ("models/web", "search_model", str(nr.get("search_model", ""))),
        ]
        for path, key, selected in capability_checks:
            reachable, models, detail = fetch_ninerouter_models(nr_base, nr_key, path)
            if not reachable:
                warn(f"Could not validate 9Router {key} via /v1/{path}: {detail}")
                continue
            if selected and selected in models:
                ok(f"9Router {key} is listed in /v1/{path}: {selected}")
            elif selected:
                warn(f"9Router {key} is not listed in /v1/{path}: {selected}")
            else:
                warn(f"9Router {key} is empty")

    if stt_provider == "local_whisper":
        try:
            import faster_whisper  # noqa: F401

            ok("faster-whisper is installed")
        except Exception as exc:
            fail(f"faster-whisper is not importable: {exc}")
            failures += 1

    if failures:
        print("")
        print(f"Preflight completed with {failures} blocking issue(s).")
        return 1

    print("")
    print("Preflight passed. Local setup looks ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
