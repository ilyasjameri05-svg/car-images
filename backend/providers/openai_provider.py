"""
OpenAI DALL-E Image Generation Provider.

Requires OPENAI_API_KEY environment variable. This is a ready-to-configure
integration — it will NOT be used unless the API key is set.
"""
import io
from PIL import Image
from backend.providers.base import (
    ImageGenerationProvider, ProviderError, ProviderNotConfiguredError
)
from backend.config import OPENAI_API_KEY, OPENAI_MODEL, build_image_prompt


class OpenAIProvider(ImageGenerationProvider):
    """OpenAI DALL-E image generation provider.

    Configure by setting environment variables:
        OPENAI_API_KEY=sk-...
        OPENAI_IMAGE_MODEL=dall-e-3  (optional, defaults to dall-e-3)
        IMAGE_PROVIDER=openai
    """

    @property
    def name(self) -> str:
        return "OpenAI DALL-E"

    @property
    def is_available(self) -> bool:
        return bool(OPENAI_API_KEY)

    async def generate(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int | None = None,
    ) -> Image.Image:
        if not self.is_available:
            raise ProviderNotConfiguredError(
                "OpenAI API key not configured. Set the OPENAI_API_KEY "
                "environment variable to use this provider."
            )

        try:
            import httpx

            # Determine size parameter (DALL-E 3 supports specific sizes)
            size = _get_dalle_size(width, height)

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": OPENAI_MODEL,
                        "prompt": prompt,
                        "n": 1,
                        "size": size,
                        "quality": "standard",
                        "response_format": "b64_json",
                    },
                )

                if response.status_code != 200:
                    error_msg = response.text
                    raise ProviderError(
                        f"OpenAI API error ({response.status_code}): {error_msg}"
                    )

                data = response.json()
                import base64
                b64_data = data["data"][0]["b64_json"]
                image_bytes = base64.b64decode(b64_data)
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                # Resize to requested dimensions if different from DALL-E output
                if image.size != (width, height):
                    image = image.resize((width, height), Image.LANCZOS)

                return image

        except ImportError:
            raise ProviderError("httpx package is required for OpenAI provider")
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Image generation failed: {str(e)}")


def _get_dalle_size(width: int, height: int) -> str:
    """Map requested dimensions to the closest DALL-E 3 supported size."""
    # DALL-E 3 supports: 1024x1024, 1024x1792, 1792x1024
    aspect = width / height
    if aspect > 1.3:
        return "1792x1024"
    elif aspect < 0.77:
        return "1024x1792"
    else:
        return "1024x1024"
