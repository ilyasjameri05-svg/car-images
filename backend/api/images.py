"""
Images API — upload, AI generate, analyze images.

Upload and drag-drop work fully without any API key.
AI generation requires a configured provider.
"""
import os
import uuid
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from PIL import Image

from backend.config import TEMP_DIR, PROJECTS_DIR, build_image_prompt, THEME_SUBJECTS
from backend.core.image_analyzer import analyze_image
from backend.providers.factory import get_provider, get_provider_info
from backend.providers.base import ProviderError, ProviderNotConfiguredError
from backend.schemas.puzzle import ImageAnalysisResponse, ImageGenerateRequest

router = APIRouter(prefix="/api/images", tags=["images"])


@router.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    """Upload one or more images. Stored temporarily — NOT in permanent library."""
    results = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            results.append({"filename": file.filename, "error": "Not an image file"})
            continue

        try:
            # Generate unique filename
            ext = Path(file.filename).suffix or ".png"
            unique_name = f"{uuid.uuid4().hex}{ext}"
            filepath = TEMP_DIR / unique_name

            # Save to temp directory (NOT permanent)
            content = await file.read()
            filepath.write_bytes(content)

            # Validate image
            img = Image.open(filepath)
            img.verify()

            results.append({
                "filename": file.filename,
                "path": str(filepath),
                "temp_name": unique_name,
                "size": len(content),
                "success": True,
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": f"Upload failed: {str(e)}",
                "success": False,
            })

    return {"uploaded": results, "count": len([r for r in results if r.get("success")])}


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image_endpoint(image_path: str = Form(...)):
    """Analyze image quality for mosaic suitability."""
    path = Path(image_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    try:
        img = Image.open(path).convert("RGB")
        result = analyze_image(img)
        return ImageAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/generate")
async def generate_image(request: ImageGenerateRequest):
    """Generate an AI image from a prompt. Requires a configured provider."""
    provider = get_provider()

    if not provider.is_available:
        raise HTTPException(
            status_code=503,
            detail=(
                "No image generation provider is configured. "
                "Set IMAGE_PROVIDER and the appropriate API key environment variable, "
                "or use the Upload Image workflow instead."
            )
        )

    try:
        # Build the optimized prompt
        if request.prompt:
            prompt = request.prompt
        elif request.subject:
            prompt = build_image_prompt(request.subject, request.theme)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'prompt' or 'subject' must be provided"
            )

        images = []
        for i in range(request.count):
            img = await provider.generate(prompt, 1024, 1024)

            # Save to temp
            filename = f"generated_{uuid.uuid4().hex}.png"
            filepath = TEMP_DIR / filename
            img.save(filepath, "PNG")

            images.append({
                "path": str(filepath),
                "filename": filename,
                "index": i + 1,
            })

        return {
            "images": images,
            "count": len(images),
            "provider": provider.name,
        }

    except ProviderNotConfiguredError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ProviderError as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/generate-bulk")
async def generate_bulk(theme: str = Form("animals"),
                        count: int = Form(10)):
    """Bulk generate images for a theme. Minimizes repetition."""
    provider = get_provider()

    if not provider.is_available:
        raise HTTPException(
            status_code=503,
            detail="No image generation provider configured."
        )

    subjects = THEME_SUBJECTS.get(theme, THEME_SUBJECTS["animals"])
    results = []
    errors = []

    for i in range(count):
        # Cycle through subjects to minimize repetition
        subject = subjects[i % len(subjects)]
        prompt = build_image_prompt(subject, theme)

        try:
            img = await provider.generate(prompt, 1024, 1024, seed=i)
            filename = f"bulk_{theme}_{i:03d}_{uuid.uuid4().hex[:8]}.png"
            filepath = TEMP_DIR / filename
            img.save(filepath, "PNG")

            # Analyze quality
            analysis = analyze_image(img)

            results.append({
                "index": i + 1,
                "subject": subject,
                "path": str(filepath),
                "filename": filename,
                "analysis": analysis,
                "success": True,
            })
        except Exception as e:
            errors.append({
                "index": i + 1,
                "subject": subject,
                "error": str(e),
                "success": False,
            })

    return {
        "results": results,
        "errors": errors,
        "total": count,
        "successful": len(results),
        "failed": len(errors),
    }


@router.get("/provider-info")
async def provider_info():
    """Get information about the configured image generation provider."""
    return get_provider_info()


@router.get("/themes")
async def list_themes():
    """List available image themes and their subjects."""
    return {
        "themes": {
            name: subjects for name, subjects in THEME_SUBJECTS.items()
        }
    }


@router.get("/temp/{filename}")
async def get_temp_image(filename: str):
    """Serve a temporary image file."""
    filepath = TEMP_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)
