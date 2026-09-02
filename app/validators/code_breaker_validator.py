"""
Code Breaker Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator

def _caesar_encode(text: str, shift: int) -> str:
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)

def _caesar_decode(text: str, shift: int) -> str:
    return _caesar_encode(text, -shift)

class CodeBreakerValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        for key in ("encoded", "decoded", "shift", "alphabet_table"):
            if key not in d:
                errors.append(f"Missing key: '{key}'")
        
        if errors:
            return self._fail(record, errors, warnings)

        encoded = d["encoded"]
        shift = d["shift"]
        stored_decoded = d["decoded"]

        # 1. Independently decode the text
        derived_decoded = _caesar_decode(encoded, shift)

        # 2. Verify re-encoding matches exactly
        if _caesar_encode(derived_decoded, shift).upper() != encoded.upper():
            errors.append("Re-encoding derived text does not match the encoded puzzle.")

        # 3. Verify alphabet table matches shift
        alphabet_table = d["alphabet_table"]
        for entry in alphabet_table:
            orig = entry["plain"]
            mapped = entry["cipher"]
            if _caesar_encode(orig, shift).upper() != mapped.upper():
                errors.append(f"Alphabet mapping for '{orig}' -> '{mapped}' does not match shift {shift}.")

        if derived_decoded.upper() != stored_decoded.upper():
            errors.append(f"Generator's stored decoded text does NOT match independently derived decoded text.")
            
        if errors:
            return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={"decoded": derived_decoded, "shift": shift},
            solver_verified=True,
            notes="Independently decoded and re-encoded to confirm correctness.",
        )
        record.answer = answer
        record.validation_status = ValidationStatus.VALID

        return ValidationResult(
            puzzle_id=puzzle_id,
            is_valid=True,
            errors=[],
            warnings=warnings,
            solution_count=1,
            solver_verified=True,
        )

    def _fail(
        self,
        record: PuzzleRecord,
        errors: list[str],
        warnings: list[str],
    ) -> ValidationResult:
        record.validation_status = ValidationStatus.INVALID
        record.answer = None
        return ValidationResult(
            puzzle_id=record.puzzle_id,
            is_valid=False,
            errors=errors,
            warnings=warnings,
            solution_count=0,
            solver_verified=False,
        )
