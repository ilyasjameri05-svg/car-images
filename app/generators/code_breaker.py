"""
Code Breaker puzzle generator.

Cipher used: Caesar cipher (shift cipher).

A phrase is chosen from a curated bank, then each letter is shifted by a random
amount (1–25). Non-letter characters are kept unchanged.

puzzle_data keys:
  encoded  — the ciphertext string shown to the solver
  decoded  — the plaintext (stored for validation / answer key)
  shift    — integer 1–25 (stored for independent solver)
  hint     — a display hint shown on the puzzle page
  alphabet_table — list of 26 {"plain": X, "cipher": Y} mappings (shown on page)
"""
from __future__ import annotations

import random
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus

# Curated phrases by difficulty
_PHRASES: dict[str, list[str]] = {
    "easy": [
        "THE SUN IS BRIGHT",
        "CATS AND DOGS",
        "OPEN THE DOOR",
        "READ MORE BOOKS",
        "DRINK YOUR WATER",
        "HAVE A NICE DAY",
        "THE BIRD CAN FLY",
        "PLAY EVERY DAY",
    ],
    "medium": [
        "KNOWLEDGE IS POWER",
        "THE EARLY BIRD CATCHES THE WORM",
        "EVERY CLOUD HAS A SILVER LINING",
        "ACTIONS SPEAK LOUDER THAN WORDS",
        "WHERE THERE IS A WILL THERE IS A WAY",
        "ALL THAT GLITTERS IS NOT GOLD",
    ],
    "hard": [
        "THE GREATEST GLORY IN LIVING LIES NOT IN NEVER FALLING",
        "IN THE MIDDLE OF EVERY DIFFICULTY LIES OPPORTUNITY",
        "IMAGINATION IS MORE IMPORTANT THAN KNOWLEDGE",
        "THE ONLY WAY TO DO GREAT WORK IS TO LOVE WHAT YOU DO",
        "SUCCESS IS NOT FINAL FAILURE IS NOT FATAL",
    ],
}

_INSTRUCTIONS: dict[str, str] = {
    "english": (
        "Each letter in the message has been shifted by the same secret number. "
        "Use the alphabet table to decode the message and write the original words."
    ),
    "french": (
        "Chaque lettre du message a été décalée du même nombre secret. "
        "Utilisez le tableau de l'alphabet pour décoder le message."
    ),
    "spanish": (
        "Cada letra del mensaje ha sido desplazada el mismo número secreto. "
        "Use la tabla del alfabeto para decodificar el mensaje."
    ),
    "arabic": (
        "تم إزاحة كل حرف في الرسالة بنفس الرقم السري. "
        "استخدم جدول الأبجدية لفك تشفير الرسالة."
    ),
}


def _caesar_encode(text: str, shift: int) -> str:
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


class CodeBreakerGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty
        phrases = _PHRASES.get(diff, _PHRASES["medium"])
        phrase = rng.choice(phrases)
        shift = rng.randint(1, 25)
        encoded = _caesar_encode(phrase, shift)

        # Build alphabet table (26 rows)
        alphabet_table = [
            {"plain": chr(ord('A') + i), "cipher": chr((ord('A') + i + shift - ord('A')) % 26 + ord('A'))}
            for i in range(26)
        ]

        # Reveal 6 letters as hints (more for easy)
        reveal_count = {"easy": 8, "medium": 5, "hard": 3}.get(diff, 5)
        revealed = rng.sample(range(26), reveal_count)

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="code_breaker",
            difficulty=diff,
            language=self.language,
            title=f"Code Breaker #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "encoded":    encoded,
                "decoded":    phrase,
                "shift":      shift,
                "alphabet_table": alphabet_table,
                "revealed_indices": sorted(revealed),
                "hint":       f"Hint: The letter A becomes {chr((shift) % 26 + ord('A'))}",
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )
