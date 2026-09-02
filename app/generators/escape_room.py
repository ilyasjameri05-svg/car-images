"""
Escape Room puzzle generator.

Selects a multi-step escape room puzzle from the curated ESCAPE_ROOM_PUZZLES
bank. Each puzzle has 3 chained steps, each with a clue, expected answer, and
hint. The final code is the solution.

puzzle_data keys:
  theme              — thematic setting string
  intro              — introductory paragraph
  steps              — list of step dicts (label, clue, answer, hint)
  final_code         — the final answer/code string
  final_instruction  — instruction for entering the final code
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.data.problem_banks import ESCAPE_ROOM_PUZZLES

_INSTRUCTIONS: dict[str, str] = {
    "english": "Solve each clue in order. The final code will unlock your escape!",
    "french":  "Résolvez chaque indice dans l'ordre. Le code final déverrouillera votre évasion!",
    "spanish": "Resuelve cada pista en orden. ¡El código final desbloqueará tu escape!",
    "arabic":  "حل كل دليل بالترتيب. سيفتح الرمز النهائي هروبك!",
}


class EscapeRoomGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed
        self._used_ids: set[str] = set()

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty

        candidates = [
            p for p in ESCAPE_ROOM_PUZZLES
            if p["difficulty"] == diff and p["id"] not in self._used_ids
        ]
        if not candidates:
            self._used_ids.clear()
            candidates = [p for p in ESCAPE_ROOM_PUZZLES if p["difficulty"] == diff]
        if not candidates:
            candidates = list(ESCAPE_ROOM_PUZZLES)

        puzzle = rng.choice(candidates)
        self._used_ids.add(puzzle["id"])

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="escape_room",
            difficulty=diff,
            language=self.language,
            title=f"Escape: {puzzle['theme']}",
            instructions=instructions,
            puzzle_data={
                "problem_id":        puzzle["id"],
                "theme":             puzzle["theme"],
                "intro":             puzzle["intro"],
                "steps":             puzzle["steps"],
                "final_code":        puzzle["final_code"],
                "final_instruction": puzzle["final_instruction"],
                "source_id":         puzzle["id"],
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
