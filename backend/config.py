"""
Application configuration — settings, env vars, page sizes, constants.
"""
import os
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
TEMP_DIR = DATA_DIR / "temp"
DECOR_DIR = BASE_DIR / "decor"
DATABASE_PATH = DATA_DIR / "database.db"

for d in [DATA_DIR, PROJECTS_DIR, TEMP_DIR, DECOR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Database ───────────────────────────────────────────────────────────
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# ── AI Provider ────────────────────────────────────────────────────────
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "placeholder")       # "openai" | "placeholder"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")

# ── Grid sizes ─────────────────────────────────────────────────────────
GRID_SIZES = [20, 30, 40, 50, 60]
DEFAULT_GRID_SIZE = 30

# ── Color counts ───────────────────────────────────────────────────────
COLOR_COUNTS = ["auto", 6, 8, 10, 12, 15, 20]
DEFAULT_COLOR_COUNT = "auto"

# ── Page counts ────────────────────────────────────────────────────────
PAGE_COUNTS = [10, 20, 30, 50, 100]

# ── Enums ──────────────────────────────────────────────────────────────

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class PageSizeType(str, Enum):
    A4 = "a4"
    US_LETTER = "us_letter"
    KDP_8_5x11 = "kdp_8_5x11"
    KDP_8x10 = "kdp_8x10"
    CUSTOM = "custom"

class Orientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class AnswerKeyPosition(str, Enum):
    AFTER_EACH = "after_each"
    AT_END = "at_end"

class DecorationMode(str, Enum):
    OFF = "off"
    LIBRARY = "library"
    CUSTOM = "custom"

class ExportFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"

class PageType(str, Enum):
    PUZZLE = "puzzle"
    ANSWER = "answer"

# ── Page size definitions (in points, 1 point = 1/72 inch) ────────────

@dataclass
class PageSize:
    name: str
    width_pt: float
    height_pt: float
    # KDP safe margins in points (inside margin depends on page count)
    margin_top_pt: float = 18.0      # 0.25"
    margin_bottom_pt: float = 18.0
    margin_outside_pt: float = 18.0
    margin_inside_pt: float = 36.0   # 0.5" default gutter
    bleed_pt: float = 0.0            # no bleed by default

PAGE_SIZES: dict[str, PageSize] = {
    "a4": PageSize("A4", 595.28, 841.89),
    "us_letter": PageSize("US Letter", 612.0, 792.0),
    "kdp_8_5x11": PageSize("KDP 8.5×11", 612.0, 792.0,
                           margin_top_pt=27.0, margin_bottom_pt=27.0,
                           margin_outside_pt=27.0, margin_inside_pt=36.0),
    "kdp_8x10": PageSize("KDP 8×10", 576.0, 720.0,
                          margin_top_pt=27.0, margin_bottom_pt=27.0,
                          margin_outside_pt=27.0, margin_inside_pt=36.0),
}

# ── Difficulty defaults ────────────────────────────────────────────────

DIFFICULTY_DEFAULTS: dict[str, dict] = {
    "easy":   {"grid_size": 20, "color_count": 8,  "detail": "low"},
    "medium": {"grid_size": 30, "color_count": 10, "detail": "medium"},
    "hard":   {"grid_size": 40, "color_count": 12, "detail": "high"},
    "expert": {"grid_size": 50, "color_count": 15, "detail": "very_high"},
}

# ── Theme prompt templates ─────────────────────────────────────────────

THEME_SUBJECTS: dict[str, list[str]] = {
    "animals": [
        "cat", "dog", "lion", "tiger", "elephant", "horse", "rabbit",
        "fox", "bear", "dinosaur", "bird", "fish", "owl", "penguin",
        "giraffe", "zebra", "monkey", "dolphin", "turtle", "butterfly",
        "panda", "koala", "deer", "wolf", "parrot", "flamingo",
        "hedgehog", "frog", "whale", "octopus",
    ],
    "christmas": [
        "christmas tree", "santa claus", "reindeer", "snowman",
        "gingerbread man", "christmas stocking", "candy cane",
        "christmas wreath", "elf", "sleigh", "christmas present",
        "bell", "angel", "star", "nutcracker",
    ],
    "halloween": [
        "pumpkin", "ghost", "black cat", "witch hat", "spider",
        "bat", "haunted house", "skeleton", "mummy", "vampire",
        "werewolf", "cauldron", "zombie", "candy bucket", "scarecrow",
    ],
    "space": [
        "rocket", "astronaut", "planet earth", "saturn", "moon",
        "sun", "ufo", "alien", "space shuttle", "comet",
        "telescope", "stars", "mars rover", "satellite", "nebula",
    ],
    "dinosaur": [
        "tyrannosaurus rex", "triceratops", "stegosaurus",
        "brontosaurus", "pterodactyl", "velociraptor", "spinosaurus",
        "ankylosaurus", "parasaurolophus", "diplodocus",
        "iguanodon", "pachycephalosaurus", "dino egg", "fossil", "volcano",
    ],
    "ocean": [
        "clownfish", "seahorse", "jellyfish", "starfish", "crab",
        "lobster", "shark", "whale", "sea turtle", "coral reef",
        "squid", "pufferfish", "manta ray", "seal", "walrus",
    ],
    "farm": [
        "cow", "pig", "chicken", "sheep", "horse", "goat", "duck",
        "rooster", "barn", "tractor", "scarecrow", "sunflower",
        "corn", "hay bale", "windmill",
    ],
    "jungle": [
        "toucan", "gorilla", "jaguar", "tree frog", "chameleon",
        "sloth", "anaconda", "macaw", "spider monkey", "tapir",
        "jungle waterfall", "tropical flower", "palm tree",
        "vine bridge", "bamboo",
    ],
    "fantasy": [
        "dragon", "unicorn", "fairy", "wizard", "mermaid", "phoenix",
        "castle", "magic wand", "treasure chest", "crystal ball",
        "gnome", "pegasus", "enchanted forest", "potion bottle", "crown",
    ],
    "winter": [
        "snowflake", "igloo", "polar bear", "penguin", "ice skates",
        "hot cocoa", "scarf", "mitten", "sled", "pine tree",
        "snowball", "icicle", "cabin", "fireplace", "aurora borealis",
    ],
    "summer": [
        "beach ball", "sandcastle", "palm tree", "sunglasses",
        "ice cream cone", "watermelon", "surfboard", "flip flops",
        "sun umbrella", "popsicle", "seashell", "lemonade",
        "swimming pool", "sailboat", "tropical fish",
    ],
}

def build_image_prompt(subject: str, theme: str = "") -> str:
    """Build an optimized prompt for AI image generation.

    The generated image should be a colorful professional illustration
    perfect for conversion into a color-by-number mosaic.
    """
    return (
        f"A colorful professional digital illustration of a cute {subject}. "
        f"The illustration has a clear single centered subject with a strong silhouette. "
        f"Use flat solid distinct colors with large and medium color regions. "
        f"The subject should be fully visible with clean defined edges and strong contrast. "
        f"Simple clean background with minimal visual noise. "
        f"Cartoon illustration style with vibrant colors. "
        f"No text, no numbers, no watermarks, no logos. "
        f"Not pixel art, not line art, not a coloring book page. "
        f"High quality, professional children's book illustration style."
    )
