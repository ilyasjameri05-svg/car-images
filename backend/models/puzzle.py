"""
SQLAlchemy model for Color-by-Number Puzzles.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.database import Base


class ColorByNumberPuzzle(Base):
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seed = Column(Integer, nullable=True)
    source_image_path = Column(String(500), default="")
    grid_width = Column(Integer, nullable=False)
    grid_height = Column(Integer, nullable=False)
    color_count = Column(Integer, nullable=False)  # Actual resolved integer count
    requested_color_count = Column(String(50), default="auto")  # 'auto' or original request
    difficulty = Column(String(50), default="medium")
    title = Column(String(255), default="")

    # Cells stored as JSON: list of {row, col, color_id, color_hex}
    cells_json = Column(Text, nullable=False, default="[]")

    # Palette stored as JSON: list of {color_id, color_name, color_hex}
    palette_json = Column(Text, nullable=False, default="[]")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def cells(self) -> list[dict]:
        return json.loads(self.cells_json) if self.cells_json else []

    @cells.setter
    def cells(self, value: list[dict]):
        self.cells_json = json.dumps(value)

    @property
    def palette(self) -> list[dict]:
        return json.loads(self.palette_json) if self.palette_json else []

    @palette.setter
    def palette(self, value: list[dict]):
        self.palette_json = json.dumps(value)

    def get_cell(self, row: int, col: int) -> dict | None:
        for cell in self.cells:
            if cell["row"] == row and cell["col"] == col:
                return cell
        return None

    def validate_grid(self) -> list[str]:
        """Validate grid integrity. Returns list of error messages."""
        errors = []
        cells = self.cells
        palette = self.palette

        expected = self.grid_width * self.grid_height
        if len(cells) != expected:
            errors.append(
                f"Cell count mismatch: expected {expected}, got {len(cells)}"
            )

        palette_ids = {p["color_id"] for p in palette}
        for cell in cells:
            if cell["color_id"] not in palette_ids:
                errors.append(
                    f"Cell ({cell['row']},{cell['col']}) has invalid "
                    f"color_id {cell['color_id']}"
                )

        # Check for duplicate positions
        positions = set()
        for cell in cells:
            pos = (cell["row"], cell["col"])
            if pos in positions:
                errors.append(f"Duplicate cell at {pos}")
            positions.add(pos)

        # Check all positions covered
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                if (r, c) not in positions:
                    errors.append(f"Missing cell at ({r},{c})")

        return errors
