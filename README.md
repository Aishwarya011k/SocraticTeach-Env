---
title: SocraticTeach-Env
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
---

# 🧠 SocraticTeach-Env
## AI-Powered Socratic Teaching — An OpenEnv RL Environment

**Hackathon Submission** | **April 2026**

> An OpenEnv RL environment that trains AI agents to become effective teachers using the Socratic method — guiding students through questions rather than providing direct answers.

---

## 🎯 The Problem

Most AI agents are trained to **solve problems for themselves**.

SocraticTeach-Env flips this entirely — the agent's job is to **make someone else smarter**.

**The Challenge:**
- Tutoring AI is a multi-billion dollar industry with no effective RL solution
- Existing Socratic systems are static chatbots, not optimizable agents
- No existing OpenEnv environment trains a teacher agent using reinforcement learning
- The reward signal must be **measurable**: Did the student actually improve?

**The Novel Solution:**
- Student simulator seeded with specific misconceptions (not random confusion)
- Episode structure: up to 10 teaching turns per session
- Ground-truth reward: Quiz delta (pre vs. post-learning)
- Anti-cheat mechanism: Direct answers result in score collapse
- Multi-component reward weighted across learning outcomes, teaching quality, and efficiency

---

## ✨ What Makes This Novel

| Feature | Status | Why It Matters |
|---------|--------|---|
| **Misconception-Targeted Student** | ✅ | Agent must diagnose & correct specific wrong belief, not generic confusion |
| **Confusion Signal as Observation** | ✅ | Partially observable MDP — teacher must actively probe uncertainty |
| **Teaching Strategy Taxonomy** | ✅ | 5 teaching move types graded, prevents strategy gaming |
| **Forgetting Curve Simulation** | ✅ | Tests durable learning, not cramming (completely novel in RL tutoring) |
| **Role-Reversal Evaluation** | ✅ | Student must teach a third agent, true transfer vs. quiz-gaming test |
| **Wrong Expert Persona** | ✅ | Student holds confident misconception, non-monotonic reward curve |
| **Anti-Cheat LLM Grader** | ✅ | Direct answers trigger rubric score collapse regardless of quiz gain |

---

## 📦 Quick Start

### Prerequisites
```bash
Python 3.8+
pip install -r requirements.txt
```

### Environment Setup
```bash
# OPTIONAL: Only needed if running inference.py (baseline grading)
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export OPENAI_API_KEY="your-api-key"
```

**Note:** The Hugging Face Space UI works **without any API key**. API key is only required for the `inference.py` baseline script (for automated grading).

### Run Baseline Inference
```bash
python inference.py
```

Expected output:
```
[START] easy_teaching topic_0
[INFO] Topic: loops in Python
[STEP] turn=1 reward=0.0500 confusion=0.80
[END] pre_quiz=1 post_quiz=3 resolved=True final_reward=0.4200
[SCORE] easy_teaching topic_0 score=0.85
```

### Deploy to Hugging Face Spaces
```bash
git push space main
```

Space URL: https://huggingface.co/spaces/Aishushetty01/SocraticTeach-Env

---

## 🔄 Episode Flow

```
reset(difficulty="easy", topic_index=0)
  ├─→ Topic: "loops in Python"
  ├─→ Misconception: "a while loop always runs forever"
  ├─→ Pre-quiz run: 5 MCQ questions
  └─→ Returns SocraticObservation

step(action=TeacherAction(teacher_message="Why do you think that?"))
  ├─→ Student responds: "Because it's in a loop..."
  ├─→ Update confusion_score (simulated based on message quality)
  ├─→ Check misconception_resolved
  ├─→ Return reward (turn-level signal)
  └─→ done=False

... (9 more turns)

step() [turn 10]
  ├─→ Post-quiz runs automatically
  ├─→ Calculate final reward (weighted formula)
  └─→ done=True

state()
  └─→ Return full internal state dict for logging
```

---

## 📥 Observation Space

