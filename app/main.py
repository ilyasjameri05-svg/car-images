import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.router import router

app = FastAPI(title="KDP Puzzle Book Generator")

# Include API router
app.include_router(router)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Create static dir if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
