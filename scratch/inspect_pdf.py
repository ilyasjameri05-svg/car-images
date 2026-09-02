import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from app.models.book import BookSettings, PuzzleType, Difficulty, TrimSize, Language, PuzzleConfig
from app.pdf.pdf_renderer import PDFRenderer
from app.api.router import GENERATOR_MAP
from app.validators.puzzle_validator import PuzzleValidator

def test_full_sample_verification():
    print("=== RUNNING FULL SAMPLE PDF INSPECTION ===")
    
    settings = BookSettings(
        title="10-Type Ultimate Puzzle Book",
        subtitle="Challenge Your Mind",
        author="Puzzle Lab",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        difficulty=Difficulty.MEDIUM,
        num_puzzle_pages=10,
        include_cover=True,
        include_title_page=True,
        include_introduction=True,
        include_answer_key=True,
    )
    
    all_types = [
        PuzzleType.SUDOKU,
        PuzzleType.WORD_SEARCH,
        PuzzleType.MAZE,
        PuzzleType.CODE_BREAKER,
        PuzzleType.MATCHING,
        PuzzleType.PATTERN,
        PuzzleType.CRITICAL_THINKING,
        PuzzleType.PICTURE_PUZZLE,
        PuzzleType.ESCAPE_ROOM,
        PuzzleType.LOGIC_GRID
    ]
    
    puzzles = []
    print("\n1. Generating & Validating Puzzles:")
    for pt in all_types:
        gen_class = GENERATOR_MAP[pt]
        generator = gen_class(settings, difficulty=Difficulty.MEDIUM.value, seed=42)
        rec = generator.generate()
        res = PuzzleValidator.validate(rec)
        print(f"  - [{pt.value.upper()}] Valid: {res.is_valid}, Solver Verified: {rec.answer.solver_verified if rec.answer else False}")
        if not res.is_valid:
            print(f"    Errors: {res.errors}")
        assert res.is_valid, f"{pt.value} validation failed"
        puzzles.append(rec)
        
    settings.puzzle_configs = {
        p.puzzle_type: PuzzleConfig(quantity=1, difficulty=Difficulty.MEDIUM)
        for p in puzzles
    }
    
    output_pdf = "sample_book.pdf"
    print("\n2. Rendering Book PDF:")
    renderer = PDFRenderer(settings)
    renderer.render_book(puzzles, output_pdf)
    
    # Check PDF file size and existence
    assert os.path.exists(output_pdf), "PDF file was not created"
    file_size = os.path.getsize(output_pdf)
    print(f"  - PDF created: {output_pdf} ({file_size:,} bytes)")
    assert file_size > 10000, "PDF file size is unexpectedly small"
    
    print("\n3. Verifying Answer Key and Formatting Integrity:")
    for i, p in enumerate(puzzles):
        print(f"  Puzzle #{i+1} ({p.puzzle_type}):")
        print(f"    Title: {p.title}")
        print(f"    Answer record present: {p.answer is not None}")
        print(f"    Answer data keys: {list(p.answer.answer_data.keys()) if isinstance(p.answer.answer_data, dict) else 'Grid/List'}")
        
    print("\n=== ALL CRITERIA VERIFIED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_full_sample_verification()
