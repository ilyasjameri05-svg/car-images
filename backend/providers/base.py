"""
Base class for AI Image Generation Providers.

This is a pluggable abstraction. The application runs fully without any API key.
Upload/drag-drop workflows work independently of any provider.
"""
from abc import ABC, abstractmethod
from PIL import Image


class ImageGenerationProvider(ABC):
    """Abstract base class for image generation providers.

    Implementations can integrate with OpenAI DALL-E, Google Imagen,
    Stability AI, or any other image generation service.

    API keys are read from environment variables — never hardcoded.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Whether this provider is configured and ready to use."""
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int | None = None,
    ) -> Image.Image:
        """Generate a single image from a text prompt.

        Args:
            prompt: Text description of the image to generate.
            width: Target width in pixels.
            height: Target height in pixels.
            seed: Optional seed for reproducibility.

        Returns:
            PIL Image of the generated illustration.

        Raises:
            ProviderError: If generation fails.
        """
        ...

    async def generate_batch(
        self,
        prompts: list[str],
        width: int = 1024,
        height: int = 1024,
        seed: int | None = None,
    ) -> list[Image.Image]:
        """Generate multiple images. Default implementation calls generate() in sequence."""
        results = []
        for prompt in prompts:
            img = await self.generate(prompt, width, height, seed)
            results.append(img)
        return results


class ProviderError(Exception):
    """Raised when image generation fails."""
    pass


class ProviderNotConfiguredError(ProviderError):
    """Raised when attempting to use a provider without required configuration."""
    pass
