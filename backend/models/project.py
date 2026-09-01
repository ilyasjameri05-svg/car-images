"""
SQLAlchemy models for Book Projects and Book Pages.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class BookProject(Base):
    __tablename__ = "book_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    subtitle = Column(String(255), default="")
    author = Column(String(255), default="")
    theme = Column(String(100), default="animals")
    difficulty = Column(String(50), default="medium")
    grid_size = Column(Integer, default=30)
    color_count = Column(String(50), default="auto")
    page_size = Column(String(50), default="kdp_8_5x11")
    orientation = Column(String(50), default="portrait")
    answer_key_position = Column(String(50), default="at_end")
    decoration_mode = Column(String(50), default="off")
    decoration_theme = Column(String(100), default="")
    seed = Column(Integer, nullable=True)
    settings_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    pages = relationship("BookPage", back_populates="project",
                         cascade="all, delete-orphan",
                         order_by="BookPage.page_number")

    @property
    def settings(self) -> dict:
        return json.loads(self.settings_json) if self.settings_json else {}

    @settings.setter
    def settings(self, value: dict):
        self.settings_json = json.dumps(value)


class BookPage(Base):
    __tablename__ = "book_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("book_projects.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_type = Column(String(50), default="puzzle")  # "puzzle" | "answer"
    title = Column(String(255), default="")
    puzzle_id = Column(Integer, ForeignKey("puzzles.id"), nullable=True)
    source_image_path = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("BookProject", back_populates="pages")
    puzzle = relationship("ColorByNumberPuzzle", backref="pages")
