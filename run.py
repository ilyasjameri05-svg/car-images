"""
KDP Puzzle Book Generator
Entry point for generating sample books and running the pipeline.
"""
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.book import BookSettings, Language, Difficulty, PuzzleType, TrimSize
from app.models.puzzle import PuzzleRecord
from app.layouts.dimensions import get_page_dimensions
from app.generators.sudoku import SudokuGenerator
from app.validators.sudoku_validator import SudokuValidator
from app.exports.project_io import ProjectIO
from app.pdf.pdf_renderer import PDFRenderer


def generate_sample_book(output_path: str = "sample_sudoku_book.pdf") -> str:
    """Generate a sample Sudoku book for testing."""
    print("=== KDP Puzzle Book Generator ===")
    print("Generating sample Sudoku book...")

    # --- Book settings ---
    settings = BookSettings(
        title="Brain Boost Sudoku",
        subtitle="50 Challenging Puzzles for Sharp Minds",
        author="Puzzle Master",
        language=Language.ENGLISH,
        grade_range="Adults / Ages 12+",
        trim_size=TrimSize.SIX_BY_NINE,
        orientation="portrait",
        bleed=False,
        color_mode="black_and_white",
        difficulty=Difficulty.MEDIUM,
        theme="Classic",
        puzzle_types=[PuzzleType.SUDOKU],
        num_puzzle_pages=5,
        num_answer_pages=1,
        include_cover=True,
        include_title_page=True,
        include_introduction=True,
        include_answer_key=True,
        page_numbering=True,
        answer_key_placement="back",
    )

    dims = get_page_dimensions(settings)
    print(f"Page dimensions: {dims.width_in:.2f}\" × {dims.height_in:.2f}\"")

    # --- Generate puzzles ---
    generator = SudokuGenerator(settings)
    validator = SudokuValidator()

    puzzles: list[PuzzleRecord] = []
    max_attempts = 20

    for i in range(settings.num_puzzle_pages):
        for attempt in range(max_attempts):
            record = generator.generate()
            result = validator.validate(record)
            if result.is_valid:
                puzzles.append(record)
                print(f"  Puzzle {i+1}: Generated & validated (ID={record.puzzle_id[:8]})")
                break
            else:
                print(f"  Puzzle {i+1}: Validation failed ({result.errors}), retrying...")
        else:
            raise RuntimeError(f"Could not generate a valid puzzle after {max_attempts} attempts")

    # --- Save project ---
    project = ProjectIO.create_project(settings, puzzles)
    project_path = output_path.replace(".pdf", ".json")
    ProjectIO.save(project, project_path)
    print(f"Project saved: {project_path}")

    # --- Render PDF ---
    renderer = PDFRenderer(settings)
    renderer.render_book(puzzles, output_path)
    print(f"PDF exported: {output_path}")
    print("=== Done ===")
    return output_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sample_sudoku_book.pdf"
    generate_sample_book(out)