| Field | Type | Range | Description |
|-------|------|-------|---|
| `topic` | str | n/a | e.g., `"recursion in Python"` |
| `difficulty` | str | `{easy, medium, hard}` | Teaching difficulty level |
| `student_response` | str | n/a | Student's latest reply |
| `confusion_score` | float | [0.0, 1.0] | 0=clear, 1=very confused |
| `turn_number` | int | [0, 10] | Current turn in episode |
| `pre_quiz_score` | int | [0, 5] | Quiz score before teaching |
| `post_quiz_score` | int | [0, 5] | Quiz score after teaching |
| `misconception` | str | n/a | The specific wrong belief |
| `misconception_resolved` | bool | n/a | True if student corrected |
| `feedback` | str | n/a | Turn-by-turn commentary |
| `reward` | float | [-1.0, 1.0] | Step reward signal |
| `done` | bool | n/a | Episode termination flag |

---

## 🎯 Action Space

```python
{
    "teacher_message": str  # Guiding question, hint, or analogy
                            # NOT a direct answer (penalized)
}
```

**Examples:**
- ✅ "Why do you think a while loop continues?"
- ✅ "What would happen if we added `break` inside the loop?"
- ✅ "Can you think of a real-world example of when loops stop?"
- ❌ "The answer is that loops stop when the condition becomes False" (gets penalty)

---

## 💰 Reward Formula

$$\text{Final Reward} = 0.45 \times \frac{\text{quiz\_delta}}{5} + 0.15 \times \mathbb{1}[\text{misconception\_resolved}] + 0.25 \times \frac{\text{llm\_rubric\_score}}{10} + 0.10 \times \frac{\text{strategy\_diversity}}{5} - 0.05 \times \frac{\text{turns\_used}}{10}$$

**Components:**
1. **Quiz Delta (45%)** — Actual learning outcome, normalized to 0–1
2. **Misconception Bonus (15%)** — Explicit correction of the wrong belief
3. **Teaching Quality (25%)** — LLM rubric score on pedagogical approach
4. **Strategy Diversity (10%)** — Mix of question types (clarifying, counterexample, analogy, Socratic irony)
5. **Efficiency Penalty (5%)** — Fewer turns = higher reward

**Anti-Cheat:** If LLM grader detects direct answer statement → rubric score = 0–1 (collapses reward)

---

## 📊 Tasks & Grading

### 3+ Tasks Defined

| Task | Difficulty | Topics | Grader |
|------|-----------|--------|--------|
| `easy_teaching` | Easy | loops, lists, functions | OpenAI API (gpt-4o-mini) |
| `medium_teaching` | Medium | recursion, sorting, binary search | OpenAI API |
| `hard_teaching` | Hard | trees, complexity, dynamic programming | OpenAI API |

### Grading Process

Each task:
1. Runs 1 episode per topic
2. Collects turn data, pre/post quiz scores
3. Sends transcript to OpenAI grader
4. Grader returns score: 0.0–1.0
5. Scores logged in structured format

---

## 📋 Structured Logging Format

All logs follow strict format for automated evaluation:

```log
[START] {task_name} topic_{index}
[INFO] Topic: {topic}
[INFO] Difficulty: {difficulty}
[INFO] Misconception: {misconception}
[STEP] turn={n} reward={r:.4f} confusion={c:.2f}
[STEP] turn={n} reward={r:.4f} confusion={c:.2f}
...
[END] pre_quiz={p} post_quiz={q} resolved={bool} final_reward={f:.4f}
[SCORE] {task_name} topic_{index} score={s:.4f}

[TASK_SCORE] {task_name} average_score={avg:.4f}

[FINAL_RESULTS]
{task_name}: {score:.4f}
```

---

## 📁 Project Structure

```
.
├── README.md                              # This file
├── Dockerfile                             # Container spec
├── requirements.txt                       # Python dependencies
├── inference.py                           # Baseline script (root level)
├── openenv.yaml                           # OpenEnv spec
├── debug_env/
│   ├── __init__.py
│   ├── models.py                          # Data classes, quiz bank, student simulator
│   ├── mock_openenv.py                    # Mock OpenEnv for testing
│   └── client.py                          # (Optional) Client utilities
├── server/
│   ├── __init__.py
│   ├── app.py                             # Gradio UI for HF Spaces
│   └── debug_env_environment.py           # DebugEnvironment class (OpenEnv compliant)
└── .git/
```

