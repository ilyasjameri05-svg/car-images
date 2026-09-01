"""
Pydantic schemas for Puzzle API requests/responses.
"""
from typing import Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


def _validate_color_count_val(v: Any) -> Union[int, str]:
    if v is None:
        return "auto"
    if isinstance(v, str):
        v_str = v.strip().lower()
        if v_str == "auto":
            return "auto"
        try:
            v_int = int(v_str)
            if 6 <= v_int <= 20:
                return v_int
        except ValueError:
            pass
        raise ValueError(f"Invalid color_count: '{v}'. Must be 'auto' or an integer between 6 and 20.")
    if isinstance(v, (int, float)):
        v_int = int(v)
        if 6 <= v_int <= 20:
            return v_int
        raise ValueError(f"color_count must be between 6 and 20, got {v}")
    raise ValueError(f"Invalid color_count type: {type(v)}")


class CellSchema(BaseModel):
    row: int
    col: int
    color_id: int
    color_hex: str


class PaletteColorSchema(BaseModel):
    color_id: int
    color_name: str
    color_hex: str


class PuzzleGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_image_path: str = ""
    grid_width: int = Field(30, ge=20, le=60)
    grid_height: int = Field(30, ge=20, le=60)
    color_count: Union[int, str] = "auto"
    difficulty: str = "medium"
    title: str = ""
    seed: Optional[int] = None
    project_id: Optional[int] = None

    @field_validator("color_count", mode="before")
    @classmethod
    def validate_color_count(cls, v):
        return _validate_color_count_val(v)


class PuzzleResponse(BaseModel):
    id: int
    seed: Optional[int]
    source_image_path: str
    grid_width: int
    grid_height: int
    color_count: int  # Actual resolved integer count
    requested_color_count: Union[int, str] = "auto"
    resolved_color_count: Optional[int] = None
    difficulty: str
    title: str
    cells: list[CellSchema]
    palette: list[PaletteColorSchema]

    class Config:
        from_attributes = True


class PuzzlePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_image_path: str = ""
    grid_width: int = Field(30, ge=20, le=60)
    grid_height: int = Field(30, ge=20, le=60)
    color_count: Union[int, str] = "auto"
    difficulty: str = "medium"
    seed: Optional[int] = None
    preview_type: str = "puzzle"  # "puzzle" | "answer" | "source"

    @field_validator("color_count", mode="before")
    @classmethod
    def validate_color_count(cls, v):
        return _validate_color_count_val(v)


class ImageAnalysisResponse(BaseModel):
    image_quality: float = Field(..., ge=0, le=100)
    color_separation: float = Field(..., ge=0, le=100)
    contrast: float = Field(..., ge=0, le=100)
    mosaic_suitability: float = Field(..., ge=0, le=100)
    subject_clarity: float = Field(..., ge=0, le=100)
    recommended_color_count: int = 10
    recommendation: str = ""
    is_suitable: bool = True
    issues: list[str] = []


class ImageGenerateRequest(BaseModel):
    prompt: str = ""
    theme: str = "animals"
    subject: str = ""
    count: int = Field(1, ge=1, le=100)


class BulkGenerateRequest(BaseModel):
    theme: str = "animals"
    count: int = Field(10, ge=1, le=100)
    project_id: Optional[int] = None
