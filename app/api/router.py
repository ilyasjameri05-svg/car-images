import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.book import BookSettings, PuzzleType, Difficulty, PuzzleConfig
from app.services.project_manager import active_project
from app.validators.puzzle_validator import PuzzleValidator
from app.pdf.pdf_renderer import PDFRenderer

# Generators (need dynamic loading based on type)
from app.generators.sudoku import SudokuGenerator
from app.generators.word_search import WordSearchGenerator
from app.generators.maze import MazeGenerator
from app.generators.logic_grid import LogicGridGenerator
from app.generators.code_breaker import CodeBreakerGenerator
from app.generators.matching import MatchingGenerator
from app.generators.pattern import PatternGenerator
from app.generators.critical_thinking import CriticalThinkingGenerator
from app.generators.picture_puzzle import PicturePuzzleGenerator
from app.generators.escape_room import EscapeRoomGenerator

router = APIRouter(prefix="/api")

GENERATOR_MAP = {
    PuzzleType.SUDOKU: SudokuGenerator,
    PuzzleType.WORD_SEARCH: WordSearchGenerator,
    PuzzleType.MAZE: MazeGenerator,
    PuzzleType.LOGIC_GRID: LogicGridGenerator,
    PuzzleType.CODE_BREAKER: CodeBreakerGenerator,
    PuzzleType.MATCHING: MatchingGenerator,
    PuzzleType.PATTERN: PatternGenerator,
    PuzzleType.CRITICAL_THINKING: CriticalThinkingGenerator,
    PuzzleType.PICTURE_PUZZLE: PicturePuzzleGenerator,
    PuzzleType.ESCAPE_ROOM: EscapeRoomGenerator,
}

@router.get("/info")
def get_info():
    return {
        "puzzle_types": [pt.value for pt in PuzzleType],
        "difficulties": [d.value for d in Difficulty]
    }

@router.get("/project/state")
def get_project_state():
    return active_project.get_state()

@router.post("/project/create")
def create_project(settings: BookSettings):
    active_project.new_project(settings)
    return {"status": "success", "message": "Project created"}

class GenerateRequest(BaseModel):
    puzzle_config: Dict[str, PuzzleConfig]

@router.post("/generate")
def generate_puzzles(req: GenerateRequest):
    if not req.puzzle_config:
        raise HTTPException(status_code=400, detail="No puzzle configuration provided")

    active_project.settings.puzzle_configs = req.puzzle_config

    # Clear existing puzzles
    active_project.puzzles = []
    
    # Generate requested number of puzzles for each selected type
    for pt_str, config in req.puzzle_config.items():
        if config.quantity <= 0:
            continue
            
        try:
            pt = PuzzleType(pt_str)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unsupported puzzle type: {pt_str}")
            
        gen_class = GENERATOR_MAP.get(pt)
        if not gen_class:
            raise HTTPException(status_code=400, detail=f"No generator available for puzzle type: {pt_str}")
            
        generator = gen_class(active_project.settings, difficulty=config.difficulty.value)
        
        valid_generated = 0
        max_attempts = config.quantity * 10
        attempts = 0
        
        while valid_generated < config.quantity and attempts < max_attempts:
            attempts += 1
            rec = generator.generate()
            # Validate immediately
            result = PuzzleValidator.validate(rec)
            if result.is_valid:
                active_project.puzzles.append(rec)
                valid_generated += 1
                
        if valid_generated < config.quantity:
            raise HTTPException(
                status_code=500, 
                detail=f"Could only generate {valid_generated}/{config.quantity} valid {pt_str} puzzles after {max_attempts} attempts."
            )
            
    return {"status": "success", "state": active_project.get_state()}

@router.post("/puzzle/{puzzle_id}/regenerate")
def regenerate_puzzle(puzzle_id: str):
    puzzle = active_project.get_puzzle(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Puzzle not found")
        
    try:
        pt = PuzzleType(puzzle.puzzle_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown puzzle type: {puzzle.puzzle_type}")
        
    gen_class = GENERATOR_MAP.get(pt)
    if not gen_class:
        raise HTTPException(status_code=400, detail="Unknown puzzle type")
        
    # Generate new one
    generator = gen_class(active_project.settings, difficulty=puzzle.difficulty)
    
    max_attempts = 10
    attempts = 0
    new_rec = None
    while attempts < max_attempts:
        attempts += 1
        rec = generator.generate()
        rec.puzzle_id = puzzle.puzzle_id
        result = PuzzleValidator.validate(rec)
        if result.is_valid:
            new_rec = rec
            break
            
    if not new_rec:
        raise HTTPException(status_code=500, detail="Failed to regenerate a valid puzzle after multiple attempts.")
    
    active_project.update_puzzle(new_rec)
    
    return {"status": "success", "puzzle": new_rec.model_dump()}

@router.get("/preflight")
def preflight_check():
    errors = []
    warnings = []
    
    if not active_project.puzzles:
        errors.append("No puzzles have been generated yet.")
        
    for p in active_project.puzzles:
        if p.validation_status.value != "valid":
            errors.append(f"Puzzle {p.puzzle_id} ({p.title}) is invalid.")
            
    status = "PASS"
    if errors:
        status = "ERROR"
    elif warnings:
        status = "WARNING"
        
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings
    }

class ExportRequest(BaseModel):
    filename: str

@router.post("/export")
def export_pdf(req: ExportRequest):
    if not active_project.puzzles:
        raise HTTPException(status_code=400, detail="No puzzles to export")
        
    # Preflight check before export
    invalid = [p for p in active_project.puzzles if p.validation_status.value != "valid"]
    if invalid:
        raise HTTPException(status_code=400, detail="Cannot export: Some puzzles are invalid")
        
    # Render PDF
    output_filename = req.filename
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"
        
    output_path = os.path.abspath(output_filename)
    
    try:
        renderer = PDFRenderer(active_project.settings)
        renderer.render_book(active_project.puzzles, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "status": "success", 
        "path": output_path,
        "filename": output_filename
    }
