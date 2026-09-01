"""
Palette color model — the named-color reference database.
"""
from sqlalchemy import Column, Integer, String
from backend.database import Base


class PaletteColor(Base):
    __tablename__ = "palette_colors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    color_id = Column(Integer, nullable=False)
    color_name = Column(String(100), nullable=False)
    color_hex = Column(String(7), nullable=False)   # e.g. "#E53935"
    category = Column(String(100), default="")       # e.g. "red", "blue"
