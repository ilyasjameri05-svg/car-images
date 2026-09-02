"""
Matching puzzle generator.

Picks a set of pairs from the curated MATCHING_SETS bank,
shuffles the right-hand column, and stores both the shuffled version
(shown to the solver) and the correct mapping (stored for answer key).

puzzle_data keys:
  left_items   — ordered list shown on the left column
  right_items  — shuffled list shown on the right column
  correct_map  — dict {left_index: right_index} for answer key
  category     — descriptive name shown as heading
  instruction  — text shown on the puzzle page
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.data.problem_banks import MATCHING_SETS

_INSTRUCTIONS: dict[str, str] = {
    "english": "Draw a line from each item on the left to the correct item on the right.",
    "french":  "Tracez une ligne de chaque élément à gauche vers l'élément correct à droite.",
    "spanish": "Traza una línea desde cada elemento de la izquierda al elemento correcto de la derecha.",
    "arabic":  "ارسم خطاً من كل عنصر على اليسار إلى العنصر الصحيح على اليمين.",
}


class MatchingGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty

        # Filter matching sets by difficulty; fall back if no exact match
        candidates = [s for s in MATCHING_SETS if s["difficulty"] == diff]
        if not candidates:
            candidates = MATCHING_SETS

        chosen = rng.choice(candidates)
        pairs = list(chosen["pairs"])

        left_items  = [p[0] for p in pairs]
        right_items = [p[1] for p in pairs]

        # Shuffle right column
        shuffled_right = list(right_items)
        rng.shuffle(shuffled_right)

        # Build correct mapping: left_index → index in shuffled_right
        correct_map = {}
        for li, left in enumerate(left_items):
            original_right = pairs[li][1]
            ri = shuffled_right.index(original_right)
            correct_map[str(li)] = ri

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])
        puzzle_inst = chosen.get("instruction", instructions)

        return PuzzleRecord(
            puzzle_type="matching",
            difficulty=diff,
            language=self.language,
            title=f"Matching: {chosen['category']}",
            instructions=f"{puzzle_inst}\n{instructions}",
            puzzle_data={
                "left_items":      left_items,
                "right_items":     shuffled_right,
                "correct_map":     correct_map,
                "category":        chosen["category"],
                "source_id":       chosen["id"],
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
