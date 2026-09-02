"""
Curated word lists organised by theme and difficulty for Word Search puzzles.

Each theme provides three lists:
  easy   — short words (3–6 letters), ~8 words
  medium — mid-length words (4–8 letters), ~10 words
  hard   — longer words (5–10 letters), ~12 words
"""
from __future__ import annotations
import random

WORD_LISTS: dict[str, dict[str, list[str]]] = {
    "animals": {
        "easy":   ["CAT", "DOG", "FOX", "OWL", "ANT", "BEE", "EEL", "YAK"],
        "medium": ["HORSE", "TIGER", "EAGLE", "SHARK", "PANDA", "LEMUR", "SNAKE", "CRANE", "BISON", "GECKO"],
        "hard":   ["LEOPARD", "DOLPHIN", "PENGUIN", "ELEPHANT", "CROCODILE", "BUTTERFLY", "CHAMELEON", "FLAMINGO", "WOLVERINE", "SALAMANDER", "PORCUPINE", "CHIMPANZEE"],
    },
    "space": {
        "easy":   ["SUN", "MOON", "STAR", "MARS", "ORBIT", "COMET", "ALIEN", "NOVA"],
        "medium": ["PLANET", "SATURN", "NEBULA", "GALAXY", "METEOR", "ROCKET", "PULSAR", "QUASAR", "CRATER", "COSMOS"],
        "hard":   ["ASTEROID", "SUPERNOVA", "TELESCOPE", "BLACKHOLE", "UNIVERSE", "RADIATION", "SATELLITE", "SPACECRAFT", "ATMOSPHERE", "ASTRONAUT", "CONSTELLATION", "SOLARSYSTEM"],
    },
    "food": {
        "easy":   ["PIE", "CAKE", "RICE", "FISH", "CORN", "BEAN", "PLUM", "PEAR"],
        "medium": ["PIZZA", "PASTA", "BREAD", "SALAD", "MANGO", "CHEESE", "LEMON", "ONION", "CARROT", "COOKIE"],
        "hard":   ["LASAGNA", "BROCCOLI", "EGGPLANT", "BLUEBERRY", "CHOCOLATE", "PINEAPPLE", "AVOCADO", "MUSHROOM", "CINNAMON", "ARTICHOKE", "RASPBERRY", "WATERMELON"],
    },
    "sports": {
        "easy":   ["RUN", "SWIM", "KICK", "GOLF", "RACE", "JUMP", "DIVE", "SKII"],
        "medium": ["TENNIS", "SOCCER", "BOXING", "HOCKEY", "ROWING", "ARCHERY", "CYCLING", "FENCING", "KARATE", "SURFING"],
        "hard":   ["FOOTBALL", "BASEBALL", "VOLLEYBALL", "WRESTLING", "GYMNASTICS", "MARATHON", "BADMINTON", "SKATEBOARD", "SNOWBOARD", "TRIATHLON", "BASKETBALL", "ATHLETICS"],
    },
    "nature": {
        "easy":   ["LAKE", "HILL", "TREE", "RAIN", "WIND", "ROCK", "LEAF", "ROSE"],
        "medium": ["OCEAN", "RIVER", "FOREST", "DESERT", "CANYON", "VALLEY", "MEADOW", "SPRING", "ISLAND", "JUNGLE"],
        "hard":   ["MOUNTAIN", "WATERFALL", "RAINFOREST", "PENINSULA", "ECOSYSTEM", "VOLCANO", "GLACIER", "MANGROVE", "ESTUARY", "SAVANNA", "TUNDRA", "ARCHIPELAGO"],
    },
    "school": {
        "easy":   ["PEN", "BOOK", "DESK", "MATH", "READ", "TEST", "QUIZ", "DRAW"],
        "medium": ["PENCIL", "ERASER", "LESSON", "SCIENCE", "LIBRARY", "TEACHER", "STUDENT", "HISTORY", "ENGLISH", "WRITING"],
        "hard":   ["HOMEWORK", "CLASSROOM", "GEOGRAPHY", "CHEMISTRY", "BIOLOGY", "PRINCIPAL", "GYMNASIUM", "CALCULATE", "LITERATURE", "VOCABULARY", "ARITHMETIC", "MICROSCOPE"],
    },
    "music": {
        "easy":   ["NOTE", "DRUM", "SONG", "HARP", "LUTE", "BEAT", "CLAP", "TUNE"],
        "medium": ["PIANO", "GUITAR", "VIOLIN", "CHORUS", "MELODY", "RHYTHM", "TRUMPET", "FLUTE", "OBOE", "SONATA"],
        "hard":   ["SYMPHONY", "ORCHESTRA", "CONDUCTOR", "SAXOPHONE", "CLARINET", "TROMBONE", "ACCORDION", "PERCUSSION", "HARMONICA", "XYLOPHONE", "COMPOSITION", "CONCERTO"],
    },
    "countries": {
        "easy":   ["PERU", "IRAN", "CUBA", "CHAD", "MALI", "TOGO", "OMAN", "FIJI"],
        "medium": ["JAPAN", "INDIA", "EGYPT", "KENYA", "SPAIN", "ITALY", "CHINA", "BRAZIL", "GHANA", "CHILE"],
        "hard":   ["GERMANY", "PORTUGAL", "ETHIOPIA", "COLOMBIA", "ARGENTINA", "AUSTRALIA", "SINGAPORE", "INDONESIA", "VENEZUELA", "BANGLADESH", "PHILIPPINES", "SWITZERLAND"],
    },
    "classic": {
        "easy":   ["RED", "BLUE", "BIG", "FAST", "COLD", "HOT", "TOP", "NEW"],
        "medium": ["HAPPY", "FUNNY", "BRAVE", "SMART", "QUIET", "PROUD", "LUCKY", "SHINY", "CLEAN", "SWEET"],
        "hard":   ["MYSTERY", "CAPTAIN", "JOURNEY", "FREEDOM", "CRYSTAL", "HORIZON", "LANTERN", "COMPASS", "THUNDER", "DIAMOND", "RAINBOW", "TWILIGHT"],
    },
}

THEMES = list(WORD_LISTS.keys())


def get_words(theme: str, difficulty: str, rng: random.Random | None = None) -> list[str]:
    """Return words for the given theme and difficulty, shuffled."""
    theme = theme.lower() if theme.lower() in WORD_LISTS else "classic"
    diff = difficulty if difficulty in ("easy", "medium", "hard") else "medium"
    words = list(WORD_LISTS[theme][diff])
    if rng:
        rng.shuffle(words)
    return words


def get_random_theme(rng: random.Random) -> str:
    return rng.choice(THEMES)
