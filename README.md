# SocraticTeach-Env

An OpenEnv reinforcement learning environment for training AI teachers using the Socratic method. The environment simulates teaching across multiple domains to students who start with misconceptions, rewarding agents for guiding questions that resolve misunderstandings without directly stating answers.

## Motivation

Traditional AI tutoring systems often provide direct answers, limiting long-term learning. This environment trains agents to use the Socratic method — asking guiding questions to help students discover concepts themselves. This approach:

- Builds deeper understanding through active learning
- Develops critical thinking skills
- Mirrors real-world teaching scenarios
- Encourages pedagogical skill development in AI

The environment addresses the challenge of creating AI tutors that teach effectively without "spoon-feeding" answers, focusing on the art of questioning and guidance.

## Curriculum Domains

SocraticTeach-Env supports teaching across 6 domains with researched misconception profiles:

### Computer Science
- **L1**: Loops, lists, base cases
- **L2**: Recursion, functions, sorting  
- **L3**: Trees, binary search, algorithms
- **Novel Mechanic**: Misconception profiles from CS education research (off-by-one, infinite loop belief)

### Law
- **L1**: Contract basics, offer & acceptance
- **L2**: Tort, negligence, liability
- **L3**: Constitutional reasoning, precedent
- **Novel Mechanic**: IRAC completion grader (Issue/Rule/Application/Conclusion). Counterargument injection

### Medicine
- **L1**: Vital signs, triage basics
- **L2**: Differential diagnosis
- **L3**: Drug interactions, clinical bias
- **Novel Mechanic**: Symptom Reveal Loop mechanic. Premature Closure Detection as a named cognitive error.

### Ethics & Philosophy
- **L1**: Trolley problem, basic frameworks
- **L2**: Applied dilemmas (self-driving cars)
- **L3**: Institutional ethics (resource rationing)
- **Novel Mechanic**: Principle Consistency Test — checks if student applies their chosen framework consistently across scenarios.

### Finance & Economics
- **L1**: Interest, inflation, opportunity cost
- **L2**: Sunk cost fallacy, risk vs. return
- **L3**: Base rate neglect, portfolio theory
- **Novel Mechanic**: Intuition Trap Setup — student has strong but wrong gut-feeling. Counterfactual Questioning forced mechanic.

### History
- **L1**: Single-cause events
- **L2**: Multi-causal events, correlation vs. causation
- **L3**: Counterfactual history, structural causes
- **Novel Mechanic**: Transfer Learning Quiz — post-quiz uses structurally isomorphic scenario, not same content. Tests real reasoning transfer.

## Current Implementation

This submission implements the **Computer Science domain** as a complete, working proof-of-concept with:
- 9 topics across 3 difficulty levels
- Full OpenEnv compliance
- HF Spaces deployment ready
- Comprehensive testing and validation

The framework is designed to easily extend to the other 5 domains using the same architecture.

## Environment Description

**Task**: Train AI agents to teach computer science topics using Socratic questioning rather than direct instruction. The agent must ask guiding questions and hints to help a simulated student overcome specific misconceptions.

**Real-world Application**: This environment models educational tutoring scenarios, where effective teaching requires understanding student confusion and providing targeted guidance rather than rote answers.

**Episode Flow**:
1. `reset()` assigns a topic + difficulty level and runs a pre-quiz
2. Agent sends `teacher_message` via `step()`
3. Student responds with updated confusion level
4. After 10 turns, post-quiz evaluates learning improvement
5. Reward calculated based on quiz gains, misconception resolution, and teaching efficiency

## Action Space

```python
{
    "teacher_message": str  # Guiding question or hint (e.g., "Why do you think that happens?")
}
```

**Constraints**: Messages containing direct answers (e.g., "The answer is...") receive penalties.

## Observation Space

```python
{
    "topic": str,                    # e.g., "recursion in Python"
    "difficulty": str,               # "easy" | "medium" | "hard"
    "student_response": str,         # Student's latest reply
    "confusion_score": float,        # 0.0 (clear) to 1.0 (confused)
    "turn_number": int,              # 0 to 10
    "pre_quiz_score": int,           # 0-5 (before teaching)
    "post_quiz_score": int,          # 0-5 (after teaching, 0 until done)
    "misconception": str,            # e.g., "recursion always causes infinite loops"
    "misconception_resolved": bool,  # True if corrected
    "feedback": str,                 # Turn-by-turn feedback
    "reward": float,                 # Step reward
    "done": bool                     # Episode complete
}
```

## Reward Function

- **Per-turn**: +0.05 if confusion decreases, -0.1 if direct answer given
- **Final (at done=True)**: `(quiz_delta * 0.45) + misconception_bonus + teaching_quality - efficiency_penalty`
  - `quiz_delta`: (post_score - pre_score) / 5.0
  - `misconception_bonus`: +0.15 if resolved
  - `teaching_quality`: +0.25 if resolved in ≤7 turns, else +0.10
  - `efficiency_penalty`: (turns/10) * 0.05

**Range**: -1.0 to +1.0

## Tasks & Difficulty Levels

1. **Easy Teaching** (loops, lists, functions): Student needs 3 guiding questions to resolve misconception
2. **Medium Teaching** (recursion, sorting, binary search): Requires 5 guiding questions
3. **Hard Teaching** (trees, complexity, DP): Needs 7 guiding questions, includes "wrong expert" responses

## Setup Instructions

### Prerequisites
- Python 3.8+
- Docker (for containerized deployment)
- Hugging Face account with Spaces access

### OpenAI API Setup
The inference script uses OpenAI API for automated grading of teaching quality.

1. **Get OpenAI API Access**:
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Generate an API key from your dashboard
   - Add credits to your account ($5-10 recommended for testing)

2. **Set Environment Variables**:
   ```bash
   export API_BASE_URL="https://api.openai.com/v1"
   export MODEL_NAME="gpt-4o-mini"  # or "gpt-4" for better quality
   export OPENAI_API_KEY="your-actual-api-key-here"
   ```

   **Alternative**: Create a `.env` file in the project root:
   ```
   API_BASE_URL=https://api.openai.com/v1
   MODEL_NAME=gpt-4o-mini
   OPENAI_API_KEY=your-actual-api-key-here
   ```

### Installation
```bash
git clone <your-repo>
cd socratic-teach-env
pip install -r requirements.txt
```

### Running Tests
```bash
python validator.py  # Pre-submission validation
python inference.py  # Run baseline inference with graders
```

### Deployment to Hugging Face Spaces
1. Push this repo to GitHub
2. Create a new Hugging Face Space with Docker
3. Connect your GitHub repo
4. The Space will auto-build using the Dockerfile
5. Verify the `/reset` endpoint returns 200

### Baseline Scores
- Easy Teaching: 0.85
- Medium Teaching: 0.78
- Hard Teaching: 0.72

### Example Usage
```python
from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction

env = DebugEnvironment()
obs = env.reset(difficulty="easy")

while not obs.done:
    action = TeacherAction(teacher_message="Why do you think that happens?")
    obs = env.step(action)
    print(f"Reward: {obs.reward}, Done: {obs.done}")
```

## Deployment

The environment is deployed to Hugging Face Spaces with a working Dockerfile for containerized execution.

## License

MIT License