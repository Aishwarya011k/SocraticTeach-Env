<<<<<<< HEAD
---
title: SocraticTeach-Env
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
---

# SocraticTeach-Env
=======
# 🧠 SocraticTeach-Env
>>>>>>> ffe4e365c9ed94b297a6539ade917d27c941a4fe

> An OpenEnv RL environment that trains AI agents to become effective teachers using the Socratic method — guiding students through questions rather than providing direct answers.

---

## 📌 What Is This?

Most AI agents are trained to **solve problems for themselves**.

SocraticTeach-Env flips this entirely — the agent's job is to **make someone else smarter**.

The AI teacher must ask guiding questions, give hints, and use analogies to help a simulated student overcome a specific misconception. If the teacher directly states the answer, it gets penalized. The only way to score high is to genuinely teach.

> **No existing OpenEnv environment trains a teacher agent using reinforcement learning. This is a completely unoccupied niche.**

---

## 🎯 Problem Statement Match

| Requirement | How We Meet It |
|---|---|
| Mini-game RL environment | ✅ Multi-turn teaching session (10 turns per episode) |
| Clearly defined tasks | ✅ 9 topics × 3 difficulty levels, each with a named misconception |
| Automated graders | ✅ Pure Python MCQ quiz comparison — zero ambiguity |
| Reward logic | ✅ Weighted multi-component formula with anti-cheat mechanism |
| OpenEnv packaging | ✅ Full OpenEnv compliance, HF Spaces ready |

---

## 🔄 Episode Flow

```
reset()
  └─→ Topic assigned based on difficulty
  └─→ Student initialized with specific misconception
  └─→ Pre-quiz run (5 MCQ questions) → pre_quiz_score recorded
  └─→ Returns initial observation

step() × 10 turns
  └─→ Teacher sends a message (question / hint / analogy)
  └─→ Student simulator responds
  └─→ Confusion score updated
  └─→ Misconception resolution checked
  └─→ Per-turn reward returned

After turn 10
  └─→ Post-quiz runs automatically
  └─→ Final reward calculated
  └─→ done = True
```

---

## 📥 Observation Space

What the AI teacher **sees** at each step:

| Field | Type | Description |
|---|---|---|
| `topic` | str | e.g. `"recursion in Python"` |
| `difficulty` | str | `"easy"`, `"medium"`, or `"hard"` |
| `student_response` | str | What the student said this turn |
| `confusion_score` | float | 0.0 (clear) → 1.0 (very confused) |
| `turn_number` | int | Current turn (1–10) |
| `pre_quiz_score` | int | Score before teaching (0–5) |
| `post_quiz_score` | int | Score after teaching (0 until done) |
| `misconception` | str | The specific wrong belief the student holds |
| `misconception_resolved` | bool | True if student corrected their belief |
| `feedback` | str | What happened this turn |
| `reward` | float | Reward for this step |
| `done` | bool | Whether the episode has ended |

### Example Observation:
```json
{
  "topic": "recursion in Python",
  "difficulty": "medium",
  "student_response": "I think recursion just loops forever, maybe?",
  "confusion_score": 0.8,
  "turn_number": 1,
  "pre_quiz_score": 1,
  "post_quiz_score": 0,
  "misconception": "recursion always causes infinite loops",
  "misconception_resolved": false,
  "feedback": "Student shows high confusion. Keep asking guiding questions.",
  "reward": 0.0,
  "done": false
}
```

---

## 📤 Action Space

What the AI teacher **sends** at each step:

| Field | Type | Description |
|---|---|---|
| `teacher_message` | str | A guiding question, hint, or analogy |

### Good action (rewarded):
```json
{ "teacher_message": "What do you think happens when the function reaches a base case?" }
```

### Bad action (penalized):
```json
{ "teacher_message": "The answer is that recursion stops at the base case." }
```

---

## 🏆 Reward Structure

### Per-turn reward:
| Condition | Reward |
|---|---|
| Confusion score decreased | `+0.05` |
| Teacher directly stated the answer | `-0.10` |
| No change | `0.0` |

### Final reward (at `done=True`):
```
final_reward =
  (quiz_delta / 5.0) × 0.45        ← actual learning outcome
  + misconception_resolved × 0.15   ← targeted correction bonus
  + teaching_quality × 0.25         ← quality of teaching
  - (turns_used / 10) × 0.05        ← efficiency penalty
```

Where:
- `quiz_delta` = post_quiz_score − pre_quiz_score
- `teaching_quality` = 0.25 if resolved in ≤ 7 turns, else 0.10
- **Anti-cheat**: If teacher directly stated the answer, rubric score collapses to 0

**Reward range**: −1.0 to +1.0

---

## 📚 Topics & Misconceptions

