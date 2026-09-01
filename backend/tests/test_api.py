"""
Tests for API endpoints.
"""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image
import io

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.main import app
from backend.database import init_db, Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


class TestHealthCheck:
    def test_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestConfig:
    def test_get_config(self):
        r = client.get("/api/config")
        assert r.status_code == 200
        data = r.json()
        assert "grid_sizes" in data
        assert "color_counts" in data
        assert "themes" in data
        assert "page_sizes" in data


class TestProjectsAPI:
    def test_create_project(self):
        r = client.post("/api/projects", json={
            "name": "Test Book",
            "theme": "animals",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Test Book"
        assert data["id"] > 0

    def test_list_projects(self):
        client.post("/api/projects", json={"name": "Book 1"})
        client.post("/api/projects", json={"name": "Book 2"})
        r = client.get("/api/projects")
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_get_project(self):
        create = client.post("/api/projects", json={"name": "Test"})
        pid = create.json()["id"]
        r = client.get(f"/api/projects/{pid}")
        assert r.status_code == 200
        assert r.json()["name"] == "Test"

    def test_update_project(self):
        create = client.post("/api/projects", json={"name": "Old"})
        pid = create.json()["id"]
        r = client.put(f"/api/projects/{pid}", json={"name": "New"})
        assert r.status_code == 200
        assert r.json()["name"] == "New"

    def test_delete_project(self):
        create = client.post("/api/projects", json={"name": "Delete Me"})
        pid = create.json()["id"]
        r = client.delete(f"/api/projects/{pid}")
        assert r.status_code == 200
        r2 = client.get(f"/api/projects/{pid}")
        assert r2.status_code == 404


class TestImagesAPI:
    def test_upload_image(self):
        img = Image.new("RGB", (100, 100), "#FF0000")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        r = client.post("/api/images/upload",
                         files=[("files", ("test.png", buf, "image/png"))])
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 1

    def test_provider_info(self):
        r = client.get("/api/images/provider-info")
        assert r.status_code == 200
        assert "name" in r.json()

    def test_themes_list(self):
        r = client.get("/api/images/themes")
        assert r.status_code == 200
        assert "themes" in r.json()


class TestPuzzlesAPI:
    def _upload_image(self):
        """Upload a test image and return its path."""
        img = Image.new("RGB", (200, 200))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 100, 100], fill="#E53935")
        draw.rectangle([100, 0, 200, 100], fill="#1E88E5")
        draw.rectangle([0, 100, 100, 200], fill="#43A047")
        draw.rectangle([100, 100, 200, 200], fill="#FDD835")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        r = client.post("/api/images/upload",
                         files=[("files", ("test.png", buf, "image/png"))])
        return r.json()["uploaded"][0]["path"]

    def test_generate_puzzle(self):
        path = self._upload_image()
        r = client.post("/api/puzzles/generate", json={
            "source_image_path": path,
            "grid_width": 20,
            "grid_height": 20,
            "color_count": 6,
            "seed": 42,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["grid_width"] == 20
        assert data["cell_count"] == 400
        assert len(data["palette"]) == 6

    def test_get_puzzle(self):
        path = self._upload_image()
        create = client.post("/api/puzzles/generate", json={
            "source_image_path": path,
            "grid_width": 20, "grid_height": 20, "color_count": 6,
        })
        pid = create.json()["id"]
        r = client.get(f"/api/puzzles/{pid}")
        assert r.status_code == 200
        assert len(r.json()["cells"]) == 400