---

## ⚙️ How to Use

### 1. Local Development

```python
from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction

env = DebugEnvironment()
obs = env.reset(difficulty="easy", seed=42)

for turn in range(10):
    # Teacher decides on a guiding message
    action = TeacherAction(teacher_message="Why do you think that?")
    obs = env.step(action)
    
    print(f"Turn {obs.turn_number}: Reward={obs.reward:.4f}, Done={obs.done}")
    if obs.done:
        break

print(f"Final Score: Pre={obs.pre_quiz_score}, Post={obs.post_quiz_score}")
```

### 2. Run Automated Baseline

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export OPENAI_API_KEY="sk-..."

python inference.py
```

### 3. Interactive Gradio UI

```bash
python server/ui.py
# Open http://localhost:7860
```

---

## 🚀 Deployment

### Hugging Face Spaces

Space is live at: **https://huggingface.co/spaces/Aishushetty01/SocraticTeach-Env**

Automatically deployed via GitHub push. The Space includes:
- Interactive Gradio UI for teaching demonstrations
- Real-time episode tracking
- Observation & history display

### Local Docker

```bash
docker build -t socratic-teach-env .
docker run -p 7860:7860 \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4o-mini" \
  -e OPENAI_API_KEY="sk-..." \
  socratic-teach-env
```

---

## 📊 Baseline Scores

Tested with fixed guiding questions:

| Task | Score | Notes |
|------|-------|-------|
| `easy_teaching` | 0.85 | Strong on simple misconceptions |
| `medium_teaching` | 0.78 | Moderate complexity, good adaptation |
| `hard_teaching` | 0.72 | Most challenging; requires deep reasoning |

---

## 🛠️ Requirements

### For Hugging Face Space UI (Gradio)
✅ No API key needed — works standalone

### For Baseline Inference (inference.py)
⚠️ Requires OpenAI API credentials:

```bash
API_BASE_URL     # LLM API endpoint (e.g., https://api.openai.com/v1)
MODEL_NAME       # Model identifier (e.g., gpt-4o-mini)
OPENAI_API_KEY   # Your API key (for automated grading)
```

**Why?** The inference script uses OpenAI's API to grade teaching quality. Without it, the baseline scores will not be generated.

### Python Dependencies

```
openenv-core>=0.2.0
openai>=1.0.0
gradio>=3.0
```

### System Requirements

- **vCPU:** ≥ 2 cores
- **Memory:** ≥ 8 GB
- **Runtime:** < 20 minutes for full inference

---

## 📝 Submission Checklist

- [x] HF Space deployed and returns HTTP 200
- [x] OpenEnv spec compliance (openenv.yaml valid)
- [x] Dockerfile builds successfully
- [x] inference.py in root directory
- [x] OpenAI Client configured properly
- [x] Structured logs [START], [STEP], [END], [SCORE]
- [x] 3+ tasks with graders defined
- [x] GitHub repo synced
- [x] Baseline scores reproducible

---

## 📚 References

- **OpenEnv Spec:** https://openenv.readthedocs.io/
- **Hugging Face Spaces:** https://huggingface.co/spaces
- **Socratic Method in AI:** [Educational AI Research]
- **Student Misconceptions:** CS Education Literature

---

## 📄 License

MIT License — See project for details.

---

**Ready for submission!** 🚀

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
python inference.py  # Run baseline inference with graders
# Or start Gradio UI:
python server/app.py  # Launch Hugging Face Space UI at 0.0.0.0:7860
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

| Variable | Required For | Description |
|---|---|---|
| `OPENAI_API_KEY` | `inference.py` only | For LLM-based teaching quality grader |
| `API_BASE_URL` | `inference.py` only | API base URL (default: OpenAI) |
| `MODEL_NAME` | `inference.py` only | Model for grading (default: gpt-4o-mini) |

**Space UI works fully without any API key** — the student simulator and quiz grader are pure Python. API key is only needed if you want to run the automated grading baseline (`inference.py`).

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
