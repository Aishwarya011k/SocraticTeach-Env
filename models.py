"""
SocraticTeach-Env: OpenEnv Models
Defines Observation, Action, and Quiz structures for the Socratic teaching environment.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field
from openenv.core import Observation as BaseObservation, Action as BaseAction


class Action(BaseAction):
    """Teacher action: send a message to the student"""
    teacher_message: str

    def to_dict(self):
        return {"teacher_message": self.teacher_message}


class Observation(BaseObservation):
    """Student observation state at each step"""
    topic: str
    difficulty: str
    student_response: str
    confusion_score: float
    turn_number: int
    pre_quiz_score: int
    post_quiz_score: int
    misconception: str
    misconception_resolved: bool
    feedback: str
    reward: float = 0.0
    done: bool = False

    def to_dict(self):
        return self.model_dump()


# QUIZ DATABASE - Hardcoded MCQ questions for each topic
QUIZ_DATABASE: Dict[str, List[Dict]] = {
    "loops in Python": [
        {
            "question": "What does this code print? `i = 0; while i < 3: print(i); i += 1`",
            "options": ["0 1 2", "infinite output", "nothing", "error"],
            "correct_idx": 0
        },
        {
            "question": "Can a while loop have a condition that becomes false?",
            "options": ["Yes, if the condition changes", "No, it always runs forever",
                        "Only in Python 4+", "Never in practice"],
            "correct_idx": 0
        },
        {
            "question": "Which loop will terminate? `while True: break` or `while 1: pass`?",
            "options": ["First one terminates", "Second one terminates", "Both infinite",
                        "Neither is valid"],
            "correct_idx": 0
        },
        {
            "question": "What is the condition called in `while condition:`?",
            "options": ["Loop body", "Boolean expression", "Counter", "Iterator"],
            "correct_idx": 1
        },
        {
            "question": "If a while loop's condition is false initially, how many times does the body run?",
            "options": ["0 times", "1 time", "Infinite times", "Depends on Python version"],
            "correct_idx": 0
        }
    ],
    "lists in Python": [
        {
            "question": "Can a Python list contain both numbers and strings?",
            "options": ["Yes, any data types can mix",
                        "No, only one type per list",
                        "Only numbers and strings together",
                        "Only in Python 2"],
            "correct_idx": 0
        },
        {
            "question": "What does `my_list = [1, 'hello', 3.14]` create?",
            "options": ["Error", "A mixed-type list with 3 elements", "A list of strings",
                        "Only numbers are stored"],
            "correct_idx": 1
        },
        {
            "question": "Which is a valid Python list?",
            "options": ["[1, 2, 3]", "['a', 'b', 'c']", "[True, 42, 'mix']", "All are valid"],
            "correct_idx": 3
        },
        {
            "question": "What can lists store?",
            "options": ["Only integers", "Only strings",
                        "Any Python object: numbers, strings, objects, etc.",
                        "Lists cannot store anything"],
            "correct_idx": 2
        },
        {
            "question": "Is `[1, 'x', None, [2, 3]]` a valid Python list?",
            "options": ["Yes, lists can be nested and mixed",
                        "No, too many types",
                        "Only if sorted",
                        "No, invalid syntax"],
            "correct_idx": 0
        }
    ],
    "functions in Python": [
        {
            "question": "What happens when you define a function with `def my_func():`?",
            "options": ["It runs immediately", "It does nothing until called",
                        "It prints 'Function defined'", "It must be called inside another function"],
            "correct_idx": 1
        },
        {
            "question": "Which statement is true? `def greet(): pass`",
            "options": ["greet runs automatically", "You must call greet() to run it",
                        "greet runs once per one per import", "greet is defined but always fails"],
            "correct_idx": 1
        },
        {
            "question": "How do you execute a function named `calculate`?",
            "options": ["Just write 'calculate'",
                        "Write 'calculate()'",
                        "Write 'run calculate'",
                        "Write 'def calculate'"],
            "correct_idx": 1
        },
        {
            "question": "Can you call a function multiple times?",
            "options": ["No, only once", "Yes, many times", "Only if recreated each time",
                        "Only within the same module"],
            "correct_idx": 1
        },
        {
            "question": "What must you do to execute a function after defining it?",
            "options": ["Nothing, it auto-runs", "Call it with parentheses",
                        "Import it", "Redefine it"],
            "correct_idx": 1
        }
    ],
    "recursion in Python": [
        {
            "question": "What is the main reason we use a base case in recursion?",
            "options": ["To speed up the code", "To prevent infinite recursion",
                        "To make the code run forever", "It is optional"],
            "correct_idx": 1
        },
        {
            "question": "Does `def fact(n): return n * fact(n-1) if n > 1 else 1` always recurse forever?",
            "options": ["Yes, always infinite",
                        "No, it has a base case (n=1) that stops it",
                        "Only if n is negative",
                        "Recursion always causes infinite loops"],
            "correct_idx": 1
        },
        {
            "question": "What prevents recursion from being infinite?",
            "options": ["Nothing, recursion is always infinite", "A base case",
                        "The language itself", "Calling return"],
            "correct_idx": 1
        },
        {
            "question": "Can a recursive function be faster than a loop?",
            "options": ["Never", "Sometimes, with optimization",
                        "Always", "Only in Python"],
            "correct_idx": 1
        },
        {
            "question": "What is a base case in recursion?",
            "options": ["The recursive call", "The condition that stops recursion",
                        "The function name", "None of the above"],
            "correct_idx": 1
        }
    ],
    "sorting algorithms": [
        {
            "question": "Is bubble sort always the fastest sorting algorithm?",
            "options": ["Yes, always", "No, it is often slow for large inputs",
                        "Only for sorted lists", "Sorting speed does not matter"],
            "correct_idx": 1
        },
        {
            "question": "For 10,000 elements, which is typically faster: bubble sort or quicksort?",
            "options": ["Bubble sort", "Quicksort", "Same speed", "Unknown"],
            "correct_idx": 1
        },
        {
            "question": "What is the worst-case time complexity of bubble sort?",
            "options": ["O(n)", "O(n log n)", "O(n^2)", "O(1)"],
            "correct_idx": 2
        },
        {
            "question": "Why might another algorithm be faster than bubble sort?",
            "options": ["Bubble sort is always optimal",
                        "Different algorithms have different time complexities",
                        "Speed does not depend on algorithm", "Algorithms are the same"],
            "correct_idx": 1
        },
        {
            "question": "Which sorting algorithm is generally better for large datasets?",
            "options": ["Bubble sort", "Merge sort or Quicksort",
                        "All are equally good", "Sorting is random"],
            "correct_idx": 1
        }
    ],
    "binary search": [
        {
            "question": "Can binary search work on an unsorted list?",
            "options": ["Yes, it works anywhere",
                        "No, the list must be sorted",
                        "Only on partially sorted lists",
                        "It depends on the values"],
            "correct_idx": 1
        },
        {
            "question": "If your list is unsorted, will binary search give wrong results?",
            "options": ["No, binary search is reliable everywhere",
                        "Yes, it may miss items or give wrong answers",
                        "Binary search cannot run on unsorted data at all",
                        "It works but slowly"],
            "correct_idx": 1
        },
        {
            "question": "What must be true about a list before using binary search?",
            "options": ["Nothing special", "It must be sorted", "It must have numbers only",
                        "It must be a certain size"],
            "correct_idx": 1
        },
        {
            "question": "Why does binary search require sorted data?",
            "options": ["It does not require sorted data",
                        "To eliminate half the search space each time",
                        "To make the code simpler",
                        "To save memory"],
            "correct_idx": 1
        },
        {
            "question": "Binary search on unsorted data [3, 1, 4, 1, 5]—what happens?",
            "options": ["Works perfectly", "Gives unreliable results",
                        "Runs very fast anyway", "Gets stuck"],
            "correct_idx": 1
        }
    ],
    "trees in CS": [
        {
            "question": "Must a binary tree always be balanced?",
            "options": ["Yes, always balanced", "No, it can be unbalanced",
                        "Only in computer science", "Balancing is auto-done"],
            "correct_idx": 1
        },
        {
            "question": "Can a binary tree be completely lopsided (like a linked list)?",
            "options": ["No, binary trees are always balanced",
                        "Yes, it is still a valid binary tree",
                        "Only theoretically",
                        "Never in practice"],
            "correct_idx": 1
        },
        {
            "question": "What defines a binary tree?",
            "options": ["Must be balanced", "Each node has at most 2 children",
                        "Always has equal left and right subtrees",
                        "Must have specific depth"],
            "correct_idx": 1
        },
        {
            "question": "Is an unbalanced binary tree still a valid binary tree?",
            "options": ["No", "Yes, balance is optional", "Only sometimes",
                        "Depends on language"],
            "correct_idx": 1
        },
        {
            "question": "What happens when a binary tree is very unbalanced?",
            "options": ["It becomes invalid", "Operations may become slower",
                        "It auto-balances", "Nothing changes"],
            "correct_idx": 1
        }
    ],
    "time complexity": [
        {
            "question": "Is O(n^2) always slower than O(n log n)?",
            "options": ["Yes, always", "No, it depends on the constants and input size",
                        "Only for large inputs", "Speed is independent of complexity"],
            "correct_idx": 1
        },
        {
            "question": "For input size n=10, is 100*n^2 faster or slower than n log n?",
            "options": ["100*n^2 is faster", "n log n is faster",
                        "They're equal", "Cannot compare without testing"],
            "correct_idx": 0
        },
        {
            "question": "What does time complexity notation tell us?",
            "options": ["Exact runtime", "Behavior as input grows",
                        "Exact number of operations", "Memory only"],
            "correct_idx": 1
        },
        {
            "question": "Can an O(n^2) algorithm outperform O(n log n) for small inputs?",
            "options": ["Never", "Yes, constants matter",
                        "Only in theory", "Not possible"],
            "correct_idx": 1
        },
        {
            "question": "Why do we study Big O complexity?",
            "options": ["To guarantee exact runtimes",
                        "To understand scalability as inputs grow",
                        "It predicts performance always",
                        "It is just a label"],
            "correct_idx": 1
        }
    ],
    "dynamic programming": [
        {
            "question": "Is dynamic programming just recursion with loops?",
            "options": ["Yes, exactly", "No, it adds memoization to avoid recomputation",
                        "Only partially true", "No one knows"],
            "correct_idx": 1
        },
        {
            "question": "What is the key idea behind dynamic programming?",
            "options": ["Use more loops", "Store results to avoid redundant calculations",
                        "Make it look complex", "Replace all recursion"],
            "correct_idx": 1
        },
        {
            "question": "Can you use dynamic programming without recursion?",
            "options": ["No, always need recursion", "Yes, via tabulation (bottom-up)",
                        "Only in certain languages", "Not practical"],
            "correct_idx": 1
        },
        {
            "question": "What problem type benefits most from dynamic programming?",
            "options": ["Sorting", "Problems with overlapping subproblems",
                        "Graphics", "String formatting"],
            "correct_idx": 1
        },
        {
            "question": "What does memoization in DP do?",
            "options": ["Forgets computed results", "Saves computed results to reuse them",
                        "Speeds up loops", "Slows things down"],
            "correct_idx": 1
        }
    ]
}

# MISCONCEPTIONS DATABASE
MISCONCEPTIONS_DB = {
    "loops in Python": "a while loop always runs forever",
    "lists in Python": "lists can only store numbers",
    "functions in Python": "a function runs automatically when defined",
    "recursion in Python": "recursion always causes infinite loops",
    "sorting algorithms": "bubble sort is always the fastest",
    "binary search": "binary search works on unsorted lists",
    "trees in CS": "a binary tree must always be balanced",
    "time complexity": "O(n^2) is always slower than O(n log n) for all inputs",
    "dynamic programming": "dynamic programming is just recursion with loops",
}

# TOPICS BY DIFFICULTY
TOPICS_BY_DIFFICULTY = {
    "easy": ["loops in Python", "lists in Python", "functions in Python"],
    "medium": ["recursion in Python", "sorting algorithms", "binary search"],
    "hard": ["trees in CS", "time complexity", "dynamic programming"],
}


def get_quiz_for_topic(topic: str) -> List[Dict]:
    """Get quiz questions for a given topic"""
    return QUIZ_DATABASE.get(topic, [])


def score_quiz_response(topic: str, responses: List[int]) -> int:
    """
    Score a quiz based on user responses.
    responses: list of selected answer indices (0-indexed)
    Returns: number of correct answers (0-5)
    """
    quiz = get_quiz_for_topic(topic)
    if len(responses) != len(quiz):
        return 0
    
    score = 0
    for response_idx, question in zip(responses, quiz):
        if response_idx == question["correct_idx"]:
            score += 1
    return score
