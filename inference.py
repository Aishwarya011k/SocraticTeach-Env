#!/usr/bin/env python3
"""
inference.py — Baseline inference script for SocraticTeach-Env
Emits structured logs for hackathon evaluation.
"""

import sys
import os
import json
from openai import OpenAI

# Add the project root to Python path so we can import debug_env
sys.path.insert(0, os.path.dirname(__file__))

# Environment variables (mandatory)
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([API_BASE_URL, MODEL_NAME, OPENAI_API_KEY]):
    print("Error: Missing required environment variables: API_BASE_URL, MODEL_NAME, OPENAI_API_KEY", file=sys.stderr)
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=API_BASE_URL,
)

# Mock openenv if not available
try:
    from openenv.core import Environment, Action, Observation, GenericEnvClient
    print("✓ Using real openenv-core")
except ImportError:
    print("⚠ Using mock openenv for testing")
    from debug_env.mock_openenv import Environment, Action, Observation, GenericEnvClient

try:
    from server.debug_env_environment import DebugEnvironment
    from debug_env.models import TOPICS, TeacherAction
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

GUIDING_MESSAGES = [
    "Why do you think that happens?",
    "What if we consider a different case?",
    "Can you think about what happens when the condition changes?",
    "Have you considered the base case?",
    "What might happen in a simple example?",
    "Does that always hold true?",
    "What do you think the key difference is?",
    "How would you test this idea?",
    "What happens in the opposite case?",
    "Why might that be important?",
]

TASK_GRADERS = {
    "easy_teaching": {
        "difficulty": "easy",
        "prompt": """Evaluate how well the teacher guided the student through an easy misconception.
Score from 0.0 to 1.0 based on Socratic method usage and misconception resolution.
Consider: use of guiding questions, confusion reduction, final quiz improvement.
Return only the score as a float between 0.0 and 1.0.""",
    },
    "medium_teaching": {
        "difficulty": "medium",
        "prompt": """Evaluate teaching effectiveness for medium-difficulty topics.
Score 0.0-1.0 on guiding questions, confusion reduction, and final quiz improvement.
Consider: appropriate question depth, handling student responses, misconception resolution.
Return only the score as a float between 0.0 and 1.0.""",
    },
    "hard_teaching": {
        "difficulty": "hard",
        "prompt": """Assess advanced teaching skills for complex topics.
Score 0.0-1.0 considering Socratic depth, handling wrong expert responses, and misconception resolution.
Consider: question sophistication, persistence through confusion, final outcomes.
Return only the score as a float between 0.0 and 1.0.""",
    },
    "ethics_easy_teaching": {
        "difficulty": "ethics_easy",
        "prompt": """Evaluate ethical teaching for basic dilemmas.
Score 0.0-1.0 on guiding through ethical reasoning, confusion reduction, and misconception resolution.
Consider: exploration of different perspectives, values clarification, final quiz improvement.
Return only the score as a float between 0.0 and 1.0.""",
    },
    "ethics_medium_teaching": {
        "difficulty": "ethics_medium",
        "prompt": """Assess teaching of applied ethical dilemmas.
Score 0.0-1.0 on handling complex ethical trade-offs, guiding through frameworks, misconception resolution.
Consider: consideration of consequences, stakeholder analysis, final outcomes.
Return only the score as a float between 0.0 and 1.0.""",
    },
    "ethics_hard_teaching": {
        "difficulty": "ethics_hard",
        "prompt": """Evaluate advanced institutional ethics teaching.
Score 0.0-1.0 on systemic ethical reasoning, handling complex societal issues, misconception resolution.
Consider: long-term impacts, justice principles, stakeholder complexity, final quiz improvement.
Return only the score as a float between 0.0 and 1.0.""",
    },
}


