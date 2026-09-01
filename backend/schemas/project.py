"""
Pydantic schemas for Book Project API requests/responses.
"""
from datetime import datetime
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


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1, max_length=255)
    subtitle: str = ""
    author: str = ""
    theme: str = "animals"
    difficulty: str = "medium"
    grid_size: int = Field(30, ge=20, le=60)
    color_count: Union[int, str] = Field("auto")
    page_size: str = "kdp_8_5x11"
    orientation: str = "portrait"
    answer_key_position: str = "at_end"
    decoration_mode: str = "off"
    decoration_theme: str = ""
    seed: Optional[int] = None
    settings_json: Optional[str] = "{}"

    @field_validator("color_count", mode="before")
    @classmethod
    def validate_color_count(cls, v):
        return _validate_color_count_val(v)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    theme: Optional[str] = None
    difficulty: Optional[str] = None
    grid_size: Optional[int] = None
    color_count: Optional[Union[int, str]] = None
    page_size: Optional[str] = None
    orientation: Optional[str] = None
    answer_key_position: Optional[str] = None
    decoration_mode: Optional[str] = None
    decoration_theme: Optional[str] = None
    seed: Optional[int] = None

    @field_validator("color_count", mode="before")
    @classmethod
    def validate_color_count(cls, v):
        if v is None:
            return None
        return _validate_color_count_val(v)


class ProjectResponse(BaseModel):
    id: int
    name: str
    subtitle: str
    author: str
    theme: str
    difficulty: str
    grid_size: int
    color_count: Union[int, str] = "auto"
    requested_color_count: Optional[Union[int, str]] = "auto"
    resolved_color_count: Optional[int] = None
    page_size: str
    orientation: str
    answer_key_position: str
    decoration_mode: str
    decoration_theme: str
    seed: Optional[int]
    page_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageCreate(BaseModel):
    page_number: int = Field(..., ge=1)
    page_type: str = "puzzle"
    title: str = ""
    puzzle_id: Optional[int] = None
    source_image_path: str = ""


class PageResponse(BaseModel):
    id: int
    project_id: int
    page_number: int
    page_type: str
    title: str
    puzzle_id: Optional[int]
    source_image_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class PageReorder(BaseModel):
    page_ids: list[int]
