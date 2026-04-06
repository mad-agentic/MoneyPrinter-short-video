import ollama

from config import (
    get_ollama_base_url,
    get_ollama_model,
    get_llm_backend,
    get_openai_base_url,
    get_openai_model,
    get_openai_api_key,
)

_selected_model: str | None = None


def _resolve_model_name(requested_model: str | None, available_models: list[str]) -> str | None:
    """Resolve requested model against installed Ollama models.

    Supports exact match, adding ':latest', and prefix-family match.
    """
    name = (requested_model or "").strip()
    if not name or not available_models:
        return None

    # 1) Exact match first.
    if name in available_models:
        return name

    # 2) Common shorthand: llama3.2 -> llama3.2:latest
    with_latest = f"{name}:latest"
    if with_latest in available_models:
        return with_latest

    # 3) Family/prefix match (prefer shortest => usually latest tag).
    prefix = f"{name}:"
    family = sorted([m for m in available_models if m.startswith(prefix)], key=len)
    if family:
        return family[0]

    return None


def _ollama_client() -> ollama.Client:
    return ollama.Client(host=get_ollama_base_url())


def _openai_client():
    from openai import OpenAI
    return OpenAI(
        base_url=get_openai_base_url(),
        api_key=get_openai_api_key() or "none",
    )


def list_models() -> list[str]:
    """
    Lists all models available on the configured LLM backend.

    Returns:
        models (list[str]): Sorted list of model names.
    """
    backend = get_llm_backend()

    if backend == "openai_compatible":
        try:
            client = _openai_client()
            response = client.models.list()
            return sorted(m.id for m in response.data if m.id)
        except Exception:
            return []

    # Default: Ollama
    response = _ollama_client().list()
    return sorted(m.model for m in response.models if m.model)


def select_model(model: str) -> None:
    """
    Sets the model to use for all subsequent generate_text calls.

    Args:
        model (str): A model name compatible with the active backend.
    """
    global _selected_model
    _selected_model = model


def get_active_model() -> str | None:
    """
    Returns the currently selected model, or None if none has been selected.
    """
    return _selected_model


def ensure_model_selected(model_name: str | None = None) -> str:
    """
    Resolve the active model for the configured backend.

    Priority:
    1. Explicit function argument
    2. Previously selected in-memory model
    3. `openai_model` / `ollama_model` from config.json
    4. First available model from backend
    """
    global _selected_model

    backend = get_llm_backend()

    if model_name:
        if backend == "ollama":
            models = list_models()
            resolved = _resolve_model_name(model_name, models)
            _selected_model = resolved or model_name
        else:
            _selected_model = model_name
        return _selected_model

    if _selected_model:
        return _selected_model

    models = list_models()

    if backend == "openai_compatible":
        configured_model = (get_openai_model() or "").strip()
        if configured_model:
            _selected_model = configured_model
            return _selected_model
        if models:
            _selected_model = models[0]
            return _selected_model
        raise RuntimeError(
            "No model available on OpenAI-compatible backend. "
            "Set 'openai_model' in config.json or check the router is running."
        )

    # Ollama
    configured_model = (get_ollama_model() or "").strip()
    if configured_model:
        resolved = _resolve_model_name(configured_model, models)
        _selected_model = resolved or configured_model
        return _selected_model

    if models:
        _selected_model = models[0]
        return _selected_model

    raise RuntimeError(
        "No Ollama model available. Set 'ollama_model' in config.json or pull a model first, "
        "for example: ollama pull llama3.2:3b"
    )


def generate_text_stream(
    prompt: str,
    messages: list[dict] | None = None,
    model_name: str | None = None,
):
    """
    Generator that yields text chunks for streaming LLM responses.

    Args:
        prompt (str): User prompt (used when messages is None)
        messages (list[dict]): Full messages list [{role, content}]. If provided,
                               overrides prompt and enables multi-turn conversation.
        model_name (str): Optional model override.

    Yields:
        str: Text chunk (may be empty string for keep-alive)
    """
    backend = get_llm_backend()
    model = ensure_model_selected(model_name)

    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    if backend == "openai_compatible":
        client = _openai_client()
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None) or ""
            if content:
                yield content
        return

    # Default: Ollama streaming
    try:
        stream = _ollama_client().chat(
            model=model,
            messages=messages,
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "") or ""
            if content:
                yield content
    except Exception as exc:
        message = str(exc).lower()
        if "not found" in message or "status code: 404" in message:
            models = list_models()
            fallback = _resolve_model_name(model, models)
            if fallback and fallback != model:
                select_model(fallback)
                stream = _ollama_client().chat(
                    model=fallback,
                    messages=messages,
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.get("message", {}).get("content", "") or ""
                    if content:
                        yield content
            else:
                raise RuntimeError(
                    f"Ollama model '{model}' not found. Available: {', '.join(models) if models else 'none'}."
                ) from exc
        else:
            raise


def generate_text_with_messages(messages: list[dict], model_name: str | None = None) -> str:
    """
    Non-streaming chat using a full messages list (system + history + user).
    Suitable for use with asyncio.to_thread() to avoid blocking the event loop.

    Args:
        messages (list[dict]): Full [{role, content}] list including system prompt.
        model_name (str): Optional model override.

    Returns:
        str: Complete generated response.
    """
    backend = get_llm_backend()
    model = ensure_model_selected(model_name)

    if backend == "openai_compatible":
        client = _openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content.strip()

    # Default: Ollama
    try:
        response = _ollama_client().chat(model=model, messages=messages)
    except Exception as exc:
        message_str = str(exc).lower()
        if "not found" in message_str or "status code: 404" in message_str:
            models = list_models()
            fallback = _resolve_model_name(model, models)
            if fallback and fallback != model:
                select_model(fallback)
                response = _ollama_client().chat(model=fallback, messages=messages)
            else:
                raise RuntimeError(
                    f"Ollama model '{model}' not found. Available: {', '.join(models) if models else 'none'}."
                ) from exc
        else:
            raise
    return response["message"]["content"].strip()


def generate_text(prompt: str, model_name: str | None = None) -> str:
    """
    Generates text using the configured LLM backend (Ollama or OpenAI-compatible).

    Args:
        prompt (str): User prompt
        model_name (str): Optional model name override

    Returns:
        response (str): Generated text
    """
    backend = get_llm_backend()
    model = ensure_model_selected(model_name)

    if backend == "openai_compatible":
        client = _openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    # Default: Ollama
    try:
        response = _ollama_client().chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        message = str(exc).lower()
        if "not found" in message or "status code: 404" in message:
            models = list_models()
            fallback = _resolve_model_name(model, models)
            if fallback and fallback != model:
                select_model(fallback)
                response = _ollama_client().chat(
                    model=fallback,
                    messages=[{"role": "user", "content": prompt}],
                )
            else:
                raise RuntimeError(
                    f"Ollama model '{model}' not found. Available models: {', '.join(models) if models else 'none'}."
                ) from exc
        else:
            raise

    return response["message"]["content"].strip()
