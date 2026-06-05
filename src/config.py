import os
import sys
import json
import srt_equalizer

from termcolor import colored

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_config_json(file):
    """Load config JSON while tolerating UTF-8 BOM at the start of the file."""
    with open(file.name, "r", encoding="utf-8-sig") as config_file:
        return json.load(config_file)

def assert_folder_structure() -> None:
    """
    Make sure that the nessecary folder structure is present.

    Returns:
        None
    """
    # Create the .mp folder
    if not os.path.exists(os.path.join(ROOT_DIR, ".mp")):
        if get_verbose():
            print(colored(f"=> Creating .mp folder at {os.path.join(ROOT_DIR, '.mp')}", "green"))
        os.makedirs(os.path.join(ROOT_DIR, ".mp"))

def get_first_time_running() -> bool:
    """
    Checks if the program is running for the first time by checking if .mp folder exists.

    Returns:
        exists (bool): True if the program is running for the first time, False otherwise
    """
    return not os.path.exists(os.path.join(ROOT_DIR, ".mp"))

def get_email_credentials() -> dict:
    """
    Gets the email credentials from the config file.

    Returns:
        credentials (dict): The email credentials
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["email"]

def get_verbose() -> bool:
    """
    Gets the verbose flag from the config file.

    Returns:
        verbose (bool): The verbose flag
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["verbose"]

def get_firefox_profile_path() -> str:
    """
    Gets the path to the Firefox profile.

    Returns:
        path (str): The path to the Firefox profile
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["firefox_profile"]

def get_headless() -> bool:
    """
    Gets the headless flag from the config file.

    Returns:
        headless (bool): The headless flag
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["headless"]

def get_ollama_base_url() -> str:
    """
    Gets the Ollama base URL.

    Returns:
        url (str): The Ollama base URL
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("ollama_base_url", "http://127.0.0.1:11434")

def get_ollama_model() -> str:
    """
    Gets the Ollama model name from the config file.

    Returns:
        model (str): The Ollama model name, or empty string if not set.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("ollama_model", "")

def get_twitter_language() -> str:
    """
    Gets the Twitter language from the config file.

    Returns:
        language (str): The Twitter language
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["twitter_language"]

def get_nanobanana2_api_base_url() -> str:
    """
    Gets the Nano Banana 2 (Gemini image) API base URL.

    Returns:
        url (str): API base URL
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get(
            "nanobanana2_api_base_url",
            "https://generativelanguage.googleapis.com/v1beta",
        )

def get_nanobanana2_api_key() -> str:
    """
    Gets the Nano Banana 2 API key.

    Returns:
        key (str): API key
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        configured = _load_config_json(file).get("nanobanana2_api_key", "")
        return configured or os.environ.get("GEMINI_API_KEY", "")

def get_nanobanana2_model() -> str:
    """
    Gets the Nano Banana 2 model name.

    Returns:
        model (str): Model name
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("nanobanana2_model", "gemini-3.1-flash-image-preview")

def get_nanobanana2_aspect_ratio() -> str:
    """
    Gets the aspect ratio for Nano Banana 2 image generation.

    Returns:
        ratio (str): Aspect ratio
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("nanobanana2_aspect_ratio", "9:16")

def get_threads() -> int:
    """
    Gets the amount of threads to use for example when writing to a file with MoviePy.

    Returns:
        threads (int): Amount of threads
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["threads"]
    
def get_zip_url() -> str:
    """
    Gets the URL to the zip file containing the songs.

    Returns:
        url (str): The URL to the zip file
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["zip_url"]

def get_is_for_kids() -> bool:
    """
    Gets the is for kids flag from the config file.

    Returns:
        is_for_kids (bool): The is for kids flag
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["is_for_kids"]

def get_google_maps_scraper_zip_url() -> str:
    """
    Gets the URL to the zip file containing the Google Maps scraper.

    Returns:
        url (str): The URL to the zip file
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["google_maps_scraper"]

def get_google_maps_scraper_niche() -> str:
    """
    Gets the niche for the Google Maps scraper.

    Returns:
        niche (str): The niche
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["google_maps_scraper_niche"]

