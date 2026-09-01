"""
Projects API — CRUD operations for book projects.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.project import BookProject, BookPage
from backend.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    PageCreate, PageResponse, PageReorder,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    data_dict = data.model_dump()
    allowed_cols = {c.name for c in BookProject.__table__.columns}
    filtered_data = {k: v for k, v in data_dict.items() if k in allowed_cols}
    if "color_count" in filtered_data and filtered_data["color_count"] is not None:
        filtered_data["color_count"] = str(filtered_data["color_count"])
    project = BookProject(**filtered_data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_to_response(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(BookProject).order_by(BookProject.updated_at.desc()).all()
    return [_project_to_response(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(BookProject).filter(BookProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_response(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate,
                   db: Session = Depends(get_db)):
    project = db.query(BookProject).filter(BookProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return _project_to_response(project)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(BookProject).filter(BookProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


# ── Pages ──────────────────────────────────────────────────────────────

@router.get("/{project_id}/pages", response_model=list[PageResponse])
def list_pages(project_id: int, db: Session = Depends(get_db)):
    pages = (db.query(BookPage)
             .filter(BookPage.project_id == project_id)
             .order_by(BookPage.page_number)
             .all())
    return pages


@router.post("/{project_id}/pages", response_model=PageResponse)
def add_page(project_id: int, data: PageCreate, db: Session = Depends(get_db)):
    project = db.query(BookProject).filter(BookProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    page = BookPage(project_id=project_id, **data.model_dump())
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.delete("/{project_id}/pages/{page_id}")
def delete_page(project_id: int, page_id: int, db: Session = Depends(get_db)):
    page = (db.query(BookPage)
            .filter(BookPage.id == page_id, BookPage.project_id == project_id)
            .first())
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete(page)
    db.commit()
    return {"message": "Page deleted"}


@router.put("/{project_id}/pages/reorder")
def reorder_pages(project_id: int, data: PageReorder,
                  db: Session = Depends(get_db)):
    for idx, page_id in enumerate(data.page_ids):
        page = (db.query(BookPage)
                .filter(BookPage.id == page_id, BookPage.project_id == project_id)
                .first())
        if page:
            page.page_number = idx + 1
    db.commit()
    return {"message": "Pages reordered"}


@router.post("/{project_id}/pages/{page_id}/duplicate", response_model=PageResponse)
def duplicate_page(project_id: int, page_id: int,
                   db: Session = Depends(get_db)):
    page = (db.query(BookPage)
            .filter(BookPage.id == page_id, BookPage.project_id == project_id)
            .first())
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Get max page number
    max_num = (db.query(BookPage.page_number)
               .filter(BookPage.project_id == project_id)
               .order_by(BookPage.page_number.desc())
               .first())
    next_num = (max_num[0] + 1) if max_num else 1

    new_page = BookPage(
        project_id=project_id,
        page_number=next_num,
        page_type=page.page_type,
        title=page.title,
        puzzle_id=page.puzzle_id,
        source_image_path=page.source_image_path,
    )
    db.add(new_page)
    db.commit()
    db.refresh(new_page)
    return new_page


def _project_to_response(project: BookProject) -> ProjectResponse:
    cc = project.color_count
    if isinstance(cc, str) and cc.isdigit():
        cc = int(cc)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        subtitle=project.subtitle,
        author=project.author,
        theme=project.theme,
        difficulty=project.difficulty,
        grid_size=project.grid_size,
        color_count=cc,
        requested_color_count=str(project.color_count),
        page_size=project.page_size,
        orientation=project.orientation,
        answer_key_position=project.answer_key_position,
        decoration_mode=project.decoration_mode,
        decoration_theme=project.decoration_theme,
        seed=project.seed,
        page_count=len(project.pages),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
