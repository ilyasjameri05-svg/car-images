"""
Pattern puzzle generator.

Selects pattern sequences from the PATTERN_SEQUENCES bank, filters by
difficulty, and packages them for display (typically 4–6 sequences per page).

puzzle_data keys:
  sequences — list of sequence dicts, each with:
    display   : list where None is replaced by "___"
    rule      : human-readable rule
    answers   : {blank_index: value}  (for answer key)
    type      : sequence type string
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.data.problem_banks import PATTERN_SEQUENCES

_INSTRUCTIONS: dict[str, str] = {
    "english": "Find the missing number(s) in each sequence. Write your answer in the blank(s).",
    "french":  "Trouvez le(s) numéro(s) manquant(s) dans chaque suite. Écrivez votre réponse.",
    "spanish": "Encuentra el/los número(s) que falta(n) en cada secuencia.",
    "arabic":  "ابحث عن الأرقام المفقودة في كل متتالية. اكتب إجابتك في الفراغ.",
}

# How many sequences to put on one puzzle page
_SEQUENCES_PER_PAGE: dict[str, int] = {
    "easy":   6,
    "medium": 5,
    "hard":   4,
}


class PatternGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty

        candidates = [s for s in PATTERN_SEQUENCES if s["difficulty"] == diff]
        if not candidates:
            candidates = list(PATTERN_SEQUENCES)

        count = _SEQUENCES_PER_PAGE.get(diff, 5)
        chosen = rng.sample(candidates, min(count, len(candidates)))

        sequences_out = []
        for seq in chosen:
            display = [
                "___" if item is None else item
                for item in seq["sequence"]
            ]
            answers = {}
            for bi, ans in zip(seq["blank_indices"], seq["answer"]):
                answers[bi] = ans

            sequences_out.append({
                "display":       display,
                "rule":          seq["rule"],
                "answers":       answers,
                "type":          seq["type"],
                "source_id":     seq["id"],
                "sequence":      seq["sequence"],
                "blank_indices": seq["blank_indices"],
            })

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="pattern",
            difficulty=diff,
            language=self.language,
            title=f"Pattern Puzzles #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "sequences": sequences_out,
                "count":     len(sequences_out),
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
