"""
models.py — SocraticTeach-Env
Data models, quiz bank, student simulator, and reward logic.
"""

from dataclasses import dataclass, field
from typing import Optional
import random

# Try to import from openenv, fall back to mock
try:
    from openenv.core import Action, Observation
except ImportError:
    from .mock_openenv import Action, Observation


class TeacherAction(Action):
    """The action produced by the teacher agent each turn."""
    teacher_message: str


class SocraticObservation(Observation):
    """Full observation returned by reset() and step()."""
    topic: str
    difficulty: str
    student_response: str
    confusion_score: float          # 0.0 – 1.0
    turn_number: int                # 1 – 10
    pre_quiz_score: int             # 0 – 5
    post_quiz_score: int            # 0 until episode ends
    misconception: str
    misconception_resolved: bool
    feedback: str
    reward: float
    done: bool


# ---------------------------------------------------------------------------
# Topic / Misconception registry
# ---------------------------------------------------------------------------

TOPICS = {
    "easy": [
        {
            "topic": "loops in Python",
            "misconception": "a while loop always runs forever",
        },
        {
            "topic": "lists in Python",
            "misconception": "lists can only store numbers",
        },
        {
            "topic": "functions in Python",
            "misconception": "a function runs automatically when defined",
        },
    ],
    "medium": [
        {
            "topic": "recursion in Python",
            "misconception": "recursion always causes infinite loops",
        },
        {
            "topic": "sorting algorithms",
            "misconception": "bubble sort is always the fastest",
        },
        {
            "topic": "binary search",
            "misconception": "binary search works on unsorted lists",
        },
    ],
    "hard": [
        {
            "topic": "trees in CS",
            "misconception": "a binary tree must always be balanced",
        },
        {
            "topic": "time complexity",
            "misconception": "O(n^2) is always slower than O(n log n) for all inputs",
        },
        {
            "topic": "dynamic programming",
            "misconception": "dynamic programming is just recursion with loops",
        },
    ],
}

# Guiding questions needed per difficulty before misconception resolves
GUIDING_THRESHOLD = {"easy": 3, "medium": 5, "hard": 7}

# ---------------------------------------------------------------------------
# Quiz bank — 5 MCQ per topic
# Each question: {"q": str, "options": [str, str, str, str], "answer": int (0-based)}
# ---------------------------------------------------------------------------

