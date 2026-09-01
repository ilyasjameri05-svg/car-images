"""
Main FastAPI application — CORS, static serving, startup, routing.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.core.decoration_manager import generate_decorations
from backend.api import projects, images, puzzles, books, export
from backend.config import TEMP_DIR

app = FastAPI(
    title="Color-by-Number Mosaic Book Generator",
    description="AI-powered Color-by-Number Mosaic Book Generator for KDP",
    version="1.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(projects.router)
app.include_router(images.router)
app.include_router(puzzles.router)
app.include_router(books.router)
app.include_router(export.router)

# Serve frontend static files
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    if (FRONTEND_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")),
                  name="assets")


@app.on_event("startup")
def startup():
    """Initialize database and generate decorations on startup."""
    init_db()
    generate_decorations()
    # Ensure temp directory exists
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Color-by-Number Mosaic Book Generator API",
            "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/config")
async def get_config():
    """Return application configuration for the frontend."""
    from backend.config import (
        GRID_SIZES, COLOR_COUNTS, PAGE_COUNTS, DIFFICULTY_DEFAULTS,
        THEME_SUBJECTS, PAGE_SIZES,
    )
    from backend.providers.factory import get_provider_info

    return {
        "grid_sizes": GRID_SIZES,
        "color_counts": COLOR_COUNTS,
        "page_counts": PAGE_COUNTS,
        "difficulty_defaults": DIFFICULTY_DEFAULTS,
        "themes": list(THEME_SUBJECTS.keys()),
        "page_sizes": {k: {"name": v.name, "width": v.width_pt, "height": v.height_pt}
                       for k, v in PAGE_SIZES.items()},
        "provider": get_provider_info(),
    }
