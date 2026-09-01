"""
Books API — book builder, page management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.project import BookProject, BookPage
from backend.models.puzzle import ColorByNumberPuzzle

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("/{project_id}/summary")
def get_book_summary(project_id: int, db: Session = Depends(get_db)):
    """Get a summary of the book including all pages."""
    project = db.query(BookProject).filter(BookProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pages = (db.query(BookPage)
             .filter(BookPage.project_id == project_id)
             .order_by(BookPage.page_number)
             .all())

    page_summaries = []
    for page in pages:
        summary = {
            "id": page.id,
            "page_number": page.page_number,
            "page_type": page.page_type,
            "title": page.title,
            "puzzle_id": page.puzzle_id,
            "source_image_path": page.source_image_path,
            "has_puzzle": page.puzzle_id is not None,
        }
        page_summaries.append(summary)

    return {
        "project_id": project.id,
        "name": project.name,
        "subtitle": project.subtitle,
        "author": project.author,
        "theme": project.theme,
        "difficulty": project.difficulty,
        "grid_size": project.grid_size,
        "color_count": project.color_count,
        "page_size": project.page_size,
        "orientation": project.orientation,
        "answer_key_position": project.answer_key_position,
        "total_pages": len(pages),
        "puzzle_pages": len([p for p in pages if p.page_type == "puzzle"]),
        "answer_pages": len([p for p in pages if p.page_type == "answer"]),
        "pages": page_summaries,
    }
