"""
Pydantic schemas for Export API requests/responses.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    project_id: int
    format: str = "pdf"       # "pdf" | "png" | "svg"
    export_type: str = "complete"  # "complete" | "puzzles" | "answers"
    page_size: Optional[str] = None   # Override project page_size
    orientation: Optional[str] = None  # Override project orientation


class SinglePageExportRequest(BaseModel):
    puzzle_id: int
    format: str = "pdf"
    export_type: str = "puzzle"  # "puzzle" | "answer"


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    page_results: list[dict] = []
