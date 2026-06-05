from config import get_ai_provider_config, get_ninerouter_config
from providers.ninerouter import NineRouterProvider


def is_ninerouter_active() -> bool:
    ai_config = get_ai_provider_config()
    nr_config = get_ninerouter_config()
    return ai_config.get("active") == "ninerouter" and bool(nr_config.get("enabled", False))


def fallback_to_local() -> bool:
    return bool(get_ai_provider_config().get("fallback_to_local", True))


def get_ninerouter() -> NineRouterProvider:
    return NineRouterProvider(get_ninerouter_config())
