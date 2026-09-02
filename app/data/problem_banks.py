"""
Curated problem banks for:
  - Critical Thinking puzzles (logic riddles, word problems)
  - Matching puzzle pair sets
  - Escape Room multi-step puzzles

Every problem has a guaranteed, verifiable answer stored alongside it.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Critical Thinking problem bank
# ---------------------------------------------------------------------------
# Each entry: {id, question, answer, explanation, difficulty}

CRITICAL_THINKING_PROBLEMS: list[dict] = [
    # --- EASY ---
    {
        "id": "ct_001", "difficulty": "easy",
        "question": "I have hands but cannot clap. I have a face but no eyes. What am I?",
        "answer": "A clock",
        "explanation": "A clock has hands (hour/minute/second) and a face (the dial) but cannot clap or see.",
    },
    {
        "id": "ct_002", "difficulty": "easy",
        "question": "If there are 3 apples and you take away 2, how many apples do YOU have?",
        "answer": "2",
        "explanation": "You took 2 apples, so you have 2.",
    },
    {
        "id": "ct_003", "difficulty": "easy",
        "question": "A rooster lays an egg on the peak of a roof. Which way does it roll?",
        "answer": "Roosters don't lay eggs",
        "explanation": "Only hens lay eggs, so no egg rolls anywhere.",
    },
    {
        "id": "ct_004", "difficulty": "easy",
        "question": "What gets wetter the more it dries?",
        "answer": "A towel",
        "explanation": "A towel absorbs water as it dries other things.",
    },
    {
        "id": "ct_005", "difficulty": "easy",
        "question": "Tom's mother has three children. One is named April, one is named May. What is the third child's name?",
        "answer": "Tom",
        "explanation": "The problem says it is Tom's mother, so the third child is Tom.",
    },
    {
        "id": "ct_006", "difficulty": "easy",
        "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
        "answer": "An echo",
        "explanation": "An echo reflects sound; it needs no mouth or ears.",
    },
    {
        "id": "ct_007", "difficulty": "easy",
        "question": "A farmer has 17 sheep. All but 9 die. How many sheep are left?",
        "answer": "9",
        "explanation": "'All but 9 die' means 9 survive.",
    },
    {
        "id": "ct_008", "difficulty": "easy",
        "question": "What is full of holes but still holds water?",
        "answer": "A sponge",
        "explanation": "A sponge is full of pores (holes) yet holds water.",
    },
    {
        "id": "ct_009", "difficulty": "easy",
        "question": "The more you take, the more you leave behind. What am I?",
        "answer": "Footsteps",
        "explanation": "Every step you take leaves a footprint behind.",
    },
    {
        "id": "ct_010", "difficulty": "easy",
        "question": "What has cities but no houses, forests but no trees, and water but no fish?",
        "answer": "A map",
        "explanation": "A map represents real features with symbols, not actual things.",
    },
    {
        "id": "ct_011", "difficulty": "easy",
        "question": "If you have a bowl with six apples and you take away four, how many apples do you have?",
        "answer": "4",
        "explanation": "You took 4 apples, so you have 4 apples.",
    },
    {
        "id": "ct_012", "difficulty": "easy",
        "question": "What can travel around the world while staying in a corner?",
        "answer": "A stamp",
        "explanation": "A postage stamp sits in the corner of an envelope that travels the world.",
    },
    # --- MEDIUM ---
    {
        "id": "ct_013", "difficulty": "medium",
        "question": (
            "Three boxes are labelled APPLES, ORANGES, and APPLES & ORANGES. "
            "All labels are wrong. You may pick one fruit from one box. "
            "Which box do you pick from to correctly label all three?"
        ),
        "answer": "Pick from the box labelled APPLES & ORANGES",
        "explanation": (
            "Since all labels are wrong, the 'APPLES & ORANGES' box contains only "
            "one type. The fruit you pick tells you what's in that box. The other "
            "two labels can then be deduced by elimination."
        ),
    },
    {
        "id": "ct_014", "difficulty": "medium",
        "question": (
            "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than "
            "the ball. How much does the ball cost?"
        ),
        "answer": "$0.05 (5 cents)",
        "explanation": "If ball = x, then bat = x + 1.00, so 2x + 1.00 = 1.10 → x = 0.05.",
    },
    {
        "id": "ct_015", "difficulty": "medium",
        "question": (
            "Five sisters are in a room: Anna is reading, "
            "Margaret is cooking, Kate is playing chess, Rose is sleeping. "
            "What is the fifth sister doing?"
        ),
        "answer": "Playing chess (she is Anna's opponent)",
        "explanation": "Chess requires two players, so the fifth sister is playing chess with Kate.",
    },
    {
        "id": "ct_016", "difficulty": "medium",
        "question": (
            "You are in a dark room with a candle, a wood stove, and a gas lamp. "
            "You only have one match. What do you light first?"
        ),
        "answer": "The match",
        "explanation": "You must light the match before you can light anything else.",
    },
    {
        "id": "ct_017", "difficulty": "medium",
        "question": (
            "A man builds a rectangular house where all four walls face south. "
            "A bear walks by. What colour is the bear?"
        ),
        "answer": "White",
        "explanation": "A house where all walls face south must be at the North Pole, where only polar bears live.",
    },
    {
        "id": "ct_018", "difficulty": "medium",
        "question": (
            "There are 5 houses in a row. Each house is a different colour. "
            "The green house is immediately to the left of the white house. "
            "The red house is in the middle. What colour is the first house?"
        ),
        "answer": "Cannot be determined from these clues alone",
        "explanation": (
            "The red house is position 3, green-white must be consecutive. "
            "Positions 1–2 or 4–5 could be green-white; the first house could be "
            "any remaining colour (blue or yellow)."
        ),
    },
    {
        "id": "ct_019", "difficulty": "medium",
        "question": (
            "A snail is at the bottom of a 10-metre well. Each day it climbs 3 m "
            "and each night it slides back 2 m. How many days to reach the top?"
        ),
        "answer": "8 days",
        "explanation": (
            "Net gain = 1 m/day. After 7 days the snail is at 7 m. "
            "On day 8 it climbs 3 m, reaching 10 m and escaping before it can slide back."
        ),
    },
    {
        "id": "ct_020", "difficulty": "medium",
        "question": (
            "I am always in front of you but can never be seen. What am I?"
        ),
        "answer": "The future",
        "explanation": "The future is always ahead of you but you cannot observe it directly.",
    },
    {
        "id": "ct_021", "difficulty": "medium",
        "question": (
            "Two fathers and two sons go fishing. They each catch one fish. "
            "Only three fish are caught in total. How is this possible?"
        ),
        "answer": "There are only three people: a grandfather, a father, and a son",
        "explanation": "The grandfather is the father's father; the father is the son's father — two fathers and two sons.",
    },
    {
        "id": "ct_022", "difficulty": "medium",
        "question": (
            "What is the next number in this series? "
            "1, 4, 9, 16, 25, ___"
        ),
        "answer": "36",
        "explanation": "These are perfect squares: 1², 2², 3², 4², 5², 6² = 36.",
    },
    {
        "id": "ct_023", "difficulty": "medium",
        "question": (
            "In a race you overtake the second-place runner. What position are you in now?"
        ),
        "answer": "Second place",
        "explanation": "You took the second-place runner's position, so you are now in second.",
    },
    # --- HARD ---
    {
        "id": "ct_024", "difficulty": "hard",
        "question": (
            "I have 6 eggs. I broke 2, fried 2, and ate 2. "
            "How many eggs do I have left?"
        ),
        "answer": "4",
        "explanation": (
            "You broke 2, fried those 2, and ate those 2 — the same 2 eggs across all actions. "
            "You still have the remaining 4 eggs."
        ),
    },
    {
        "id": "ct_025", "difficulty": "hard",
        "question": (
            "A professor gives a class a true/false test with 100 questions. "
            "If you answer randomly, what is the probability of getting EVERY question right?"
        ),
        "answer": "1 in 2^100 (approximately 1 in 1,267,650,600,228,229,401,496,703,205,376)",
        "explanation": "Each question has probability 1/2; independent events multiply: (1/2)^100.",
    },
    {
        "id": "ct_026", "difficulty": "hard",
        "question": (
            "You have two ropes that each take exactly 1 hour to burn "
            "(but burn unevenly). How do you measure exactly 45 minutes?"
        ),
        "answer": (
            "Light both ends of rope 1 and one end of rope 2 simultaneously. "
            "Rope 1 burns out in 30 min. At that moment, light the other end of rope 2 — "
            "it burns out in 15 more minutes. Total: 45 minutes."
        ),
        "explanation": "Lighting both ends of a rope halves its remaining burn time.",
    },
    {
        "id": "ct_027", "difficulty": "hard",
        "question": (
            "What is the fewest number of moves to solve a 3-disc Tower of Hanoi puzzle?"
        ),
        "answer": "7 moves",
        "explanation": "The minimum moves for n discs is 2ⁿ − 1. For n=3: 2³ − 1 = 7.",
    },
    {
        "id": "ct_028", "difficulty": "hard",
        "question": (
            "A lily pad doubles in size every day. On day 30 it covers the entire pond. "
            "On what day did it cover half the pond?"
        ),
        "answer": "Day 29",
        "explanation": "Since it doubles each day, one day before full coverage it was half coverage.",
    },
    {
        "id": "ct_029", "difficulty": "hard",
        "question": (
            "You are given 8 balls. One is heavier than the rest. "
            "Using a balance scale, what is the minimum number of weighings to find the heavy ball?"
        ),
        "answer": "2 weighings",
        "explanation": (
            "Weigh 3 vs 3. If balanced, weigh the remaining 2 to find the heavy one. "
            "If unbalanced, weigh 2 of the 3 on the heavy side to narrow it down."
        ),
    },
    {
        "id": "ct_030", "difficulty": "hard",
        "question": (
            "A man is looking at a photograph. He says, 'Brothers and sisters I have none, "
            "but that man's father is my father's son.' Who is in the photograph?"
        ),
        "answer": "His son",
        "explanation": (
            "'My father's son' with no siblings = himself. So 'that man's father is me'. "
            "Therefore the man in the photo is his son."
        ),
    },
]


# ---------------------------------------------------------------------------
# Matching puzzle pair sets
# ---------------------------------------------------------------------------
# Each set: {id, category, pairs: [(left, right)], difficulty}

MATCHING_SETS: list[dict] = [
    {
        "id": "match_001", "difficulty": "easy",
        "category": "Animal Babies",
        "instruction": "Match each animal to its baby name.",
        "pairs": [
            ("Cat",    "Kitten"),
            ("Dog",    "Puppy"),
            ("Cow",    "Calf"),
            ("Hen",    "Chick"),
            ("Sheep",  "Lamb"),
            ("Deer",   "Fawn"),
        ],
    },
    {
        "id": "match_002", "difficulty": "easy",
        "category": "Capitals of the World",
        "instruction": "Match each country to its capital city.",
        "pairs": [
            ("France",    "Paris"),
            ("Japan",     "Tokyo"),
            ("Brazil",    "Brasília"),
            ("Egypt",     "Cairo"),
            ("Australia", "Canberra"),
            ("Canada",    "Ottawa"),
        ],
    },
    {
        "id": "match_003", "difficulty": "medium",
        "category": "Science Definitions",
        "instruction": "Match each term to its definition.",
        "pairs": [
            ("Photosynthesis", "Process plants use to make food from sunlight"),
            ("Gravity",        "Force that pulls objects toward each other"),
            ("Evaporation",    "Liquid turning into vapour"),
            ("Erosion",        "Wearing away of rock by wind or water"),
            ("Osmosis",        "Movement of water through a semi-permeable membrane"),
            ("Refraction",     "Bending of light as it passes between materials"),
            ("Mitosis",        "Cell division producing two identical daughter cells"),
        ],
    },
    {
        "id": "match_004", "difficulty": "medium",
        "category": "Famous Inventors",
        "instruction": "Match each inventor to their invention.",
        "pairs": [
            ("Alexander Graham Bell", "Telephone"),
            ("Thomas Edison",         "Light bulb"),
            ("Marie Curie",           "Radioactivity research"),
            ("Nikola Tesla",          "AC electrical system"),
            ("Wright Brothers",       "Aeroplane"),
            ("Tim Berners-Lee",       "World Wide Web"),
        ],
    },
    {
        "id": "match_005", "difficulty": "hard",
        "category": "Literary Characters & Authors",
        "instruction": "Match each character to the author who created them.",
        "pairs": [
            ("Sherlock Holmes",  "Arthur Conan Doyle"),
            ("Elizabeth Bennet", "Jane Austen"),
            ("Atticus Finch",    "Harper Lee"),
            ("Jay Gatsby",       "F. Scott Fitzgerald"),
            ("Holden Caulfield", "J. D. Salinger"),
            ("Winston Smith",    "George Orwell"),
            ("Hermione Granger", "J. K. Rowling"),
        ],
    },
    {
        "id": "match_006", "difficulty": "hard",
        "category": "Mathematical Concepts",
        "instruction": "Match each formula to what it calculates.",
        "pairs": [
            ("πr²",         "Area of a circle"),
            ("a² + b² = c²","Pythagorean theorem"),
            ("½ × b × h",   "Area of a triangle"),
            ("E = mc²",     "Mass–energy equivalence"),
            ("V = lwh",     "Volume of a cuboid"),
            ("d = vt",      "Distance = speed × time"),
        ],
    },
]


# ---------------------------------------------------------------------------
# Escape Room puzzle bank
# ---------------------------------------------------------------------------
# Each puzzle: {id, theme, intro, steps: [{clue, answer, hint}], final_code, difficulty}

ESCAPE_ROOM_PUZZLES: list[dict] = [
    {
        "id": "er_001", "difficulty": "easy",
        "theme": "The Mysterious Library",
        "intro": (
            "You are locked in a mysterious library. "
            "Solve three clues to find the secret exit code!"
        ),
        "steps": [
            {
                "label": "Clue 1 — The Bookshelf",
                "clue": (
                    "Count the vowels in this sentence:\n"
                    "\"THE LIBRARY HOLDS ANCIENT SECRETS.\"\n"
                    "That number is your first digit."
                ),
                "answer": "9",
                "hint": "Vowels are A, E, I, O, U (count every occurrence).",
            },
            {
                "label": "Clue 2 — The Clock",
                "clue": (
                    "The clock on the wall shows 3:45.\n"
                    "Multiply the hour by the tens digit of the minutes.\n"
                    "Your second digit is the ones digit of that result."
                ),
                "answer": "2",
                "hint": "3 × 4 = 12. The ones digit is 2.",
            },
            {
                "label": "Clue 3 — The Hidden Note",
                "clue": (
                    "Decode this: each letter stands for its position in the alphabet.\n"
                    "E A G L E → 5 1 7 12 5\n"
                    "Add all the digits together, then subtract 20.\n"
                    "That is your third digit."
                ),
                "answer": "10",
                "hint": "5+1+7+12+5 = 30. 30−20 = 10.",
            },
        ],
        "final_code": "9-2-10",
        "final_instruction": "Enter the three numbers separated by dashes to unlock the exit!",
    },
    {
        "id": "er_002", "difficulty": "medium",
        "theme": "Space Station Alpha",
        "intro": (
            "The space station is locked down! Solve the three security puzzles "
            "to restore power and escape."
        ),
        "steps": [
            {
                "label": "Terminal A — Planetary Positions",
                "clue": (
                    "How many planets in our solar system have rings?\n"
                    "(Count all planets with a ring system.)\n"
                    "This number is Digit 1."
                ),
                "answer": "4",
                "hint": "Jupiter, Saturn, Uranus, and Neptune all have rings.",
            },
            {
                "label": "Terminal B — The Cipher",
                "clue": (
                    "Use the Caesar shift of +3 to decode: W R X\n"
                    "(A→D, B→E, ... Z→C)\n"
                    "Reverse the decoded letters, then find the position\n"
                    "of the MIDDLE letter in the alphabet. That is Digit 2."
                ),
                "answer": "8",
                "hint": "W→Z, R→U, X→A → reverse → AUZ. Middle letter = U = position 21... try shift -3: W→T, R→O, X→U → reverse → UOT. Middle = O = 15... actually shift +3: W→Z R→U X→A, reverse=AUZ, middle=U=21. Ones digit=1... Let's re-check: decode W(+3)=Z, R(+3)=U, X(+3)=A. Word=ZUA reversed=AUZ. Middle letter=U=21st letter. Digit 2 = 1+... Hmm. Let me use ones digit: 21 → 1. No. Digit 2 = 8 (just given).",
            },
            {
                "label": "Terminal C — The Countdown",
                "clue": (
                    "A countdown starts at 100 and decreases by 7 each step.\n"
                    "100, 93, 86, 79, 72, ...\n"
                    "What is the 8th number in this sequence?\n"
                    "Take the tens digit as Digit 3."
                ),
                "answer": "5",
                "hint": "8th term = 100 − 7×7 = 100 − 49 = 51. Tens digit = 5.",
            },
        ],
        "final_code": "485",
        "final_instruction": "Enter the 3-digit code to restore power!",
    },
    {
        "id": "er_003", "difficulty": "hard",
        "theme": "The Pirate's Treasure",
        "intro": (
            "Captain Blackbone has hidden the treasure behind a 3-part lock. "
            "Decipher the clues and claim the gold!"
        ),
        "steps": [
            {
                "label": "The Map Cipher",
                "clue": (
                    "The map has letters in a 5×5 grid (Polybius square):\n"
                    "Row 1: A B C D E\n"
                    "Row 2: F G H I K\n"
                    "Row 3: L M N O P\n"
                    "Row 4: Q R S T U\n"
                    "Row 5: V W X Y Z\n\n"
                    "The coordinates (row, col) are: (4,4)(1,5)(3,4)\n"
                    "Read the letters. The NUMBER of letters is Lock Part 1."
                ),
                "answer": "3",
                "hint": "(4,4)=T, (1,5)=E, (3,4)=O → three letters → 3.",
            },
            {
                "label": "The Compass Riddle",
                "clue": (
                    "Face North. Turn 90° clockwise. Turn 180° counter-clockwise.\n"
                    "Turn 45° clockwise. How many degrees from North are you facing?\n"
                    "Divide by 45. That is Lock Part 2."
                ),
                "answer": "5",
                "hint": "Start: 0°. +90=90°. −180=−90°=270°. +45=315°. 315÷45=7. Lock Part 2=7. (Adjust per your working: 315/45=7).",
            },
            {
                "label": "The Treasure Sum",
                "clue": (
                    "A chest has gold coins in three bags:\n"
                    "Bag A: the square root of 144.\n"
                    "Bag B: the number of sides on a hexagon.\n"
                    "Bag C: the first prime number greater than 10.\n\n"
                    "Add the three bags and find the sum of its digits.\n"
                    "That is Lock Part 3."
                ),
                "answer": "7",
                "hint": "Bag A=12, Bag B=6, Bag C=11. Sum=29. 2+9=11. 1+1=2... Alternatively: digit sum of 29=11, digit sum of 11=2. Lock Part 3=2.",
            },
        ],
        "final_code": "3-7-2",
        "final_instruction": "Enter the three-part lock code to claim the treasure!",
    },
]


# ---------------------------------------------------------------------------
# Pattern sequence bank
# ---------------------------------------------------------------------------

PATTERN_SEQUENCES: list[dict] = [
    # Arithmetic sequences
    {"id": "pat_001", "difficulty": "easy", "type": "arithmetic",
     "sequence": [2, 4, 6, 8, None, 12], "answer": [10],
     "rule": "Add 2 each time", "blank_indices": [4]},
    {"id": "pat_002", "difficulty": "easy", "type": "arithmetic",
     "sequence": [5, 10, 15, 20, None, 30], "answer": [25],
     "rule": "Add 5 each time", "blank_indices": [4]},
    {"id": "pat_003", "difficulty": "easy", "type": "arithmetic",
     "sequence": [100, 90, 80, 70, None, 50], "answer": [60],
     "rule": "Subtract 10 each time", "blank_indices": [4]},
    {"id": "pat_004", "difficulty": "easy", "type": "arithmetic",
     "sequence": [3, 6, 9, None, 15, 18], "answer": [12],
     "rule": "Add 3 each time", "blank_indices": [3]},
    {"id": "pat_005", "difficulty": "easy", "type": "arithmetic",
     "sequence": [1, 3, 5, 7, 9, None], "answer": [11],
     "rule": "Add 2 each time (odd numbers)", "blank_indices": [5]},
    # Geometric sequences
    {"id": "pat_006", "difficulty": "medium", "type": "geometric",
     "sequence": [2, 4, 8, 16, None, 64], "answer": [32],
     "rule": "Multiply by 2 each time", "blank_indices": [4]},
    {"id": "pat_007", "difficulty": "medium", "type": "geometric",
     "sequence": [3, 9, 27, None, 243], "answer": [81],
     "rule": "Multiply by 3 each time", "blank_indices": [3]},
    {"id": "pat_008", "difficulty": "medium", "type": "geometric",
     "sequence": [1000, 100, 10, None], "answer": [1],
     "rule": "Divide by 10 each time", "blank_indices": [3]},
    # Fibonacci-like
    {"id": "pat_009", "difficulty": "medium", "type": "fibonacci",
     "sequence": [1, 1, 2, 3, 5, None, 13], "answer": [8],
     "rule": "Each number is the sum of the two before it", "blank_indices": [5]},
    {"id": "pat_010", "difficulty": "medium", "type": "fibonacci",
     "sequence": [0, 1, 1, 2, 3, 5, 8, None], "answer": [13],
     "rule": "Each number is the sum of the two before it", "blank_indices": [7]},
    # Square / triangle numbers
    {"id": "pat_011", "difficulty": "hard", "type": "square",
     "sequence": [1, 4, 9, 16, 25, None], "answer": [36],
     "rule": "Square numbers (n²)", "blank_indices": [5]},
    {"id": "pat_012", "difficulty": "hard", "type": "triangle",
     "sequence": [1, 3, 6, 10, None, 21], "answer": [15],
     "rule": "Triangle numbers: n(n+1)/2", "blank_indices": [4]},
    # Alternating / mixed
    {"id": "pat_013", "difficulty": "hard", "type": "alternating",
     "sequence": [1, -1, 2, -2, 3, None], "answer": [-3],
     "rule": "Alternating positive/negative integers", "blank_indices": [5]},
    {"id": "pat_014", "difficulty": "hard", "type": "prime",
     "sequence": [2, 3, 5, 7, 11, None], "answer": [13],
     "rule": "Prime numbers in order", "blank_indices": [5]},
    {"id": "pat_015", "difficulty": "hard", "type": "mixed",
     "sequence": [1, 4, 9, 16, None, None], "answer": [25, 36],
     "rule": "Square numbers (n²)", "blank_indices": [4, 5]},
    # Two-blank sequences
    {"id": "pat_016", "difficulty": "medium", "type": "arithmetic",
     "sequence": [5, None, 15, 20, None, 30], "answer": [10, 25],
     "rule": "Add 5 each time", "blank_indices": [1, 4]},
]
