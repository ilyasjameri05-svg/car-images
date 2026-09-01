"""
Puzzles API — generate puzzles, get data, preview.
"""
import io
import base64
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from PIL import Image

from backend.database import get_db
from backend.models.puzzle import ColorByNumberPuzzle
from backend.core.puzzle_generator import generate_puzzle, PuzzleData
from backend.core.palette_engine import NamedColor
from backend.renderers.puzzle_renderer import render_puzzle_image, render_color_key_image
from backend.renderers.answer_renderer import render_answer_image
from backend.schemas.puzzle import PuzzleGenerateRequest, PuzzleResponse, PuzzlePreviewRequest

router = APIRouter(prefix="/api/puzzles", tags=["puzzles"])


@router.post("/generate")
def generate_puzzle_endpoint(request: PuzzleGenerateRequest,
                              db: Session = Depends(get_db)):
    """Generate a puzzle from a source image + settings.

    The image is processed ONCE. The resulting PuzzleData is used for both
    the puzzle (numbers) and answer key (colors).
    """
    # Load source image
    img_path = Path(request.source_image_path)
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Source image not found")

    try:
        source_image = Image.open(img_path).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    try:
        # Generate puzzle (ONCE — never reprocess)
        puzzle_data = generate_puzzle(
            source_image=source_image,
            grid_width=request.grid_width,
            grid_height=request.grid_height,
            color_count=request.color_count,
            seed=request.seed,
            title=request.title,
            difficulty=request.difficulty,
            source_image_path=request.source_image_path,
        )

        # Save to database
        db_puzzle = ColorByNumberPuzzle(
            seed=puzzle_data.seed,
            source_image_path=str(img_path),
            grid_width=puzzle_data.grid_width,
            grid_height=puzzle_data.grid_height,
            color_count=len(puzzle_data.palette),
            requested_color_count=str(request.color_count),
            difficulty=puzzle_data.difficulty,
            title=puzzle_data.title,
        )
        db_puzzle.cells = puzzle_data.cells
        db_puzzle.palette = [p.to_dict() for p in puzzle_data.palette]
        db.add(db_puzzle)
        db.commit()
        db.refresh(db_puzzle)

        return {
            "id": db_puzzle.id,
            "grid_width": puzzle_data.grid_width,
            "grid_height": puzzle_data.grid_height,
            "cell_count": len(puzzle_data.cells),
            "color_count": len(puzzle_data.palette),
            "resolved_color_count": len(puzzle_data.palette),
            "requested_color_count": str(request.color_count),
            "palette": [p.to_dict() for p in puzzle_data.palette],
            "seed": puzzle_data.seed,
            "title": puzzle_data.title,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Puzzle generation failed: {str(e)}")


@router.get("/{puzzle_id}")
def get_puzzle(puzzle_id: int, db: Session = Depends(get_db)):
    """Get puzzle data by ID."""
    puzzle = db.query(ColorByNumberPuzzle).filter(
        ColorByNumberPuzzle.id == puzzle_id
    ).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    return {
        "id": puzzle.id,
        "seed": puzzle.seed,
        "source_image_path": puzzle.source_image_path,
        "grid_width": puzzle.grid_width,
        "grid_height": puzzle.grid_height,
        "color_count": puzzle.color_count,
        "resolved_color_count": puzzle.color_count,
        "requested_color_count": puzzle.requested_color_count if hasattr(puzzle, "requested_color_count") else "auto",
        "difficulty": puzzle.difficulty,
        "title": puzzle.title,
        "cells": puzzle.cells,
        "palette": puzzle.palette,
    }


@router.post("/preview")
async def preview_puzzle(request: PuzzlePreviewRequest):
    """Generate a preview image (puzzle, answer, or source).

    Returns a base64-encoded PNG image.
    """
    img_path = Path(request.source_image_path)
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="Source image not found")

    try:
        source_image = Image.open(img_path).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    try:
        if request.preview_type == "source":
            # Return the source image as preview
            preview = source_image.copy()
            preview.thumbnail((600, 600), Image.LANCZOS)
            resolved_count = None
        else:
            # Generate puzzle data
            puzzle_data = generate_puzzle(
                source_image=source_image,
                grid_width=request.grid_width,
                grid_height=request.grid_height,
                color_count=request.color_count,
                difficulty=request.difficulty,
                seed=request.seed,
            )

            if request.preview_type == "answer":
                preview = render_answer_image(puzzle_data, 600, 600)
            else:
                preview = render_puzzle_image(puzzle_data, 600, 600)

            resolved_count = len(puzzle_data.palette)

        # Convert to base64
        buf = io.BytesIO()
        preview.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return {
            "image": f"data:image/png;base64,{b64}",
            "width": preview.size[0],
            "height": preview.size[1],
            "color_count": resolved_count,
            "resolved_color_count": resolved_count,
            "requested_color_count": str(request.color_count),
            "recommended_color_count": resolved_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/{puzzle_id}/preview/{preview_type}")
def get_puzzle_preview(puzzle_id: int, preview_type: str,
                       db: Session = Depends(get_db)):
    """Get a preview image for a saved puzzle."""
    puzzle = db.query(ColorByNumberPuzzle).filter(
        ColorByNumberPuzzle.id == puzzle_id
    ).first()
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")

    puzzle_data = _db_puzzle_to_data(puzzle)

    if preview_type == "answer":
        img = render_answer_image(puzzle_data, 600, 600)
    else:
        img = render_puzzle_image(puzzle_data, 600, 600)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")


def _db_puzzle_to_data(puzzle: ColorByNumberPuzzle) -> PuzzleData:
    """Convert a database puzzle to PuzzleData."""
    palette = [
        NamedColor(
            color_id=p["color_id"],
            color_name=p["color_name"],
            color_hex=p["color_hex"],
        )
        for p in puzzle.palette
    ]
    return PuzzleData(
        grid_width=puzzle.grid_width,
        grid_height=puzzle.grid_height,
        cells=puzzle.cells,
        palette=palette,
        seed=puzzle.seed,
        title=puzzle.title,
        difficulty=puzzle.difficulty,
        source_image_path=puzzle.source_image_path,
    )
