"""
Comprehensive End-to-End Tests for Auto Color Count and Manual Color Counts.
"""
import pytest
import io
from pathlib import Path
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import Base, engine
from backend.core.color_quantizer import detect_optimal_color_count, quantize_colors
from backend.core.puzzle_generator import generate_puzzle
from backend.validators.book_validator import validate_book

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def sample_image_path(tmp_path):
    """Generate a test image and save to disk."""
    img = Image.new("RGB", (300, 300), "#0A192F")
    draw = ImageDraw.Draw(img)
    # Draw colorful features
    draw.rectangle([50, 50, 250, 250], fill="#E53935")
    draw.ellipse([80, 80, 140, 140], fill="#1E88E5")
    draw.ellipse([160, 80, 220, 140], fill="#43A047")
    draw.polygon([(150, 150), (130, 200), (170, 200)], fill="#FDD835")
    draw.rectangle([100, 210, 200, 230], fill="#FFFFFF")
    
    file_path = tmp_path / "test_subject.png"
    img.save(file_path, "PNG")
    return str(file_path)


class TestAutoColorQuantization:
    def test_allowed_integers_only(self, sample_image_path):
        """Auto must resolve strictly to one of [6, 8, 10, 12, 15, 20]."""
        img = Image.open(sample_image_path)
        allowed = [6, 8, 10, 12, 15, 20]
        for diff in ["easy", "medium", "hard", "expert"]:
            count = detect_optimal_color_count(img, grid_width=30, grid_height=30, difficulty=diff, seed=42)
            assert count in allowed, f"Resolved count {count} not in allowed set {allowed}"

    def test_deterministic_with_seed(self, sample_image_path):
        """Auto color detection must be 100% deterministic when seed is provided."""
        img = Image.open(sample_image_path)
        c1 = detect_optimal_color_count(img, grid_width=30, grid_height=30, difficulty="medium", seed=99)
        c2 = detect_optimal_color_count(img, grid_width=30, grid_height=30, difficulty="medium", seed=99)
        assert c1 == c2

        p1 = generate_puzzle(img, grid_width=30, grid_height=30, color_count="auto", seed=99)
        p2 = generate_puzzle(img, grid_width=30, grid_height=30, color_count="auto", seed=99)
        assert p1.color_count == p2.color_count
        assert [c.color_hex for c in p1.palette] == [c.color_hex for c in p2.palette]

    def test_manual_color_counts(self, sample_image_path):
        """Manual color counts 6, 12, 20 should produce exact palette lengths."""
        img = Image.open(sample_image_path)
        for expected in [6, 12, 20]:
            puzzle = generate_puzzle(img, grid_width=30, grid_height=30, color_count=expected, seed=42)
            assert puzzle.color_count == expected
            assert len(puzzle.palette) == expected
            assert puzzle.requested_color_count == expected


class TestAutoColorsAPI:
    def test_preview_with_auto(self, sample_image_path):
        """Preview endpoint should accept color_count='auto' and return resolved count."""
        r = client.post("/api/puzzles/preview", json={
            "source_image_path": sample_image_path,
            "grid_width": 30,
            "grid_height": 30,
            "color_count": "auto",
            "seed": 42,
            "preview_type": "puzzle",
        })
        assert r.status_code == 200
        data = r.json()
        assert "image" in data
        assert data["resolved_color_count"] in [6, 8, 10, 12, 15, 20]
        assert data["recommended_color_count"] == data["resolved_color_count"]

    def test_preview_with_manual_integers(self, sample_image_path):
        """Preview endpoint should accept manual integers (6, 12, 20)."""
        for count in [6, 12, 20]:
            r = client.post("/api/puzzles/preview", json={
                "source_image_path": sample_image_path,
                "grid_width": 30,
                "grid_height": 30,
                "color_count": count,
                "seed": 42,
                "preview_type": "puzzle",
            })
            assert r.status_code == 200
            data = r.json()
            assert data["resolved_color_count"] == count

    def test_puzzle_generate_with_auto(self, sample_image_path):
        """Generate endpoint must accept 'auto' and store both requested and resolved counts."""
        r = client.post("/api/puzzles/generate", json={
            "source_image_path": sample_image_path,
            "grid_width": 30,
            "grid_height": 30,
            "color_count": "auto",
            "seed": 42,
            "title": "Auto Cat",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["requested_color_count"] == "auto"
        assert data["resolved_color_count"] in [6, 8, 10, 12, 15, 20]
        assert data["color_count"] == data["resolved_color_count"]
        assert len(data["palette"]) == data["resolved_color_count"]

    def test_invalid_color_counts_rejected(self, sample_image_path):
        """Invalid color_count values (out of range, invalid string) must be rejected with 422."""
        invalid_values = [3, 25, 99, "invalid", "custom_5", -1]
        for val in invalid_values:
            r = client.post("/api/puzzles/generate", json={
                "source_image_path": sample_image_path,
                "grid_width": 30,
                "grid_height": 30,
                "color_count": val,
            })
            assert r.status_code == 422, f"Value {val} should have been rejected"


class TestBookWorkflowWithAuto:
    def test_create_project_with_auto(self):
        """Create project endpoint should accept color_count='auto'."""
        r = client.post("/api/projects", json={
            "name": "Auto Colors Book",
            "color_count": "auto",
            "grid_size": 30,
            "difficulty": "medium",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Auto Colors Book"
        assert data["color_count"] == "auto"

    def test_end_to_end_book_creation_and_export_pdf(self, sample_image_path):
        """Complete workflow: Create Book with Auto -> Generate Puzzle -> Validate -> Export PDF."""
        # 1. Create project with color_count="auto"
        proj_res = client.post("/api/projects", json={
            "name": "Full Auto Book",
            "theme": "animals",
            "difficulty": "medium",
            "grid_size": 30,
            "color_count": "auto",
            "page_size": "kdp_8_5x11",
            "orientation": "portrait",
            "answer_key_position": "at_end",
        })
        assert proj_res.status_code == 200
        project_id = proj_res.json()["id"]

        # 2. Generate puzzle with color_count="auto"
        puzzle_res = client.post("/api/puzzles/generate", json={
            "source_image_path": sample_image_path,
            "grid_width": 30,
            "grid_height": 30,
            "color_count": "auto",
            "difficulty": "medium",
            "title": "Auto Page 1",
            "seed": 42,
            "project_id": project_id,
        })
        assert puzzle_res.status_code == 200
        puzzle_id = puzzle_res.json()["id"]
        assert puzzle_res.json()["resolved_color_count"] in [6, 8, 10, 12, 15, 20]

        # 3. Add page to project
        page_res = client.post(f"/api/projects/{project_id}/pages", json={
            "page_number": 1,
            "page_type": "puzzle",
            "title": "Auto Page 1",
            "puzzle_id": puzzle_id,
            "source_image_path": sample_image_path,
        })
        assert page_res.status_code == 200

        # 4. Validate book
        val_res = client.post("/api/export/validate", json={
            "project_id": project_id,
            "format": "pdf",
            "export_type": "complete",
            "page_size": "kdp_8_5x11",
            "orientation": "portrait",
        })
        assert val_res.status_code == 200
        assert val_res.json()["is_valid"] is True

        # 5. Export Complete Book PDF
        export_res = client.post("/api/export/pdf", json={
            "project_id": project_id,
            "format": "pdf",
            "export_type": "complete",
            "page_size": "kdp_8_5x11",
            "orientation": "portrait",
        })
        assert export_res.status_code == 200
        assert export_res.headers["content-type"] == "application/pdf"
        assert len(export_res.content) > 1000  # Valid PDF binary bytes
