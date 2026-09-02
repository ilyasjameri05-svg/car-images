"""
Tests for PDF generation:
- PDF is created
- File size is non-trivial
- Page dimensions are correct
- Project save/load round-trip
"""
import os
import struct
import tempfile
import pytest

from app.models.book import BookSettings, Difficulty, Language, PuzzleType, TrimSize
from app.models.puzzle import PuzzleRecord, ValidationStatus
from app.models.layout import POINTS_PER_INCH
from app.generators.sudoku import SudokuGenerator
from app.validators.sudoku_validator import SudokuValidator
from app.pdf.pdf_renderer import PDFRenderer
from app.exports.project_io import ProjectIO


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_settings(**kwargs) -> BookSettings:
    defaults = dict(
        title="PDF Test Book",
        subtitle="Test",
        author="Tester",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        puzzle_types=[PuzzleType.SUDOKU],
        difficulty=Difficulty.MEDIUM,
        num_puzzle_pages=3,
        include_cover=True,
        include_title_page=True,
        include_introduction=True,
        include_answer_key=True,
    )
    defaults.update(kwargs)
    return BookSettings(**defaults)


def _generate_validated_puzzles(settings: BookSettings, count: int) -> list:
    gen = SudokuGenerator(settings, difficulty="medium", seed=0)
    validator = SudokuValidator()
    puzzles = []
    for seed in range(count * 3):
        gen._seed = seed
        record = gen.generate()
        result = validator.validate(record)
        if result.is_valid:
            puzzles.append(record)
        if len(puzzles) >= count:
            break
    return puzzles


def _read_pdf_page_size(path: str) -> tuple[float, float] | None:
    """
    Extract the MediaBox from the first page of a PDF.
    Returns (width_pt, height_pt) or None if not found.
    """
    with open(path, "rb") as f:
        content = f.read()
    import re
    # Find MediaBox: /MediaBox [0 0 width height]
    pattern = rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]"
    match = re.search(pattern, content)
    if match:
        w = float(match.group(3)) - float(match.group(1))
        h = float(match.group(4)) - float(match.group(2))
        return w, h
    return None


# ---------------------------------------------------------------------------
# PDF generation tests
# ---------------------------------------------------------------------------

