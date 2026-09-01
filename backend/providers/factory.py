"""
Provider Factory — returns the configured image generation provider.

Falls back to the placeholder provider if no API key is set.
The application runs fully without any API key.
"""
from backend.config import IMAGE_PROVIDER, OPENAI_API_KEY
from backend.providers.base import ImageGenerationProvider
from backend.providers.placeholder_provider import PlaceholderProvider
from backend.providers.openai_provider import OpenAIProvider


_provider_instance: ImageGenerationProvider | None = None


def get_provider() -> ImageGenerationProvider:
    """Get the configured image generation provider.

    Priority:
    1. If IMAGE_PROVIDER=openai and OPENAI_API_KEY is set → OpenAI
    2. Otherwise → Placeholder (always available)

    Returns:
        An ImageGenerationProvider instance.
    """
    global _provider_instance

    if _provider_instance is not None:
        return _provider_instance

    if IMAGE_PROVIDER == "openai" and OPENAI_API_KEY:
        _provider_instance = OpenAIProvider()
    else:
        _provider_instance = PlaceholderProvider()

    return _provider_instance


def get_provider_info() -> dict:
    """Return information about the current provider configuration."""
    provider = get_provider()
    return {
        "name": provider.name,
        "is_available": provider.is_available,
        "provider_type": IMAGE_PROVIDER,
        "has_api_key": bool(OPENAI_API_KEY),
    }


def reset_provider():
    """Reset the cached provider (useful for testing)."""
    global _provider_instance
    _provider_instance = None
