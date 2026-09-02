"""
Critical Thinking puzzle generator.

Randomly selects a problem from the curated CRITICAL_THINKING_PROBLEMS bank,
filtered by difficulty. Each problem has a stored, verified answer.

puzzle_data keys:
  problem_id   — bank ID
  question     — full question text
  answer       — correct answer string (used for answer key)
  explanation  — how to reach the answer
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.data.problem_banks import CRITICAL_THINKING_PROBLEMS

_INSTRUCTIONS: dict[str, str] = {
    "english": "Read the question carefully and write your answer in the space provided.",
    "french":  "Lisez attentivement la question et écrivez votre réponse dans l'espace prévu.",
    "spanish": "Lee la pregunta con atención y escribe tu respuesta en el espacio proporcionado.",
    "arabic":  "اقرأ السؤال بعناية واكتب إجابتك في المساحة المخصصة.",
}


class CriticalThinkingGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed
        # Track used IDs per generator instance to avoid repeating
        self._used_ids: set[str] = set()

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty

        candidates = [
            p for p in CRITICAL_THINKING_PROBLEMS
            if p["difficulty"] == diff and p["id"] not in self._used_ids
        ]
        if not candidates:
            # Reset if all have been used
            self._used_ids.clear()
            candidates = [p for p in CRITICAL_THINKING_PROBLEMS if p["difficulty"] == diff]
        if not candidates:
            candidates = list(CRITICAL_THINKING_PROBLEMS)

        problem = rng.choice(candidates)
        self._used_ids.add(problem["id"])

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="critical_thinking",
            difficulty=diff,
            language=self.language,
            title=f"Think It Through #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "problem_id":  problem["id"],
                "question":    problem["question"],
                "answer":      problem["answer"],
                "explanation": problem["explanation"],
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
