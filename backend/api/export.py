"""
Export API — PDF/PNG/SVG export with pre-validation.

Exports are BLOCKED if validation fails.
"""
import io
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.project import BookProject, BookPage
from backend.models.puzzle import ColorByNumberPuzzle
from backend.core.puzzle_generator import PuzzleData
from backend.core.palette_engine import NamedColor
from backend.renderers.pdf_renderer import render_puzzle_pdf, render_answer_pdf, render_book_pdf
from backend.renderers.png_renderer import render_puzzle_png, render_answer_png
from backend.renderers.svg_renderer import render_puzzle_svg, render_answer_svg
from backend.renderers.page_layout import calculate_layout
from backend.validators.book_validator import validate_puzzle, validate_book, validate_layout
from backend.schemas.export import ExportRequest, SinglePageExportRequest, ValidationResult
from backend.config import PROJECTS_DIR

router = APIRouter(prefix="/api/export", tags=["export"])


@router.post("/validate")
def validate_export(request: ExportRequest, db: Session = Depends(get_db)):
    """Validate book before export. Returns detailed validation report."""
    project = db.query(BookProject).filter(
        BookProject.id == request.project_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    puzzles = _get_project_puzzles(project, db)
    if not puzzles:
        return ValidationResult(
            is_valid=False,
            errors=["No puzzles found in this project"],
        )

    result = validate_book(
        puzzles,
        request.page_size or project.page_size,
        request.orientation or project.orientation,
    )

    return ValidationResult(
        is_valid=result["valid"],
        errors=result["errors"],
        warnings=result.get("warnings", []),
        page_results=result.get("page_results", []),
    )


@router.post("/pdf")
def export_pdf(request: ExportRequest, db: Session = Depends(get_db)):
    """Export complete book as PDF. Validates first — blocks if invalid."""
    project = db.query(BookProject).filter(
        BookProject.id == request.project_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    puzzles = _get_project_puzzles(project, db)
    if not puzzles:
        raise HTTPException(status_code=400, detail="No puzzles in project")

    # Validate before export
    validation = validate_book(
        puzzles,
        request.page_size or project.page_size,
        request.orientation or project.orientation,
    )
    if not validation["valid"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Validation failed — cannot export",
                "errors": validation["errors"],
                "warnings": validation.get("warnings", []),
            }
        )

    # Determine which puzzles to include
    if request.export_type == "puzzles":
        # Only puzzle pages (no answers)
        pdf_bytes = render_book_pdf(
            puzzles,
            request.page_size or project.page_size,
            request.orientation or project.orientation,
            answer_key_position="none",  # no answers
            book_title=project.name,
        )
    elif request.export_type == "answers":
        # Only answer pages
        pdf_bytes = _render_answers_only(
            puzzles,
            request.page_size or project.page_size,
            request.orientation or project.orientation,
        )
    else:
        # Complete book
        pdf_bytes = render_book_pdf(
            puzzles,
            request.page_size or project.page_size,
            request.orientation or project.orientation,
            answer_key_position=project.answer_key_position,
            book_title=project.name,
        )

    # Save to project directory
    project_dir = PROJECTS_DIR / str(project.id)
    project_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{project.name.replace(' ', '_')}_{request.export_type}.pdf"
    filepath = project_dir / filename
    filepath.write_bytes(pdf_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-File-Path": str(filepath),
        }
    )


@router.post("/png")
def export_png(request: SinglePageExportRequest, db: Session = Depends(get_db)):
    """Export a single puzzle or answer as PNG."""
    puzzle_data = _get_puzzle_data(request.puzzle_id, db)

    if request.export_type == "answer":
        png_bytes = render_answer_png(puzzle_data)
    else:
        png_bytes = render_puzzle_png(puzzle_data)

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="puzzle_{request.puzzle_id}.png"'},
    )


@router.post("/svg")
def export_svg(request: SinglePageExportRequest, db: Session = Depends(get_db)):
    """Export a single puzzle or answer as SVG."""
    puzzle_data = _get_puzzle_data(request.puzzle_id, db)

    if request.export_type == "answer":
        svg_content = render_answer_svg(puzzle_data)
    else:
        svg_content = render_puzzle_svg(puzzle_data)

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f'attachment; filename="puzzle_{request.puzzle_id}.svg"'},
    )


# ── Helpers ────────────────────────────────────────────────────────────

def _get_project_puzzles(project: BookProject, db: Session) -> list[PuzzleData]:
    """Get all PuzzleData objects for a project."""
    pages = (db.query(BookPage)
             .filter(BookPage.project_id == project.id, BookPage.page_type == "puzzle")
             .order_by(BookPage.page_number)
             .all())

    puzzles = []
    for page in pages:
        if page.puzzle_id:
            db_puzzle = db.query(ColorByNumberPuzzle).filter(
                ColorByNumberPuzzle.id == page.puzzle_id
            ).first()
            if db_puzzle:
                puzzles.append(_db_to_puzzle_data(db_puzzle, page.title))

    return puzzles


def _get_puzzle_data(puzzle_id: int, db: Session) -> PuzzleData:
    """Get PuzzleData for a single puzzle."""
    db_puzzle = db.query(ColorByNumberPuzzle).filter(
        ColorByNumberPuzzle.id == puzzle_id
    ).first()
    if not db_puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return _db_to_puzzle_data(db_puzzle)


def _db_to_puzzle_data(db_puzzle: ColorByNumberPuzzle, title: str = "") -> PuzzleData:
    """Convert database puzzle to PuzzleData."""
    palette = [
        NamedColor(
            color_id=p["color_id"],
            color_name=p["color_name"],
            color_hex=p["color_hex"],
        )
        for p in db_puzzle.palette
    ]
    return PuzzleData(
        grid_width=db_puzzle.grid_width,
        grid_height=db_puzzle.grid_height,
        cells=db_puzzle.cells,
        palette=palette,
        color_count=db_puzzle.color_count,
        requested_color_count=getattr(db_puzzle, "requested_color_count", "auto") or "auto",
        seed=db_puzzle.seed,
        title=title or db_puzzle.title,
        difficulty=db_puzzle.difficulty,
        source_image_path=db_puzzle.source_image_path,
    )


def _render_answers_only(
    puzzles: list[PuzzleData], page_size: str, orientation: str
) -> bytes:
    """Render only the answer key pages."""
    from reportlab.pdfgen import canvas as rl_canvas
    from backend.renderers.pdf_renderer import _draw_answer_page
    from backend.renderers.page_layout import calculate_layout

    buf = io.BytesIO()
    sample = calculate_layout(page_size, orientation,
                              puzzles[0].grid_width, puzzles[0].grid_height)
    c = rl_canvas.Canvas(buf, pagesize=(sample.page_width, sample.page_height))

    for idx, puzzle in enumerate(puzzles):
        layout = calculate_layout(
            page_size, orientation,
            puzzle.grid_width, puzzle.grid_height,
            color_count=len(puzzle.palette),
        )
        title = f"Answer Key - {puzzle.title}" if puzzle.title else "Answer Key"
        _draw_answer_page(c, puzzle, layout, title, idx + 1)
        c.showPage()

    c.save()
    return buf.getvalue()
