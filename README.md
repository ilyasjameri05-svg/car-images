# Color-by-Number Mosaic Book Generator for KDP

An AI-powered Color-by-Number Pixel / Mosaic Book Generator tailored for Amazon KDP (Kindle Direct Publishing).

## Features

- **Pixel & Mosaic Generation**: Convert images or prompt AI to generate pixel art puzzles.
- **Custom Themes & Palettes**: Multiple difficulty tiers, color counts, and decorative vector frames.
- **KDP-Ready Export**: Generates high-resolution, print-ready PDF interiors with puzzle and solution pages.
- **FastAPI Backend + Modern Frontend**: Interactive UI for real-time preview and customization.

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run the Application
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000` to access the application.