def get_scraper_timeout() -> int:
    """
    Gets the timeout for the scraper.

    Returns:
        timeout (int): The timeout
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["scraper_timeout"] or 300

def get_outreach_message_subject() -> str:
    """
    Gets the outreach message subject.

    Returns:
        subject (str): The outreach message subject
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["outreach_message_subject"]
    
def get_outreach_message_body_file() -> str:
    """
    Gets the outreach message body file.

    Returns:
        file (str): The outreach message body file
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["outreach_message_body_file"]

def get_tts_voice() -> str:
    """
    Gets the TTS voice from the config file.

    Returns:
        voice (str): The TTS voice
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("tts_voice", "Jasper")

def get_tts_engine() -> str:
    """
    Gets the primary TTS engine.

    Returns:
        engine (str): Preferred TTS engine name.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("tts_engine", "kitten")).strip().lower()

def get_tts_fallback_engine() -> str:
    """
    Gets the fallback TTS engine used when primary engine fails.

    Returns:
        engine (str): Fallback TTS engine name.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("tts_fallback_engine", "kitten")).strip().lower()

def get_tts_language() -> str:
    """
    Gets the preferred TTS language hint.

    Returns:
        language (str): Language hint, e.g. "auto", "vietnamese", "english".
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("tts_language", "auto")).strip().lower()

def get_tts_sample_rate() -> int:
    """
    Gets output sample rate for synthesized TTS audio.

    Returns:
        sample_rate (int): Output sample rate in Hz.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return int(_load_config_json(file).get("tts_sample_rate", 24000))

def get_omnivoice_model() -> str:
    """
    Gets OmniVoice model ID.

    Returns:
        model (str): OmniVoice model identifier.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("omnivoice_model", "k2-fsa/OmniVoice")).strip()

def get_omnivoice_device_map() -> str:
    """
    Gets OmniVoice device map strategy.

    Returns:
        device_map (str): Device placement setting.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("omnivoice_device_map", "auto")).strip()

def get_omnivoice_dtype() -> str:
    """
    Gets OmniVoice tensor dtype strategy.

    Returns:
        dtype (str): Dtype name such as "auto", "float16", "float32".
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("omnivoice_dtype", "auto")).strip().lower()

def get_omnivoice_instruct() -> str:
    """
    Gets optional OmniVoice style instruction used for voice design.

    Returns:
        instruct (str): Voice design instruction.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("omnivoice_instruct", "")).strip()

def get_tts_strict_mode() -> bool:
    """
    Gets whether TTS should fail the run when any chunk remains failed after fallback.

    Returns:
        strict_mode (bool): True to fail hard on partial TTS success.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return bool(_load_config_json(file).get("tts_strict_mode", False))

def get_assemblyai_api_key() -> str:
    """
    Gets the AssemblyAI API key.

    Returns:
        key (str): The AssemblyAI API key
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["assembly_ai_api_key"]

def get_stt_provider() -> str:
    """
    Gets the configured STT provider.

    Returns:
        provider (str): The STT provider
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("stt_provider", "local_whisper")

def get_whisper_model() -> str:
    """
    Gets the local Whisper model name.

    Returns:
        model (str): Whisper model name
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("whisper_model", "base")

def get_whisper_device() -> str:
    """
    Gets the target device for Whisper inference.

    Returns:
        device (str): Whisper device
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("whisper_device", "auto")

def get_whisper_compute_type() -> str:
    """
    Gets the compute type for Whisper inference.

    Returns:
        compute_type (str): Whisper compute type
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("whisper_compute_type", "int8")

def get_whisper_vad_filter() -> bool:
    """
    Gets whether Whisper VAD filter is enabled.

    Returns:
        enabled (bool): True to enable VAD filter.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return bool(_load_config_json(file).get("whisper_vad_filter", False))

def get_whisper_beam_size() -> int:
    """
    Gets Whisper beam size.

    Returns:
        beam_size (int): Beam width for decoding.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return int(_load_config_json(file).get("whisper_beam_size", 1))

