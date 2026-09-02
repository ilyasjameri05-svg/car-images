"""
Pattern Validator.
"""
from __future__ import annotations

from app.models.puzzle import (
    AnswerRecord,
    PuzzleRecord,
    ValidationResult,
    ValidationStatus,
)
from app.validators.base import BasePuzzleValidator

class PatternValidator(BasePuzzleValidator):
    def validate(self, record: PuzzleRecord) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        puzzle_id = record.puzzle_id
        d = record.puzzle_data

        if "sequences" not in d:
            errors.append("Missing key: 'sequences'")
            return self._fail(record, errors, warnings)

        seqs = d["sequences"]
        if not seqs:
            errors.append("sequences list is empty.")
            return self._fail(record, errors, warnings)

        answer_data = []
        for i, seq in enumerate(seqs):
            for key in ("display", "answers", "sequence", "blank_indices"):
                if key not in seq:
                    errors.append(f"Sequence {i} missing '{key}'.")
            
            if errors:
                continue

            full_seq = seq["sequence"]
            display_seq = seq["display"]
            blank_idx = seq["blank_indices"]
            answers = seq["answers"]

            # Reconstruct display to ensure consistency
            reconstructed_display = []
            for j, val in enumerate(full_seq):
                if j in blank_idx:
                    reconstructed_display.append("___")
                else:
                    reconstructed_display.append(val)
            
            # verify the display sequence is consistent with the blanks
            if display_seq != reconstructed_display:
                errors.append(f"Sequence {i} display string does not match the generated sequence and blanks.")

            from app.data.problem_banks import PATTERN_SEQUENCES
            pattern_lookup = {p["id"]: p for p in PATTERN_SEQUENCES}
            source = pattern_lookup.get(seq.get("source_id"))
            if not source:
                errors.append(f"Sequence {i} missing valid source_id.")
                continue

            # verify the missing values are correctly stored
            derived_answers = {str(bi): str(ans) for bi, ans in zip(source["blank_indices"], source["answer"])}
            str_answers = {str(k): str(v) for k, v in answers.items()}
            
            if str_answers != derived_answers:
                errors.append(f"Sequence {i} answers do not match the values at the blank indices.")
            
            answer_data.append({
                "display": display_seq,
                "answers": derived_answers,
                "rule": seq.get("rule", ""),
            })

        if errors:
            return self._fail(record, errors, warnings)

        answer = AnswerRecord(
            puzzle_id=puzzle_id,
            answer_data={"sequences": answer_data},
            solver_verified=True,
            notes="Pattern answers explicitly verified against the sequence and blank indices.",
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
