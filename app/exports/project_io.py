"""
Project save / load utilities.

A project file is a JSON document containing:
- version: schema version string
- settings: serialized BookSettings
- puzzles: list of serialized PuzzleRecords (including answers)

The project file is the single artefact that allows a book to be reproduced
exactly (given the same settings and stored puzzle_data).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, AnswerRecord, ValidationStatus

_SCHEMA_VERSION = "1.0"


class ProjectFile:
    """In-memory representation of a saved project."""

    def __init__(
        self,
        project_id: str,
        settings: BookSettings,
        puzzles: List[PuzzleRecord],
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.project_id = project_id
        self.settings = settings
        self.puzzles = puzzles
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "version": _SCHEMA_VERSION,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "settings": self.settings.model_dump(),
            "puzzles": [_puzzle_to_dict(p) for p in self.puzzles],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectFile":
        _check_version(data.get("version", "unknown"))
        settings = BookSettings(**data["settings"])
        puzzles = [_puzzle_from_dict(p) for p in data.get("puzzles", [])]
        return cls(
            project_id=data["project_id"],
            settings=settings,
            puzzles=puzzles,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


class ProjectIO:
    """Static helpers for creating, saving, and loading projects."""

    @staticmethod
    def create_project(
        settings: BookSettings,
        puzzles: List[PuzzleRecord],
    ) -> ProjectFile:
        return ProjectFile(
            project_id=str(uuid.uuid4()),
            settings=settings,
            puzzles=puzzles,
        )

    @staticmethod
    def save(project: ProjectFile, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(path: str) -> ProjectFile:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Project file not found: {path}")
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return ProjectFile.from_dict(data)


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _puzzle_to_dict(p: PuzzleRecord) -> dict:
    d = p.model_dump()
    # Ensure datetime fields are ISO strings
    d["generated_at"] = p.generated_at.isoformat()
    if p.answer:
        d["answer"]["generated_at"] = p.answer.generated_at.isoformat()
    return d


def _puzzle_from_dict(data: dict) -> PuzzleRecord:
    answer_data = data.pop("answer", None)
    record = PuzzleRecord(**data)
    if answer_data:
        record.answer = AnswerRecord(**answer_data)
    return record


def _check_version(version: str) -> None:
    if version != _SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported project file version: {version!r}. "
            f"Expected: {_SCHEMA_VERSION!r}."
        )
