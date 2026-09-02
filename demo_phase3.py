"""
Demo script for Phase 3 puzzle types.
Generates puzzles, validates them, and produces a PDF.
"""

from app.models.book import BookSettings, Difficulty, PuzzleType
from app.models.puzzle import PuzzleRecord
from app.generators.word_search import WordSearchGenerator
from app.generators.maze import MazeGenerator
from app.generators.logic_grid import LogicGridGenerator
from app.generators.code_breaker import CodeBreakerGenerator
from app.generators.matching import MatchingGenerator
from app.generators.pattern import PatternGenerator
from app.generators.critical_thinking import CriticalThinkingGenerator
from app.generators.picture_puzzle import PicturePuzzleGenerator
from app.generators.escape_room import EscapeRoomGenerator
from app.validators.puzzle_validator import PuzzleValidator
from app.pdf.pdf_renderer import PDFRenderer

import os

def main():
    settings = BookSettings(
        title="Phase 3 Demo Book",
        author="KDP AI Assistant",
        difficulty=Difficulty.MEDIUM,
        puzzle_types=[
            PuzzleType.WORD_SEARCH,
            PuzzleType.MAZE,
            PuzzleType.CODE_BREAKER,
            PuzzleType.MATCHING,
            PuzzleType.PATTERN,
            PuzzleType.CRITICAL_THINKING,
            PuzzleType.PICTURE_PUZZLE,
            PuzzleType.ESCAPE_ROOM,
            PuzzleType.LOGIC_GRID,
        ],
        include_cover=True,
        include_title_page=True,
        include_introduction=True,
        include_answer_key=True,
        page_numbering=True,
    )

    generators = [
        WordSearchGenerator(settings),
        MazeGenerator(settings),
        CodeBreakerGenerator(settings),
        MatchingGenerator(settings),
        PatternGenerator(settings),
        CriticalThinkingGenerator(settings),
        PicturePuzzleGenerator(settings),
        EscapeRoomGenerator(settings),
        LogicGridGenerator(settings),
    ]

    puzzles: list[PuzzleRecord] = []
    
    print("Generating and validating Phase 3 puzzles...\n")
    
    for gen in generators:
        # Generate the puzzle
        rec = gen.generate()
        
        # Validate the puzzle
        result = PuzzleValidator.validate(rec)
        
        print(f"Puzzle Type: {rec.puzzle_type.upper()}")
        print(f"  Title: {rec.title}")
        print(f"  Valid: {result.is_valid}")
        if not result.is_valid:
            print(f"  Errors: {result.errors}")
        print()
        
        puzzles.append(rec)

    # Render the PDF
    output_filename = "phase3_demo.pdf"
    output_path = os.path.abspath(output_filename)
    
    print("Rendering PDF...")
    renderer = PDFRenderer(settings)
    renderer.render_book(puzzles, output_path)
    
    print(f"\nPDF successfully generated at:")
    print(output_path)

if __name__ == "__main__":
    main()