def get_enable_title_audio() -> bool:
    """
    Gets whether the title card audio (subject read aloud before main content) is enabled.

    Returns:
        enabled (bool): True to prepend title audio (default), False to skip it.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return bool(_load_config_json(file).get("enable_title_audio", True))

def get_video_encode_preset() -> str:
    """
    Gets ffmpeg x264 preset for video encoding speed/quality tradeoff.

    Returns:
        preset (str): x264 preset value.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return str(_load_config_json(file).get("video_encode_preset", "veryfast"))

def get_video_encode_crf() -> int:
    """
    Gets ffmpeg CRF value for final video encoding.

    Returns:
        crf (int): Constant Rate Factor.
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return int(_load_config_json(file).get("video_encode_crf", 24))
    
def equalize_subtitles(srt_path: str, max_chars: int = 10) -> None:
    """
    Equalizes the subtitles in a SRT file.

    Args:
        srt_path (str): The path to the SRT file
        max_chars (int): The maximum amount of characters in a subtitle

    Returns:
        None
    """
    normalized_path = os.path.abspath(srt_path)
    try:
        equalizer_path = os.path.relpath(normalized_path, ROOT_DIR)
        if equalizer_path.startswith("..") or os.path.isabs(equalizer_path):
            equalizer_path = normalized_path
    except ValueError:
        equalizer_path = normalized_path
    previous_cwd = os.getcwd()
    try:
        os.chdir(ROOT_DIR)
        srt_equalizer.equalize_srt_file(equalizer_path, equalizer_path, max_chars)
    finally:
        os.chdir(previous_cwd)
    
def get_font() -> str:
    """
    Gets the font from the config file.

    Returns:
        font (str): The font
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["font"]

def get_fonts_dir() -> str:
    """
    Gets the fonts directory.

    Returns:
        dir (str): The fonts directory
    """
    return os.path.join(ROOT_DIR, "fonts")

def get_imagemagick_path() -> str:
    """
    Gets the path to ImageMagick.

    Returns:
        path (str): The path to ImageMagick
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)["imagemagick_path"]

def get_script_sentence_length() -> int:
    """
    Gets the forced script's sentence length.
    In case there is no sentence length in config, returns 4 when none

    Returns:
        length (int): Length of script's sentence
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        config_json = _load_config_json(file)
        if (config_json.get("script_sentence_length") is not None):
            return config_json["script_sentence_length"]
        else:
            return 4

