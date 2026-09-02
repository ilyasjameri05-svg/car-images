"""
Core data models for BookSettings and related configuration.

BookSettings is the central object passed to every component of the pipeline.
It controls page dimensions, puzzle selection, layout, and export options.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Language(str, Enum):
    ENGLISH = "english"
    FRENCH = "french"
    SPANISH = "spanish"
    ARABIC = "arabic"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class PuzzleType(str, Enum):
    SUDOKU = "sudoku"
    WORD_SEARCH = "word_search"
    MAZE = "maze"
    LOGIC_GRID = "logic_grid"
    CODE_BREAKER = "code_breaker"
    MATCHING = "matching"
    PATTERN = "pattern"
    CRITICAL_THINKING = "critical_thinking"
    PICTURE_PUZZLE = "picture_puzzle"
    ESCAPE_ROOM = "escape_room"


class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class ColorMode(str, Enum):
    BLACK_AND_WHITE = "black_and_white"
    COLOR = "color"


class AnswerKeyPlacement(str, Enum):
    BACK = "back"            # All answers at the end of the book
    AFTER_EACH = "after_each"  # Answer immediately after each puzzle
    SEPARATE = "separate"    # Separate answer-key section


class TrimSize(str, Enum):
    """Standard KDP trim sizes."""
    SIX_BY_NINE = "6x9"
    EIGHT_BY_TEN = "8x10"
    EIGHT_HALF_BY_ELEVEN = "8.5x11"
    EIGHT_HALF_BY_EIGHT_HALF = "8.5x8.5"
    FIVE_BY_EIGHT = "5x8"
    FIVE_HALF_BY_EIGHT_HALF = "5.5x8.5"
    SEVEN_BY_TEN = "7x10"
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# Puzzle Configuration
# ---------------------------------------------------------------------------

class PuzzleConfig(BaseModel):
    """Configuration for a specific puzzle type."""
    quantity: int = Field(default=0, ge=0)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)


# ---------------------------------------------------------------------------
# BookSettings model
# ---------------------------------------------------------------------------

class BookSettings(BaseModel):
    """
    All user-configurable settings for a puzzle book.

    This object is the single source of truth passed to every stage of the
    pipeline: generator, layout engine, PDF renderer, and preflight checker.
    """

    # Metadata
    title: str = Field(default="My Puzzle Book", min_length=1, max_length=200)
    subtitle: str = Field(default="", max_length=300)
    author: str = Field(default="Unknown Author", min_length=1, max_length=200)
    language: Language = Field(default=Language.ENGLISH)
    grade_range: str = Field(default="Adults", max_length=100)

    # Page configuration
    trim_size: TrimSize = Field(default=TrimSize.SIX_BY_NINE)
    custom_width_in: Optional[float] = Field(default=None, gt=0, le=24)
    custom_height_in: Optional[float] = Field(default=None, gt=0, le=24)
    orientation: Orientation = Field(default=Orientation.PORTRAIT)
    bleed: bool = Field(default=False)
    bleed_amount_in: float = Field(default=0.125, ge=0, le=0.5)  # inches
    color_mode: ColorMode = Field(default=ColorMode.BLACK_AND_WHITE)

    # Content
    theme: str = Field(default="Classic", max_length=100)
    puzzle_configs: Dict[str, PuzzleConfig] = Field(
        default_factory=lambda: {PuzzleType.SUDOKU.value: PuzzleConfig(quantity=1, difficulty=Difficulty.MEDIUM)}
    )

    # Page counts
    num_puzzle_pages: int = Field(default=10, ge=1, le=500)
    num_answer_pages: int = Field(default=1, ge=0, le=50)

    # Book structure toggles
    include_cover: bool = Field(default=True)
    include_title_page: bool = Field(default=True)
    include_introduction: bool = Field(default=True)
    include_answer_key: bool = Field(default=True)

    # Typography
    font_family: str = Field(default="Helvetica")
    margin_top_in: float = Field(default=0.75, ge=0.25, le=3.0)
    margin_bottom_in: float = Field(default=0.75, ge=0.25, le=3.0)
    margin_inner_in: float = Field(default=0.875, ge=0.25, le=3.0)  # gutter
    margin_outer_in: float = Field(default=0.625, ge=0.25, le=3.0)

    # Navigation / structure
    page_numbering: bool = Field(default=True)
    answer_key_placement: AnswerKeyPlacement = Field(
        default=AnswerKeyPlacement.BACK
    )

    @field_validator("puzzle_configs")
    @classmethod
    def at_least_one_puzzle_configured(cls, v: Dict[str, PuzzleConfig]) -> Dict[str, PuzzleConfig]:
        if not any(config.quantity > 0 for config in v.values()):
            raise ValueError("At least one puzzle type must have a quantity > 0.")
        return v

    @model_validator(mode="after")
    def custom_size_requires_dimensions(self) -> "BookSettings":
        if self.trim_size == TrimSize.CUSTOM:
            if self.custom_width_in is None or self.custom_height_in is None:
                raise ValueError(
                    "custom_width_in and custom_height_in are required when "
                    "trim_size is CUSTOM."
                )
        return self

    @property
    def is_rtl(self) -> bool:
        """True if the selected language uses right-to-left text direction."""
        return self.language == Language.ARABIC

    def effective_width_in(self) -> float:
        """Logical width in inches (before orientation swap)."""
        _sizes = {
            TrimSize.SIX_BY_NINE: 6.0,
            TrimSize.EIGHT_BY_TEN: 8.0,
            TrimSize.EIGHT_HALF_BY_ELEVEN: 8.5,
            TrimSize.EIGHT_HALF_BY_EIGHT_HALF: 8.5,
            TrimSize.FIVE_BY_EIGHT: 5.0,
            TrimSize.FIVE_HALF_BY_EIGHT_HALF: 5.5,
            TrimSize.SEVEN_BY_TEN: 7.0,
            TrimSize.CUSTOM: self.custom_width_in,
        }
        return _sizes[self.trim_size]

    def effective_height_in(self) -> float:
        """Logical height in inches (before orientation swap)."""
        _sizes = {
            TrimSize.SIX_BY_NINE: 9.0,
            TrimSize.EIGHT_BY_TEN: 10.0,
            TrimSize.EIGHT_HALF_BY_ELEVEN: 11.0,
            TrimSize.EIGHT_HALF_BY_EIGHT_HALF: 8.5,
            TrimSize.FIVE_BY_EIGHT: 8.0,
            TrimSize.FIVE_HALF_BY_EIGHT_HALF: 8.5,
            TrimSize.SEVEN_BY_TEN: 10.0,
            TrimSize.CUSTOM: self.custom_height_in,
        }
        return _sizes[self.trim_size]