class TestPDFGeneration:

    def test_pdf_is_created(self):
        settings = _make_settings()
        puzzles = _generate_validated_puzzles(settings, 3)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            assert os.path.exists(path)
        finally:
            os.unlink(path)

    def test_pdf_file_size_nontrivial(self):
        settings = _make_settings()
        puzzles = _generate_validated_puzzles(settings, 3)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            size = os.path.getsize(path)
            assert size > 10_000, f"PDF seems too small ({size} bytes) — may be empty"
        finally:
            os.unlink(path)

    def test_pdf_starts_with_pdf_header(self):
        settings = _make_settings()
        puzzles = _generate_validated_puzzles(settings, 2)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            with open(path, "rb") as f:
                header = f.read(4)
            assert header == b"%PDF", f"File does not start with %PDF: {header!r}"
        finally:
            os.unlink(path)

    def test_pdf_6x9_page_dimensions(self):
        settings = _make_settings(trim_size=TrimSize.SIX_BY_NINE)
        puzzles = _generate_validated_puzzles(settings, 2)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            result = _read_pdf_page_size(path)
            assert result is not None, "Could not read MediaBox from PDF"
            w_pt, h_pt = result
            assert abs(w_pt - 6.0 * POINTS_PER_INCH) < 2.0, f"Width mismatch: {w_pt:.2f}pt"
            assert abs(h_pt - 9.0 * POINTS_PER_INCH) < 2.0, f"Height mismatch: {h_pt:.2f}pt"
        finally:
            os.unlink(path)

    def test_pdf_8_5x11_page_dimensions(self):
        settings = _make_settings(trim_size=TrimSize.EIGHT_HALF_BY_ELEVEN)
        puzzles = _generate_validated_puzzles(settings, 2)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            result = _read_pdf_page_size(path)
            assert result is not None
            w_pt, h_pt = result
            assert abs(w_pt - 8.5 * POINTS_PER_INCH) < 2.0
            assert abs(h_pt - 11.0 * POINTS_PER_INCH) < 2.0
        finally:
            os.unlink(path)

    def test_pdf_8x10_page_dimensions(self):
        settings = _make_settings(trim_size=TrimSize.EIGHT_BY_TEN)
        puzzles = _generate_validated_puzzles(settings, 2)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            result = _read_pdf_page_size(path)
            assert result is not None
            w_pt, h_pt = result
            assert abs(w_pt - 8.0 * POINTS_PER_INCH) < 2.0
            assert abs(h_pt - 10.0 * POINTS_PER_INCH) < 2.0
        finally:
            os.unlink(path)

    def test_pdf_without_cover_is_created(self):
        settings = _make_settings(
            include_cover=False,
            include_title_page=False,
            include_introduction=False,
            include_answer_key=True,
        )
        puzzles = _generate_validated_puzzles(settings, 2)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path = f.name
        try:
            renderer = PDFRenderer(settings)
            renderer.render_book(puzzles, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 5000
        finally:
            os.unlink(path)

    def test_pdf_answer_key_included(self):
        """
        Verify that enabling the answer key produces a larger PDF than disabling it.
        We cannot grep for 'Answer Key' directly because ReportLab compresses page
        content streams. Instead we compare file sizes.
        """
        puzzles_with = _generate_validated_puzzles(_make_settings(include_answer_key=True), 3)
        puzzles_without = _generate_validated_puzzles(_make_settings(include_answer_key=False), 3)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path_with = f.name
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            path_without = f.name

        try:
            PDFRenderer(_make_settings(include_answer_key=True)).render_book(puzzles_with, path_with)
            PDFRenderer(_make_settings(include_answer_key=False)).render_book(puzzles_without, path_without)

            size_with = os.path.getsize(path_with)
            size_without = os.path.getsize(path_without)
            assert size_with > size_without, (
                f"PDF with answer key ({size_with}B) should be larger than "
                f"PDF without ({size_without}B)"
            )
        finally:
            os.unlink(path_with)
            os.unlink(path_without)


# ---------------------------------------------------------------------------
# Project IO tests
# ---------------------------------------------------------------------------

class TestProjectIO:

    def test_save_and_load_round_trip(self):
        settings = _make_settings()
        puzzles = _generate_validated_puzzles(settings, 2)
        project = ProjectIO.create_project(settings, puzzles)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name

        try:
            ProjectIO.save(project, path)
            assert os.path.exists(path)

            loaded = ProjectIO.load(path)
            assert loaded.settings.title == settings.title
            assert loaded.settings.trim_size == settings.trim_size
            assert len(loaded.puzzles) == len(puzzles)
        finally:
            os.unlink(path)

    def test_loaded_puzzles_have_answers(self):
        settings = _make_settings()
        puzzles = _generate_validated_puzzles(settings, 2)
        project = ProjectIO.create_project(settings, puzzles)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            ProjectIO.save(project, path)
            loaded = ProjectIO.load(path)
            for p in loaded.puzzles:
                assert p.answer is not None
                assert p.answer.solver_verified
        finally:
            os.unlink(path)

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            ProjectIO.load("/nonexistent/path/project.json")

    def test_version_mismatch_raises(self):
        import json, tempfile
        data = {"version": "99.0", "project_id": "x", "settings": {}, "puzzles": [],
                "created_at": "2024-01-01T00:00:00+00:00",
                "updated_at": "2024-01-01T00:00:00+00:00"}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump(data, f)
            path = f.name
        try:
            with pytest.raises(ValueError, match="version"):
                ProjectIO.load(path)
        finally:
            os.unlink(path)
