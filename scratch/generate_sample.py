import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath('.'))

from app.models.book import BookSettings, PuzzleType, Difficulty, TrimSize, Language, PuzzleConfig
from app.pdf.pdf_renderer import PDFRenderer
from app.api.router import GENERATOR_MAP
from app.validators.puzzle_validator import PuzzleValidator

def generate_sample():
    print("Generating 10-type sample PDF...")
    
    settings = BookSettings(
        title="10-Type Puzzle Challenge",
        author="Puzzle Master",
        language=Language.ENGLISH,
        trim_size=TrimSize.SIX_BY_NINE,
        difficulty=Difficulty.MEDIUM,
        puzzle_types=[], # Filled dynamically
        num_puzzle_pages=1,
        include_cover=True,
        include_title_page=True,
        include_introduction=True,
        include_answer_key=True,
    )
    
    puzzles = []
    types_to_generate = [
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
    
    for pt in types_to_generate:
        print(f"Generating 1 {pt.value} puzzle...")
        gen_class = GENERATOR_MAP.get(pt)
        if not gen_class:
            print(f"No generator for {pt.value}, skipping.")
            continue
            
        generator = gen_class(settings, difficulty=Difficulty.MEDIUM.value)
        
        valid_rec = None
        for i in range(10):
            rec = generator.generate()
            res = PuzzleValidator.validate(rec)
            if res.is_valid:
                valid_rec = rec
                break
        
        if valid_rec:
            puzzles.append(valid_rec)
        else:
            print(f"Failed to generate valid {pt.value} puzzle!")

    settings.puzzle_configs = {
        p.puzzle_type: PuzzleConfig(quantity=1, difficulty=Difficulty.MEDIUM)
        for p in puzzles
    }
    
    print(f"Rendering PDF with {len(puzzles)} puzzles...")
    output_path = "sample_book.pdf"
    renderer = PDFRenderer(settings)
    renderer.render_book(puzzles, output_path)
    print(f"Done! PDF saved to {output_path}")

if __name__ == "__main__":
    generate_sample()