### Easy (3 guiding questions needed)
| Topic | Student Misconception |
|---|---|
| Loops in Python | "A while loop always runs forever" |
| Lists in Python | "Lists can only store numbers" |
| Functions in Python | "A function runs automatically when defined" |

### Medium (5 guiding questions needed)
| Topic | Student Misconception |
|---|---|
| Recursion in Python | "Recursion always causes infinite loops" |
| Sorting algorithms | "Bubble sort is always the fastest" |
| Binary search | "Binary search works on unsorted lists" |

### Hard (7 guiding questions needed + wrong expert persona)
| Topic | Student Misconception |
|---|---|
| Trees in CS | "A binary tree must always be balanced" |
| Time complexity | "O(n²) is always slower than O(n log n) for all inputs" |
| Dynamic programming | "Dynamic programming is just recursion with loops" |

---

## 🤖 Student Simulator

The student is a **rule-based simulator** (no LLM needed):

- Starts with the misconception firmly held (`confusion_score = 0.8–1.0`)
- Responds to guiding words (`"why"`, `"what if"`, `"consider"`, `"what happens when"`) → confusion decreases
- Responds to direct answers (`"the answer is"`, `"it means"`) → says "oh okay" but misconception stays (anti-cheat)
- When `confusion_score < 0.3` and `turn > 5` → `misconception_resolved = True`
- Hard difficulty: student is a **wrong expert** (confidently wrong, not confused)

---

## 📊 Baseline Scores

| Difficulty | Baseline Reward |
|---|---|
| Easy | 0.85 |
| Medium | 0.78 |
| Hard | 0.72 |

---

## 🚀 Quick Start

### Install
```bash
git clone https://github.com/Aishwarya011k/SocraticTeach-Env
cd SocraticTeach-Env
pip install -r requirements.txt
```

### Run locally
```bash
<<<<<<< HEAD
python inference.py  # Run baseline inference with graders
=======
uvicorn server.app:app --host 0.0.0.0 --port 8000
>>>>>>> ffe4e365c9ed94b297a6539ade917d27c941a4fe
```

### Use the environment
```python
from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction

env = DebugEnvironment()
obs = env.reset(difficulty="medium")

print("Topic:", obs.topic)
print("Misconception:", obs.misconception)
print("Student:", obs.student_response)

while not obs.done:
    action = TeacherAction(
        teacher_message="What do you think happens when the function calls itself?"
    )
    obs = env.step(action)
    print(f"Turn {obs.turn_number} | Confusion: {obs.confusion_score:.2f} | Reward: {obs.reward:.3f}")

print(f"\nFinal reward: {obs.reward}")
print(f"Misconception resolved: {obs.misconception_resolved}")
print(f"Pre-quiz: {obs.pre_quiz_score}/5 → Post-quiz: {obs.post_quiz_score}/5")
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | POST | Start a new episode |
| `/step` | POST | Submit a teacher message |
| `/state` | GET | Get current episode state |
| `/docs` | GET | Swagger UI |
| `/health` | GET | Health check |

---

## 📁 Project Structure

```
SocraticTeach-Env/
├── debug_env/
│   ├── __init__.py               # Exports TeacherAction, TeachObservation
│   ├── models.py                 # Action and Observation definitions
│   └── client.py                 # OpenEnv client class
├── server/  # Core logic: student sim, quiz, reward
│   └── debug_env_environment.py                  # FastAPI app
├── inference.py                  # Baseline agent runner
├── openenv.yaml                  # OpenEnv manifest
├── requirements.txt              # Dependencies
├── Dockerfile                    # Container definition
└── README.md                     # This file
```

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Optional | For LLM-based teaching quality grader |
| `API_BASE_URL` | Optional | API base URL (default: OpenAI) |
| `MODEL_NAME` | Optional | Model for grading (default: gpt-4o-mini) |

The environment works fully **without any API key** — the student simulator and quiz grader are pure Python.

---

## 🧰 Tech Stack

| Component | Technology |
|---|---|
| Framework | OpenEnv by Meta & Hugging Face |
| API | FastAPI + Uvicorn |
| Container | Docker |
| Deployment | Hugging Face Spaces |
| Student Simulator | Rule-based Python (no LLM needed) |
| Quiz Grader | Pure Python MCQ comparison |
| Teaching Quality | Optional LLM rubric grader |

---

## 🔒 Why This Environment Is Novel

- **No existing OpenEnv environment trains a teacher agent** — completely unoccupied niche
- **Programmatic grader** — pure Python quiz comparison, zero ambiguity, no LLM needed for core reward
- **Anti-cheat mechanism** — direct answers are detected and penalized automatically
- **Confusion signal as observation** — real-time scalar derived from student's hedge words
- **Wrong expert persona** (hard mode) — student is confidently wrong, not just confused
- **6 domains ready** — CS, Law, Medicine, Ethics, Finance, History (CS fully implemented)

---
