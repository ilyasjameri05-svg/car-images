import json
import os
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord

class ProjectState(BaseModel):
    settings: BookSettings
    puzzles: List[PuzzleRecord]
    last_saved: Optional[str] = None

class ProjectManager:
    def __init__(self):
        self.settings = BookSettings(title="New Puzzle Book", author="Author")
        self.puzzles: List[PuzzleRecord] = []
        self.filepath: Optional[str] = None

    def new_project(self, settings: BookSettings):
        self.settings = settings
        self.puzzles = []
        self.filepath = None

    def load_project(self, filepath: str) -> bool:
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            state = ProjectState.model_validate(data)
            self.settings = state.settings
            self.puzzles = state.puzzles
            self.filepath = filepath
            return True

    def save_project(self, filepath: Optional[str] = None) -> str:
        path_to_save = filepath or self.filepath
        if not path_to_save:
            path_to_save = f"{self.settings.title.replace(' ', '_').lower()}_project.json"
        
        state = ProjectState(
            settings=self.settings,
            puzzles=self.puzzles,
            last_saved=datetime.utcnow().isoformat()
        )
        
        with open(path_to_save, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2))
            
        self.filepath = path_to_save
        return path_to_save

    def get_puzzle(self, puzzle_id: str) -> Optional[PuzzleRecord]:
        for p in self.puzzles:
            if p.puzzle_id == puzzle_id:
                return p
        return None

    def update_puzzle(self, puzzle: PuzzleRecord):
        for i, p in enumerate(self.puzzles):
            if p.puzzle_id == puzzle.puzzle_id:
                self.puzzles[i] = puzzle
                break

    def get_state(self) -> dict:
        return {
            "settings": self.settings.model_dump(),
            "puzzles": [p.model_dump() for p in self.puzzles],
            "filepath": self.filepath,
            "puzzle_count": len(self.puzzles),
            "valid_count": sum(1 for p in self.puzzles if p.validation_status.value == "valid")
        }

# Global singleton for the active project
active_project = ProjectManager()