QUIZ_BANK: dict[str, list[dict]] = {
    # ---- easy ---------------------------------------------------------------
    "loops in Python": [
        {
            "q": "What controls when a while loop stops?",
            "options": [
                "The loop condition becoming False",
                "Python's built-in timer",
                "The number of lines in the loop body",
                "It never stops",
            ],
            "answer": 0,
        },
        {
            "q": "Which keyword exits a loop immediately?",
            "options": ["continue", "pass", "break", "exit"],
            "answer": 2,
        },
        {
            "q": "How many times does `for i in range(3)` iterate?",
            "options": ["2", "3", "4", "Infinite"],
            "answer": 1,
        },
        {
            "q": "A while loop with `while False:` runs how many times?",
            "options": ["Once", "Twice", "Zero times", "Forever"],
            "answer": 2,
        },
        {
            "q": "What happens if the while-loop condition is always True and there's no break?",
            "options": [
                "It runs once then stops",
                "Python raises a SyntaxError",
                "It loops forever (infinite loop)",
                "It skips the body",
            ],
            "answer": 2,
        },
    ],
    "lists in Python": [
        {
            "q": "Which of the following can be stored in a Python list?",
            "options": ["Only integers", "Only strings", "Any data type", "Only floats"],
            "answer": 2,
        },
        {
            "q": "What does `my_list.append('hello')` do?",
            "options": [
                "Raises a TypeError because lists hold numbers only",
                "Adds 'hello' to the end of the list",
                "Replaces all elements with 'hello'",
                "Removes 'hello' from the list",
            ],
            "answer": 1,
        },
        {
            "q": "Can a Python list contain other lists?",
            "options": ["No, lists are flat", "Yes, lists can be nested", "Only if they are the same length", "Only in Python 3.10+"],
            "answer": 1,
        },
        {
            "q": "What is the type of `x` after `x = [1, 'two', 3.0]`?",
            "options": ["int", "str", "list", "tuple"],
            "answer": 2,
        },
        {
            "q": "How do you access the first element of `lst`?",
            "options": ["lst[1]", "lst[-1]", "lst[0]", "lst.first()"],
            "answer": 2,
        },
    ],
    "functions in Python": [
        {
            "q": "When does a function's body execute?",
            "options": [
                "When it is defined with `def`",
                "When it is called with parentheses",
                "When the script is imported",
                "Automatically every second",
            ],
            "answer": 1,
        },
        {
            "q": "What does a `return` statement do?",
            "options": [
                "Defines the function",
                "Calls the function again",
                "Exits the function and optionally returns a value",
                "Prints output",
            ],
            "answer": 2,
        },
        {
            "q": "Which is the correct way to call `greet()`?",
            "options": ["def greet()", "greet", "call greet()", "greet()"],
            "answer": 3,
        },
        {
            "q": "Can a function be defined but never called?",
            "options": [
                "No, Python calls it automatically",
                "Yes, it simply won't execute",
                "No, it raises a NameError",
                "Only if it has no parameters",
            ],
            "answer": 1,
        },
        {
            "q": "What is a parameter in a function?",
            "options": [
                "The name of the function",
                "A variable in the function definition that receives an argument",
                "The return value",
                "A global variable",
            ],
            "answer": 1,
        },
    ],
    # ---- medium -------------------------------------------------------------
    "recursion in Python": [
        {
            "q": "What prevents a recursive function from running forever?",
            "options": [
                "Python's garbage collector",
                "A base case that stops the recursion",
                "The `global` keyword",
                "Using a while loop inside it",
            ],
            "answer": 1,
        },
        {
            "q": "What is the base case in `factorial(n)`?",
            "options": [
                "When n equals 10",
                "When n is negative",
                "When n equals 0 or 1",
                "When n is even",
            ],
            "answer": 2,
        },
        {
            "q": "Recursion always causes infinite loops — this statement is:",
            "options": ["True", "False; a base case terminates it", "True for Python only", "Depends on the OS"],
            "answer": 1,
        },
        {
            "q": "What error does Python raise when recursion depth is exceeded?",
            "options": ["IndexError", "ValueError", "RecursionError", "MemoryError"],
            "answer": 2,
        },
        {
            "q": "Which problem is naturally suited for recursion?",
            "options": ["Adding two numbers", "Traversing a binary tree", "Sorting with bubble sort", "Reading a file"],
            "answer": 1,
        },
    ],
    "sorting algorithms": [
        {
            "q": "What is the average time complexity of bubble sort?",
            "options": ["O(n)", "O(n log n)", "O(n^2)", "O(1)"],
            "answer": 2,
        },
        {
            "q": "Which sort has O(n log n) average complexity?",
            "options": ["Bubble sort", "Selection sort", "Merge sort", "Insertion sort"],
            "answer": 2,
        },
        {
            "q": "When can bubble sort be faster than merge sort in practice?",
            "options": [
                "Never",
                "For very large arrays",
                "For nearly-sorted small arrays",
                "When data is random",
            ],
            "answer": 2,
        },
        {
            "q": "Bubble sort is always the fastest — this is:",
            "options": [
                "True",
                "False; merge/quick sort are faster for large inputs",
                "True for Python only",
                "True when n < 5",
            ],
            "answer": 1,
        },
        {
            "q": "What does bubble sort do in each pass?",
            "options": [
                "Splits the array in half",
                "Finds the minimum element",
                "Swaps adjacent elements that are out of order",
                "Builds a sorted subtree",
            ],
            "answer": 2,
        },
    ],
    "binary search": [
        {
            "q": "What prerequisite must a list meet for binary search?",
            "options": [
                "It must contain only integers",
                "It must be sorted",
                "It must have an even number of elements",
                "It must be stored in a dict",
            ],
            "answer": 1,
        },
        {
            "q": "What is the time complexity of binary search?",
            "options": ["O(n)", "O(n^2)", "O(log n)", "O(1)"],
            "answer": 2,
        },
        {
            "q": "Binary search works on unsorted lists — this is:",
            "options": [
                "True",
                "False; it requires a sorted list",
                "True if the list is short",
                "Depends on the language",
            ],
            "answer": 1,
        },
        {
            "q": "In each step, binary search eliminates approximately how much of the remaining search space?",
            "options": ["One element", "A quarter", "Half", "All of it"],
            "answer": 2,
        },
        {
            "q": "How many comparisons does binary search need in the worst case for 1024 elements?",
            "options": ["1024", "512", "10", "1"],
            "answer": 2,
        },
    ],
    # ---- hard ---------------------------------------------------------------
    "trees in CS": [
        {
            "q": "A binary tree MUST always be balanced — this is:",
            "options": [
                "True",
                "False; trees can be unbalanced",
                "True only for BSTs",
                "True only in Python",
            ],
            "answer": 1,
        },
        {
            "q": "In a balanced BST, search is:",
            "options": ["O(n)", "O(n^2)", "O(log n)", "O(1)"],
            "answer": 2,
        },
        {
            "q": "A degenerate (skewed) binary tree has search complexity of:",
            "options": ["O(log n)", "O(n)", "O(1)", "O(n log n)"],
            "answer": 1,
        },
        {
            "q": "Which tree type self-balances?",
            "options": ["Simple BST", "AVL tree", "Degenerate tree", "Min-heap"],
            "answer": 1,
        },
        {
            "q": "How many children can a binary tree node have at most?",
            "options": ["1", "2", "3", "Unlimited"],
            "answer": 1,
        },
    ],
    "time complexity": [
        {
            "q": "For n=5, which is larger: n^2 or n log n (base 2)?",
            "options": [
                "n log n (≈11.6) > n^2 (25) — False; n^2 is larger",
                "n^2 = 25 > n log n ≈ 11.6",
                "They are equal",
                "Cannot be compared",
            ],
            "answer": 1,
        },
        {
            "q": "For very small n (e.g. n=2), which may actually run faster in practice?",
            "options": [
                "O(n log n) algorithm always",
                "O(n^2) algorithm due to low constants",
                "They are always identical",
                "Neither can run",
            ],
            "answer": 1,
        },
        {
            "q": "Big-O describes how runtime grows — it ignores:",
            "options": [
                "The algorithm's correctness",
                "Constant factors and lower-order terms",
                "The programming language",
                "All of the above",
            ],
            "answer": 1,
        },
        {
            "q": "O(n^2) is ALWAYS slower than O(n log n) for ALL inputs — this is:",
            "options": [
                "True",
                "False; for very small n, constants matter",
                "True only for sorting",
                "True in Python only",
            ],
            "answer": 1,
        },
        {
            "q": "Which factor does Big-O NOT capture?",
            "options": [
                "Growth rate",
                "Worst-case behaviour",
                "Cache effects and hardware constants",
                "Asymptotic bounds",
            ],
            "answer": 2,
        },
    ],
    "dynamic programming": [
        {
            "q": "The key idea of dynamic programming is:",
            "options": [
                "Using recursion with loops",
                "Memoising overlapping subproblems to avoid recomputation",
                "Dividing the array in half repeatedly",
                "Using dynamic typing",
            ],
            "answer": 1,
        },
        {
            "q": "Dynamic programming requires which two properties?",
            "options": [
                "Sorting and searching",
                "Optimal substructure and overlapping subproblems",
                "Recursion and loops",
                "Greedy choice and backtracking",
            ],
            "answer": 1,
        },
        {
            "q": "Memoisation means:",
            "options": [
                "Writing comments in code",
                "Caching results of expensive function calls",
                "Using memory-mapped files",
                "Memorising the algorithm",
            ],
            "answer": 1,
        },
        {
            "q": "DP is just recursion with loops — this is:",
            "options": [
                "True",
                "False; DP specifically exploits overlapping subproblems via memoisation/tabulation",
                "True for iterative DP only",
                "True for top-down DP only",
            ],
            "answer": 1,
        },
        {
            "q": "Which classic problem is solved with DP?",
            "options": [
                "Binary search",
                "Fibonacci sequence (with memoisation)",
                "Bubble sort",
                "DFS traversal",
            ],
            "answer": 1,
        },
    ],
}


