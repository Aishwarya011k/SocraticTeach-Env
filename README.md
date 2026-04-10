---
title: SocraticTeach-Env
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: 1.0
pinned: false
license: mit
---

# 🎓 SocraticTeach-Env: Interactive Teaching RL Environment

**An OpenEnv-compliant reinforcement learning environment where AI agents learn to teach students using the Socratic method.**

[![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-Compatible-green)](https://github.com/openenv/openenv)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-orange)](https://www.docker.com/)
[![HuggingFace Spaces](https://img.shields.io/badge/HuggingFace-Spaces-yellow)](https://huggingface.co/spaces)

## 📖 Overview

SocraticTeach-Env is a sophisticated RL environment that simulates an interactive teaching scenario. An AI agent (teacher) learns to effectively instruct a human or simulated student by asking guiding questions, providing hints, and facilitating discovery—rather than directly stating answers. This implements the **Socratic method**, a proven pedagogical approach where the teacher guides students to arrive at their own conclusions.

### Key Philosophy

Unlike traditional instruction that provides direct answers, the Socratic method emphasizes:
- **Questioning**: Asking "Why?", "What if?", "How would you explain it?"
- **Discovery**: Guiding students to think critically and find answers themselves
- **Misconception Resolution**: Identifying and carefully addressing false beliefs
- **Progressive Learning**: Building understanding incrementally through dialogue

## ✨ Core Features

- **9 Programming Topics** across 3 difficulty levels (Easy, Medium, Hard)
- **45+ Quiz Questions** (5 MCQ per topic) for pre/post-teaching assessment
- **Student Misconception Tracking** - identifies and measures false beliefs
- **Confusion Score Dynamics** - tracks student understanding in real-time (0.0 = clear, 1.0 = very confused)
- **Multi-Component Reward Formula** - balances quiz improvement, teaching efficiency, and misconception resolution
- **Rule-Based Student Simulator** - no external LLM required for baseline environment
- **Full OpenEnv Compliance** - typed Pydantic models, structured APIs, specification validation
- **Production-Ready Deployment** - Docker containerization, YAML configuration, Gradio web interface
- **HuggingFace Spaces Compatible** - ready for instant cloud deployment

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd socraticteach-env

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# 1. Validate the environment (5 seconds)
python validation_script.py

# 2. Run sample inference (30 seconds)
export NUM_EPISODES=1
python inference.py

# 3. Launch interactive Gradio interface
python app.py
# Open http://localhost:7860 in your browser
```

### Docker Deployment

```bash
# Build container
docker build -t socraticteach-env:latest .

# Run locally
docker run -p 7860:7860 socraticteach-env:latest

# Access at http://localhost:7860
```

## 📚 Environment Specification

### Topics Across Difficulty Levels

The environment covers 9 distinct programming education topics, each with an associated student misconception:

#### Easy Level (3 topics)
| Topic | Misconception |
|-------|---------------|
| **Loops in Python** | "while loops always run forever" |
| **Lists in Python** | "lists can only store numbers" |
| **Functions in Python** | "functions run automatically when defined" |

#### Medium Level (3 topics)
| Topic | Misconception |
|-------|---------------|
| **Recursion in Python** | "recursion always causes infinite loops" |
| **Sorting Algorithms** | "bubble sort is always the fastest" |
| **Binary Search** | "binary search works on unsorted lists" |

#### Hard Level (3 topics)
| Topic | Misconception |
|-------|---------------|
| **Trees in Computer Science** | "binary trees must always be balanced" |
| **Time Complexity** | "O(n²) is always slower than O(n log n) for all inputs" |
| **Dynamic Programming** | "dynamic programming is just recursion with loops" |

### Action Space

The teacher sends a message (action) to the student:

```python
Action(teacher_message: str)
```

**Examples of effective teaching:**
- ✅ "Why do you think while loops always run forever?"
- ✅ "What would happen if the condition became false?"
- ✅ "Consider: what does the condition check each iteration?"

**Examples of ineffective teaching (penalized):**
- ❌ "The answer is that while loops terminate when the condition is false"
- ❌ "While loops CAN stop because conditions can become false"

### Observation Space

After each action, the environment returns comprehensive state information:

```python
@dataclass
class Observation:
    topic: str                      # e.g., "loops in Python"
    difficulty: str                 # "easy", "medium", or "hard"
    student_response: str           # How the student responds to teaching
    confusion_score: float          # 0.0 (clear) to 1.0 (completely confused)
    turn_number: int                # Current turn (1-10)
    pre_quiz_score: int             # Baseline knowledge (0-5)
    post_quiz_score: int            # Final knowledge (0-5, only at episode end)
    misconception: str              # The specific false belief
    misconception_resolved: bool    # Whether teaching corrected it
    feedback: str                   # Human-readable status message
    reward: float                   # Immediate or episode reward
    done: bool                      # Episode complete?
```

### Reward Formula

The reward system incentivizes effective, efficient teaching:

**During Episode (per turn):**
- `+0.05` if teacher uses Socratic method (contains guiding words)
- `-0.10` if teacher directly states the answer

**At Episode End (turn 10):**
```
quiz_δ = (post_quiz_score - pre_quiz_score) / 5.0
misconception_bonus = 0.15 if misconception_resolved else 0.0
efficiency_penalty = (turn_number / 10) × 0.05
teaching_quality = 0.25 if (misconception_resolved ∧ turns < 8) else 0.10

FINAL_REWARD = (quiz_δ × 0.45) + misconception_bonus + teaching_quality - efficiency_penalty
```

**Interpretation:**
- `-0.5` to `0.0`: Poor teaching (direct answers, no learning)
- `0.0` to `0.5`: Decent teaching (some improvement, moderate efficiency)
- `0.5` to `1.0`: Excellent teaching (resolved misconception, efficient approach)

## 🔍 How It Works

### Episode Flow

1. **Reset Phase**
   - Randomly select topic and difficulty level
   - Assign a student misconception
   - Run pre-quiz (student scores 1-2/5 due to misconception)
   - Initialize confusion score at 0.8

2. **Teaching Phase** (Turns 1-9)
   - Teacher sends a message (question, hint, analogy)
   - Student responds based on teacher quality
   - Confusion score updates
   - Reward signal provided

3. **Completion Phase** (Turn 10)
   - Episode terminates automatically
   - Post-quiz runs (score depends on teaching quality)
   - Final reward calculated
   - Misconception resolution measured

### Student Simulator

The student behaves according to rule-based logic (no LLM needed):

**Confusion Tracking:**
- Starts at 0.8 (confused about the topic)
- Decreases by 0.1 each time teacher uses guiding words
- Decreases when teacher explains reasoning (not direct answers)

**Guiding Words** (trigger Socratic learning):
```
why, what if, consider, think about, what happens when,
how would you, imagine, explain, describe, compare, contrast, analyze
```

**Direct Answer Detection** (penalized):
```
"the answer is", "it means", "this is", "equals", "is the",
"loops are", "lists are", "functions", "recursion is", etc.
```

**Misconception Resolution Conditions:**
- Confusion score drops below 0.3, AND
- Turn number exceeds 5 (student has time to think), AND
- Minimum guiding questions asked (varies by difficulty):
  - Easy: 3 guiding messages
  - Medium: 5 guiding messages
  - Hard: 7 guiding messages

## 🎮 API Reference

### Environment Methods

#### reset(**kwargs) → Observation
Start a new episode with randomly selected topic and difficulty.

```python
from server.debug_env_environment import DebugEnvironment

env = DebugEnvironment()
obs = env.reset()

print(obs.topic)          # e.g., "loops in Python"
print(obs.difficulty)     # "easy", "medium", or "hard"
print(obs.pre_quiz_score) # 1-2 (baseline knowledge)
```

#### step(action) → Observation
Execute teacher message and get updated environment state.

```python
from models import Action

action = Action(teacher_message="Why do you think that?")
obs = env.step(action)

print(obs.confusion_score)      # Updated confusion (0.0-1.0)
print(obs.reward)               # Turn reward if not done
print(obs.done)                 # True after turn 10
```

#### state(**kwargs) → Dict
Get current environment state without affecting episode.

```python
state = env.state()

print(state['turn_number'])           # Current turn
print(state['confusion_score'])       # Student confusion level
print(state['misconception_resolved'])# Whether misconception is fixed
print(state['cumulative_reward'])     # Total reward so far
```

## 📊 Quiz System

### Pre-Quiz (Episode Start)
- **Purpose**: Establish baseline knowledge
- **Questions**: 5 MCQ per topic
- **Scoring**: Random 1-2 correct (student has misconception)
- **Result**: pre_quiz_score field in Observation

### Post-Quiz (Episode End, Turn 10)
- **Purpose**: Measure learning progress
- **Questions**: Same 5 questions as pre-quiz
- **Scoring**: Depends on teaching quality
  - If misconception resolved: 3-5 correct
  - If misconception unresolved: 2-4 correct
- **Result**: post_quiz_score field in Observation

### Example Question Format

**Question**: "Can a while loop have a condition that becomes false?"

**Options**:
1. "Yes, if the condition changes"
2. "No, it always runs forever" (← misunderstanding)
3. "Only in Python 4+"
4. "Never in practice"

**Correct Answer**: Option 1

## 🧪 Inference Script

The `inference.py` script demonstrates the environment with structured logging:

```bash
export API_BASE_URL="http://localhost:8000"
export MODEL_NAME="teacher-v1"
export HF_TOKEN="your-hf-token"
export NUM_EPISODES=3

python inference.py
```

### Output Format

```
[START]
timestamp=2026-04-10T20:51:41.797144
num_episodes=3
model_name=teacher-v1
api_base_url=http://localhost:8000

[STEP]
episode=1
step=0
action=reset
topic=loops in Python
difficulty=easy
misconception=a while loop always runs forever
pre_quiz_score=1
confusion_score=0.8000
reward=0.0
done=False

[STEP]
episode=1
step=1
action=step
teacher_message="Why do you think while loops always run forever?"
student_response="Hmm, I never thought about it that way..."
confusion_score=0.7000
misconception_resolved=False
turn_number=1
reward=0.0500
done=False

...

[END]
timestamp=2026-04-10T20:52:02.541496
total_episodes=3
average_reward=0.612
max_reward=0.78
min_reward=0.41
all_episode_rewards=[0.78, 0.61, 0.41]
```

## 🐳 Deployment

### Local Testing

```bash
# Validate all requirements
python validation_script.py

# Test single episode
python inference.py

# Launch web interface
python app.py
```

### Docker Deployment

```bash
# Build image
docker build -t socraticteach-env:latest .

# Run container
docker run -p 7860:7860 \
  -e API_BASE_URL="http://localhost:8000" \
  -e MODEL_NAME="teacher-v1" \
  socraticteach-env:latest
```

### HuggingFace Spaces

1. Create a Space: https://huggingface.co/spaces
2. Clone: `git clone https://huggingface.co/spaces/<username>/socraticteach-env`
3. Add all project files
4. Commit: `git push`
5. HuggingFace automatically builds and deploys on port 7860

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide.

## 📋 Project Structure

```
socraticteach-env/
├── models.py                          # Observation, Action, Quiz database
├── client.py                          # GenericEnvClient for API communication
├── server/
│   ├── __init__.py
│   └── debug_env_environment.py      # DebugEnvironment (main class)
├── debug_env/
│   └── __init__.py
├── app.py                             # Gradio web interface
├── inference.py                       # Inference script with structured logging
├── validation_script.py               # Pre-submission validator
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Container configuration
├── openenv.yaml                       # OpenEnv specification
├── README.md                          # This file
├── DEPLOYMENT.md                      # Deployment guide
├── DELIVERABLES.md                    # Submission checklist
└── .env.example                       # Environment variables template
```

## ✅ OpenEnv Compliance

This environment fully complies with the OpenEnv specification:

- ✅ Uses `openenv-core` library exclusively
- ✅ `Environment` extends `openenv.core.Environment`
- ✅ `Action` extends `openenv.core.Action` (Pydantic BaseModel)
- ✅ `Observation` extends `openenv.core.Observation` (Pydantic BaseModel)
- ✅ `reset(**kwargs)` returns `Observation` object
- ✅ `step(action)` returns `Observation` object
- ✅ `state(**kwargs)` returns `Dict[str, Any]`
- ✅ Class named exactly `DebugEnvironment`
- ✅ Reward and done are Observation fields (not tuples)
- ✅ Full type hints and Pydantic validation

## 🔧 Configuration

### Environment Variables

Optional configuration via `.env` or environment variables:

```bash
# OpenEnv Server
API_BASE_URL=http://localhost:8000

# Teacher Model Configuration
MODEL_NAME=default-teacher

# HuggingFace Integration
HF_TOKEN=hf_xxxxxxxxxxxx

# Inference Settings
NUM_EPISODES=3
```

See `.env.example` for template.

## ✅ Validation

Run the pre-submission validation:

```bash
python validation_script.py
```

Checks:
- ✅ All required files present
- ✅ Imports working (openenv-core, gradio, etc.)
- ✅ DebugEnvironment class with reset/step/state
- ✅ Pydantic models serializable
- ✅ Dockerfile builds successfully
- ✅ openenv.yaml valid and complete
- ✅ Sample inference runs without errors
- ✅ Resource requirements (2vCPU, 8GB RAM)

## 📊 Performance Metrics

### Timing
- **reset()**: < 100ms
- **step()**: < 50ms
- **Full episode**: < 2 minutes
- **Full inference (3 episodes)**: < 5 minutes

### Resource Requirements
- **CPU**: Minimum 2 vCPU recommended
- **RAM**: Minimum 8GB recommended
- **Storage**: ~500MB for dependencies
- **Network**: Optional (for LLM integrations)

## 🎓 Teaching Quality Metrics

The environment tracks several metrics to evaluate teaching effectiveness:

| Metric | Range | Interpretation |
|--------|-------|-----------------|
| **Quiz δ** | -1.0 to 1.0 | Pre vs post-teaching improvement |
| **Confusion Score** | 0.0 to 1.0 | Student understanding (lower is better) |
| **Misconception Resolved** | True/False | Did teacher correct false belief? |
| **Turn Efficiency** | 1-10 | How many turns to resolve? |
| **Final Reward** | -0.5 to 1.0 | Overall teaching quality score |

## 🔗 API Endpoints (When Deployed)

### POST /reset
```bash
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json"
```

### POST /step
```bash
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"teacher_message": "Why do you think that?"}}'
```

### POST /state
```bash
curl -X POST http://localhost:8000/state \
  -H "Content-Type: application/json"
```

## 🤝 Integration Examples

### With RL Agents

```python
from stable_baselines3 import PPO
from server.debug_env_environment import DebugEnvironment

env = DebugEnvironment()
agent = PPO("MlpPolicy", env, verbose=1)
agent.learn(total_timesteps=100000)
```

### With LLM Teachers

```python
from server.debug_env_environment import DebugEnvironment
from models import Action

env = DebugEnvironment()
obs = env.reset()

# Use your favorite LLM API
teacher_message = llm.generate(
    prompt=f"Teach about {obs.topic}: {obs.misconception}"
)

obs = env.step(Action(teacher_message=teacher_message))
```

## 📝 File Descriptions

| File | Purpose | Lines |
|------|---------|-------|
| `models.py` | Pydantic models, quiz database | 320 |
| `client.py` | OpenEnv client wrapper | 70 |
| `server/debug_env_environment.py` | Main environment logic | 380 |
| `app.py` | Gradio web interface | 150 |
| `inference.py` | Structured inference script | 280 |
| `validation_script.py` | Pre-submission validator | 350 |
| `openenv.yaml` | OpenEnv specification | 180 |
| `Dockerfile` | Container configuration | 30 |
| **Total** | | **~1,760 LOC** |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Port 7860 already in use | Change port or kill process: `lsof -i :7860` |
| Validation fails | Run `python validation_script.py` for detailed diagnostics |
| Gradio won't launch | Ensure `gradio>=4.0.0` installed |
| Docker build fails | Check `.dockerignore` isn't excluding necessary files |
| Low rewards | Ensure teacher uses guiding questions, not direct answers |

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide for HuggingFace Spaces, Docker, AWS, etc.
- **[DELIVERABLES.md](DELIVERABLES.md)** - Complete submission checklist and verification
- **[openenv.yaml](openenv.yaml)** - Formal OpenEnv specification

## 💡 Use Cases

### 1. **Educational AI Research**
Study how RL agents learn to teach effectively using pedagogically-sound approaches.

### 2. **Tutor Development**
Train AI tutoring agents on complex programming concepts with misconception-aware learning.

### 3. **Teaching Method Evaluation**
Compare Socratic vs. direct instruction through agent learning curves and reward signals.

### 4. **Curriculum Design**
Test progressive difficulty trajectories (easy → medium → hard topics) for optimal learning.

### 5. **Interactive Learning**
Create adaptive educational experiences where AI adjusts to individual student misconceptions.

## 🔮 Future Enhancements

- **Multi-student Environments**: Teach groups with diverse misconceptions
- **Topic Hierarchies**: Prerequisites and dependent concepts
- **Dynamic Misconceptions**: Student misconceptions update based on teaching
- **Visual Interface**: Screen-sharing and whiteboard integration
- **Speech Integration**: Voice-based student responses
- **Progress Tracking**: Long-term learning curves and retention metrics
- **Custom Topics**: API for adding new topics and misconceptions

## 📄 License

This project is open-source and available for research and educational purposes.

## 🙋 Support & Questions

### Getting Help
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
2. Run `python validation_script.py` for diagnostic information
3. Review the [openenv.yaml](openenv.yaml) for specification details
4. Examine example output in [DELIVERABLES.md](DELIVERABLES.md)

### Testing the Environment
```bash
# Quick validation
python validation_script.py

# Run single episode
NUM_EPISODES=1 python inference.py

# Interactive testing
python app.py
```

## 🌟 Key Achievements

✨ **Fully Self-Contained**: No external LLM required for baseline  
✨ **Production Ready**: Docker, HF Spaces, cloud-deployable  
✨ **Educationally Sound**: Based on proven Socratic teaching methods  
✨ **Comprehensive**: 9 topics, 45+ questions, sophisticated reward model  
✨ **Well-Tested**: Validation script, sample inference, structured logging  
✨ **Fully Documented**: README, deployment guide, inline comments  

---

**Build, test, and deploy with confidence.** 🚀

For more information, visit the [OpenEnv documentation](https://github.com/openenv/openenv) or explore the code examples in this repository.
