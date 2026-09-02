"""
Logic Grid puzzle generator.

Generates a classic "who has what" deduction puzzle:
  - 3 categories (e.g. People, Pets, Colours)
  - 3 or 4 items per category (based on difficulty)

Algorithm:
1. Define theme (people names, pet names, colour names).
2. Create a random valid solution assignment.
3. Generate all possible positive and negative clues from the solution.
4. Shuffle the clues. Add them one by one; after each addition run the
   constraint-propagation solver. Stop when the puzzle is uniquely solvable.
5. Record the minimal clue set.

puzzle_data keys:
  categories  — list of category names (e.g. ["People", "Pets", "Colours"])
  items       — {category: [item, ...]}
  solution    — {person: {category: item}}  (the full solution)
  clues       — list of clue strings used in the puzzle
  num_items   — int (items per category)
"""
from __future__ import annotations

import random
from itertools import product
from typing import Optional

from app.generators.base import BasePuzzleGenerator
from app.models.book import BookSettings
from app.models.puzzle import PuzzleRecord, ValidationStatus

# Themes: (people, pets, colours/hobbies)
_THEMES: list[dict] = [
    {
        "name": "Beach Holiday",
        "categories": ["People", "Drinks", "Activities"],
        "items": {
            "People":     ["Alice", "Ben", "Clara", "Dan"],
            "Drinks":     ["Juice", "Water", "Tea", "Lemonade"],
            "Activities": ["Swimming", "Surfing", "Kayaking", "Sunbathing"],
        },
    },
    {
        "name": "School Science Fair",
        "categories": ["Students", "Projects", "Prizes"],
        "items": {
            "Students": ["Emma", "Liam", "Mia", "Noah"],
            "Projects": ["Volcano", "Robot", "Telescope", "Windmill"],
            "Prizes":   ["Gold", "Silver", "Bronze", "Merit"],
        },
    },
    {
        "name": "Pet Show",
        "categories": ["Owners", "Pets", "Colours"],
        "items": {
            "Owners": ["Sara", "Tom", "Lily", "Jack"],
            "Pets":   ["Dog", "Cat", "Rabbit", "Parrot"],
            "Colours": ["Red", "Blue", "Green", "Yellow"],
        },
    },
    {
        "name": "Birthday Party",
        "categories": ["Children", "Gifts", "Cakes"],
        "items": {
            "Children": ["Amy", "Bob", "Chloe", "Dave"],
            "Gifts":    ["Book", "Toy", "Game", "Puzzle"],
            "Cakes":    ["Chocolate", "Vanilla", "Strawberry", "Lemon"],
        },
    },
]

_INSTRUCTIONS: dict[str, str] = {
    "english": (
        "Use the clues to fill in the grid. Each person has exactly one of each category. "
        "Mark ✓ when you are sure of a match and ✗ when it is impossible."
    ),
    "french": (
        "Utilisez les indices pour remplir la grille. Chaque personne a exactement un élément de chaque catégorie."
    ),
    "spanish": (
        "Usa las pistas para completar la cuadrícula. Cada persona tiene exactamente un elemento de cada categoría."
    ),
    "arabic": (
        "استخدم الأدلة لملء الشبكة. كل شخص لديه عنصر واحد بالضبط من كل فئة."
    ),
}

_NUM_ITEMS: dict[str, int] = {"easy": 3, "medium": 3, "hard": 4}


class LogicGridGenerator(BasePuzzleGenerator):
    def __init__(self, settings: BookSettings, difficulty: str = None, seed: Optional[int] = None) -> None:
        super().__init__(settings, difficulty=difficulty)
        self._seed = seed

    def generate(self) -> PuzzleRecord:
        rng = random.Random(self._seed)
        diff = self.difficulty
        n = _NUM_ITEMS.get(diff, 3)

        theme = rng.choice(_THEMES)
        categories = theme["categories"]  # [cat_A, cat_B, cat_C]
        # Primary category is always index 0 (people / students / owners / children)
        primary = categories[0]
        other_cats = categories[1:]

        # Trim items to n
        people = theme["items"][primary][:n]
        items_by_cat: dict[str, list[str]] = {primary: people}
        for cat in other_cats:
            items_by_cat[cat] = theme["items"][cat][:n]

        # Generate random solution: person → {cat: item}
        solution: dict[str, dict[str, str]] = {}
        for cat in other_cats:
            shuffled = list(items_by_cat[cat])
            rng.shuffle(shuffled)
            for person, item in zip(people, shuffled):
                if person not in solution:
                    solution[person] = {}
                solution[person][cat] = item

        # Generate all possible clues
        all_clues = self._generate_all_clues(solution, people, other_cats)
        rng.shuffle(all_clues)

        # Incrementally add clues until uniquely solvable
        selected_clues: list[str] = []
        for clue_text, clue_data in all_clues:
            selected_clues.append(clue_text)
            if self._is_uniquely_solvable(selected_clues, people, items_by_cat, other_cats, solution):
                break

        instructions = _INSTRUCTIONS.get(self.language, _INSTRUCTIONS["english"])

        return PuzzleRecord(
            puzzle_type="logic_grid",
            difficulty=diff,
            language=self.language,
            title=f"Logic Grid: {theme['name']} #{rng.randint(100, 999)}",
            instructions=instructions,
            puzzle_data={
                "theme":      theme["name"],
                "categories": categories,
                "items":      items_by_cat,
                "solution":   solution,
                "clues":      selected_clues,
                "num_items":  n,
                "primary":    primary,
                "other_cats": other_cats,
            },
            validation_status=ValidationStatus.PENDING,
            seed=self._seed,
        )

    # ------------------------------------------------------------------
    # Clue generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_all_clues(
        solution: dict[str, dict[str, str]],
        people: list[str],
        other_cats: list[str],
    ) -> list[tuple[str, dict]]:
        """Generate positive and cross-category clues from the solution."""
        clues: list[tuple[str, dict]] = []

        # Positive clues: "Alice has the Dog."
        for person in people:
            for cat in other_cats:
                item = solution[person][cat]
                clues.append((
                    f"{person} has the {item}.",
                    {"type": "positive", "person": person, "cat": cat, "item": item},
                ))

        # Negative clues: "Alice does NOT have the Cat."
        for person in people:
            for cat in other_cats:
                correct_item = solution[person][cat]
                # Generate one negative for a different item in the same category
                wrong_items = [
                    solution[p][cat] for p in people if solution[p][cat] != correct_item
                ]
                for wi in wrong_items[:1]:  # limit one negative per person-cat
                    clues.append((
                        f"{person} does NOT have the {wi}.",
                        {"type": "negative", "person": person, "cat": cat, "item": wi},
                    ))

        # Cross-category clues: "The person with Dog also has Red."
        if len(other_cats) >= 2:
            cat_a, cat_b = other_cats[0], other_cats[1]
            for person in people:
                ia = solution[person][cat_a]
                ib = solution[person][cat_b]
                clues.append((
                    f"The person with the {ia} also has the {ib}.",
                    {"type": "cross", "cat_a": cat_a, "item_a": ia, "cat_b": cat_b, "item_b": ib},
                ))

        return clues

    def _is_uniquely_solvable(
        self,
        clues: list[str],
        people: list[str],
        items_by_cat: dict[str, list[str]],
        other_cats: list[str],
        solution: dict[str, dict[str, str]],
    ) -> bool:
        """
        Run a simple constraint propagation check.
        Returns True if the given clues lead to exactly the stored solution.
        """
        from app.solvers.logic_solver import LogicSolver
        solver = LogicSolver(people, items_by_cat, other_cats, clues)
        derived = solver.solve()
        return derived == solution