# ---------------------------------------------------------------------------
# Student simulator
# ---------------------------------------------------------------------------

# Words that indicate the teacher is guiding rather than telling
GUIDING_WORDS = [
    "why", "what if", "consider", "think about", "what happens when",
    "how would", "can you", "imagine", "suppose", "what do you",
    "have you", "does that", "could you", "what might", "how might",
]

# Phrases that indicate the teacher is directly stating the answer (anti-cheat)
DIRECT_ANSWER_PHRASES = [
    "the answer is", "it means", "recursion is", "the solution is",
    "you should know", "the correct answer", "the definition is",
    "it is defined as", "it simply means", "to summarise,",
]

# Student response templates
_STUDENT_RESPONSES = {
    "confused_start": [
        "I'm not sure… {misconception}.",
        "Well, I think {misconception}. Is that right?",
        "I guess {misconception}? Not really confident.",
    ],
    "partial": [
        "Hmm, maybe I was wrong about that. Let me think…",
        "That's an interesting way to look at it. I think I'm starting to get it.",
        "So maybe {misconception} isn't always true?",
    ],
    "direct_told": [
        "Oh okay, got it.",
        "I see, thanks.",
        "Oh, alright then.",
    ],
    "resolved": [
        "Oh! I think I understand now. {misconception} isn't always correct.",
        "That makes sense! So the misconception I had was wrong.",
        "I get it now. I was wrong to think {misconception}.",
    ],
    "hard_confident_wrong": [
        "I'm actually quite sure that {misconception}. I've read about this.",
        "With respect, I believe {misconception} — it's well established.",
        "I disagree — {misconception} is definitely true from what I know.",
    ],
}