def get_llm_backend() -> str:
    """
    Gets the LLM backend to use: 'ollama' (default) or 'openai_compatible'.

    Returns:
        backend (str): 'ollama' or 'openai_compatible'
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("llm_backend", "ollama")

def get_openai_base_url() -> str:
    """
    Gets the OpenAI-compatible API base URL (e.g. 9router: http://localhost:20128/v1).

    Returns:
        url (str): Base URL
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("openai_base_url", "http://localhost:20128/v1")

def get_openai_model() -> str:
    """
    Gets the model name to use with the OpenAI-compatible backend.

    Returns:
        model (str): Model name
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file).get("openai_model", "")

def get_openai_api_key() -> str:
    """
    Gets the API key for the OpenAI-compatible backend.
    Falls back to OPENAI_API_KEY env var.

    Returns:
        key (str): API key (can be 'none' for local routers)
    """
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        configured = _load_config_json(file).get("openai_api_key", "")
        return configured or os.environ.get("OPENAI_API_KEY", "none")

def _read_config_json() -> dict:
    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        return _load_config_json(file)

def _default_ninerouter_config(config_json: dict | None = None) -> dict:
    config_json = config_json or {}
    openai_base_url = str(config_json.get("openai_base_url", "http://localhost:20128/v1")).rstrip("/")
    if openai_base_url.endswith("/v1"):
        base_url = openai_base_url[:-3]
    else:
        base_url = openai_base_url
    return {
        "enabled": str(config_json.get("llm_backend", "")).strip() == "openai_compatible",
        "base_url": base_url or "http://localhost:20128",
        "api_key": str(config_json.get("openai_api_key", "none") or "none"),
        "chat_model": str(config_json.get("openai_model", "") or ""),
        "image_model": "gemini/gemini-3-pro-image-preview",
        "image_size": "1024x1792",
        "tts_model": "edge-tts/vi-VN-HoaiMyNeural",
        "tts_voice": "vi-VN-HoaiMyNeural",
        "tts_response_format": "wav",
        "stt_model": "gemini/gemini-2.5-flash",
        "stt_response_format": "srt",
        "search_model": "search-combo",
        "search_max_results": 10,
    }

def get_ai_provider_config() -> dict:
    config_json = _read_config_json()
    raw = config_json.get("ai_provider", {})
    if not isinstance(raw, dict):
        raw = {}
    active = str(raw.get("active", "") or "").strip().lower()
    if not active and str(config_json.get("llm_backend", "")).strip() == "openai_compatible":
        active = "ninerouter"
    return {
        "active": active,
        "fallback_to_local": bool(raw.get("fallback_to_local", True)),
    }

def get_provider_configs() -> dict:
    config_json = _read_config_json()
    providers = config_json.get("providers", {})
    if not isinstance(providers, dict):
        providers = {}

    ninerouter = _default_ninerouter_config(config_json)
    raw_ninerouter = providers.get("ninerouter", {})
    if isinstance(raw_ninerouter, dict):
        ninerouter.update(raw_ninerouter)

    if not str(ninerouter.get("search_model", "") or "").strip():
        ninerouter["search_model"] = "search-combo"

    local = providers.get("local", {})
    if not isinstance(local, dict):
        local = {}

    return {
        "ninerouter": ninerouter,
        "local": {"enabled": bool(local.get("enabled", True))},
    }

def get_ninerouter_config() -> dict:
    return get_provider_configs()["ninerouter"]

def get_post_bridge_config() -> dict:
    """
    Gets the Post Bridge configuration with safe defaults.

    Returns:
        config (dict): Sanitized Post Bridge configuration
    """
    defaults = {
        "enabled": False,
        "api_key": "",
        "platforms": ["tiktok", "instagram"],
        "account_ids": [],
        "auto_crosspost": False,
    }
    supported_platforms = {"tiktok", "instagram"}

    with open(os.path.join(ROOT_DIR, "config.json"), "r") as file:
        config_json = _load_config_json(file)

    raw_config = config_json.get("post_bridge", {})
    if not isinstance(raw_config, dict):
        raw_config = {}

    raw_platforms = raw_config.get("platforms")
    normalized_platforms = []
    seen_platforms = set()

    if raw_platforms is None:
        normalized_platforms = defaults["platforms"].copy()
    elif isinstance(raw_platforms, list):
        for platform in raw_platforms:
            normalized_platform = str(platform).strip().lower()
            if (
                normalized_platform in supported_platforms
                and normalized_platform not in seen_platforms
            ):
                normalized_platforms.append(normalized_platform)
                seen_platforms.add(normalized_platform)
    else:
        normalized_platforms = []

    raw_account_ids = raw_config.get("account_ids", defaults["account_ids"])
    normalized_account_ids = []
    if isinstance(raw_account_ids, list):
        for account_id in raw_account_ids:
            try:
                normalized_account_ids.append(int(account_id))
            except (TypeError, ValueError):
                continue

    api_key = str(raw_config.get("api_key", "")).strip()
    if not api_key:
        api_key = os.environ.get("POST_BRIDGE_API_KEY", "").strip()

    return {
        "enabled": bool(raw_config.get("enabled", defaults["enabled"])),
        "api_key": api_key,
        "platforms": normalized_platforms,
        "account_ids": normalized_account_ids,
        "auto_crosspost": bool(
            raw_config.get("auto_crosspost", defaults["auto_crosspost"])
        ),
    }