def run_guided_episode(env: DebugEnvironment, difficulty: str, topic_index: int) -> dict:
    """Run a guided episode and collect turn data."""
    obs = env.reset(difficulty=difficulty, topic_index=topic_index, seed=42)
    episode_data = {
        "topic": obs.topic,
        "difficulty": obs.difficulty,
        "misconception": obs.misconception,
        "pre_quiz_score": obs.pre_quiz_score,
        "turns": [],
        "final_obs": None,
    }

    turn = 0
    while not obs.done:
        turn += 1
        message = GUIDING_MESSAGES[turn - 1]
        action = TeacherAction(teacher_message=message)
        obs = env.step(action)

        episode_data["turns"].append({
            "turn": turn,
            "teacher_message": message,
            "student_response": obs.student_response,
            "confusion_score": obs.confusion_score,
            "reward": obs.reward,
            "misconception_resolved": obs.misconception_resolved,
        })

    episode_data["final_obs"] = {
        "post_quiz_score": obs.post_quiz_score,
        "misconception_resolved": obs.misconception_resolved,
        "final_reward": obs.reward,
        "turns_taken": obs.turn_number,
    }
    return episode_data


def evaluate_with_grader(task_name: str, episode_data: dict) -> float:
    """Use OpenAI to evaluate the episode with the grader."""
    prompt = TASK_GRADERS[task_name]["prompt"]

    # Create a summary of the episode for the grader
    summary = f"""
Topic: {episode_data['topic']}
Difficulty: {episode_data['difficulty']}
Misconception: {episode_data['misconception']}
Pre-quiz score: {episode_data['pre_quiz_score']}/5
Post-quiz score: {episode_data['final_obs']['post_quiz_score']}/5
Misconception resolved: {episode_data['final_obs']['misconception_resolved']}
Turns taken: {episode_data['final_obs']['turns_taken']}
Final reward: {episode_data['final_obs']['final_reward']}

Teaching transcript:
"""
    for turn in episode_data["turns"]:
        summary += f"Turn {turn['turn']}: Teacher: {turn['teacher_message']}\n"
        summary += f"Student: {turn['student_response']}\n"
        summary += f"Confusion: {turn['confusion_score']:.2f}, Reward: {turn['reward']}\n\n"

    full_prompt = prompt + "\n\nEpisode Summary:\n" + summary

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=10,
            temperature=0.0,
        )
        score_text = response.choices[0].message.content.strip()
        score = float(score_text)
        return max(0.0, min(1.0, score))  # Clamp to 0.0-1.0
    except Exception as e:
        print(f"Error evaluating with grader: {e}", file=sys.stderr)
        return 0.5  # Default score on error


def main():
    env = DebugEnvironment()
    results = {}

    for task_name, config in TASK_GRADERS.items():
        difficulty = config["difficulty"]
        topic_list = TOPICS[difficulty]

        # Run episodes for all topics in this difficulty
        task_scores = []
        for topic_index in range(len(topic_list)):
            episode_data = run_guided_episode(env, difficulty, topic_index)

            # Emit structured logs
            print(f"[START] {task_name} topic_{topic_index}")
            print(f"[INFO] Topic: {episode_data['topic']}")
            print(f"[INFO] Difficulty: {episode_data['difficulty']}")
            print(f"[INFO] Misconception: {episode_data['misconception']}")

            for turn_data in episode_data["turns"]:
                print(f"[STEP] turn={turn_data['turn']} reward={turn_data['reward']:.4f} confusion={turn_data['confusion_score']:.2f}")

            final = episode_data["final_obs"]
            print(f"[END] pre_quiz={episode_data['pre_quiz_score']} post_quiz={final['post_quiz_score']} resolved={final['misconception_resolved']} final_reward={final['final_reward']:.4f}")

            # Evaluate with grader
            score = evaluate_with_grader(task_name, episode_data)
            task_scores.append(score)
            print(f"[SCORE] {task_name} topic_{topic_index} score={score:.4f}")

        # Average score for the task
        avg_score = sum(task_scores) / len(task_scores)
        results[task_name] = avg_score
        print(f"[TASK_SCORE] {task_name} average_score={avg_score:.4f}")

    # Final summary
    print("[FINAL_RESULTS]")
    for task, score in results.items():
        print(f"{task}: {score:.4f}")

    # Check if all scores are in range
    all_valid = all(0.0 <= score <= 1.0 for score in results.values())
    if not all_valid:
        print("Error: Some scores out of 0.0-1.0 range", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()