def _pick(templates: list[str], misconception: str) -> str:
    t = random.choice(templates)
    return t.replace("{misconception}", misconception)


def simulate_student(
    teacher_message: str,
    misconception: str,
    confusion_score: float,
    turn_number: int,
    difficulty: str,
    guiding_count: int,
    misconception_resolved: bool,
) -> tuple[str, float, bool, bool, int]:
    """
    Rule-based student simulator.

    Returns:
        student_response: str
        new_confusion_score: float
        new_misconception_resolved: bool
        gave_direct_answer: bool  (True if teacher cheated)
        new_guiding_count: int
    """
    msg_lower = teacher_message.lower()

    gave_direct_answer = any(p in msg_lower for p in DIRECT_ANSWER_PHRASES)
    is_guiding = any(w in msg_lower for w in GUIDING_WORDS)

    new_confusion = confusion_score
    new_resolved = misconception_resolved
    new_guiding_count = guiding_count

    if gave_direct_answer:
        # Anti-cheat: student says "ok" but misconception NOT resolved
        response = _pick(_STUDENT_RESPONSES["direct_told"], misconception)
        return response, new_confusion, False, True, new_guiding_count

    if is_guiding and not misconception_resolved:
        new_confusion = max(0.0, confusion_score - 0.1)
        new_guiding_count += 1
        threshold = GUIDING_THRESHOLD[difficulty]

        if new_guiding_count >= threshold and turn_number > 4:
            # Misconception resolved
            new_resolved = True
            response = _pick(_STUDENT_RESPONSES["resolved"], misconception)
        elif difficulty == "hard" and turn_number <= 4:
            # Hard mode: confidently wrong early on
            response = _pick(_STUDENT_RESPONSES["hard_confident_wrong"], misconception)
        else:
            response = _pick(_STUDENT_RESPONSES["partial"], misconception)
    else:
        # No guiding word, not resolved — student stays confused
        if difficulty == "hard" and not misconception_resolved and turn_number <= 5:
            response = _pick(_STUDENT_RESPONSES["hard_confident_wrong"], misconception)
        else:
            response = _pick(_STUDENT_RESPONSES["confused_start"], misconception)

    return response, new_confusion, new_resolved, False, new_guiding_count


# ---------------------------------------------------------------------------
# Quiz logic
# ---------------------------------------------------------------------------

def run_quiz(topic: str, random_seed: int | None = None) -> tuple[int, list[dict]]:
    """
    Run a quiz for the given topic.
    Returns (score 0-5, list of question dicts used).
    This is the *initial* call — student starts with 1-2 correct.
    """
    if random_seed is not None:
        random.seed(random_seed)
    questions = QUIZ_BANK.get(topic, [])
    # Student starts knowing 1-2 answers (pre-quiz)
    correct_count = random.randint(1, 2)
    return correct_count, questions


def run_post_quiz(topic: str, misconception_resolved: bool, pre_score: int) -> int:
    """
    Simulate post-quiz improvement.
    If misconception resolved → score improves by 2-3 points (capped at 5).
    Otherwise → improves by 0-1 point.
    """
    if misconception_resolved:
        delta = random.randint(2, 3)
    else:
        delta = random.randint(0, 1)
    return min(5, pre_score + delta)


# ---------------------------------------------------------------------------
# Reward formula
# ---------------------------------------------------------------------------

def compute_reward(
    pre_quiz_score: int,
    post_quiz_score: int,
    misconception_resolved: bool,
    turn_number: int,
    confusion_decreased: bool,
    gave_direct_answer: bool,
    done: bool,
) -> float:
    if not done:
        r = 0.05 if confusion_decreased else 0.0
        if gave_direct_answer:
            r -= 0.1
        return round(r, 4)

    quiz_delta = (post_quiz_score - pre_quiz_score) / 5.0
    misconception_bonus = 0.15 if misconception_resolved else 0.0
    efficiency_penalty = (turn_number / 10) * 0.05
    teaching_quality = 0.25 if (misconception_resolved and turn_number < 8) else 0.10
    final = (quiz_delta * 0.45) + misconception_bonus + teaching_quality - efficiency_penalty
    return round(final, 4)