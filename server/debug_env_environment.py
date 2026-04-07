"""
server/debug_env_environment.py — SocraticTeach-Env
OpenEnv RL environment implementing the Socratic teaching loop.

Class name MUST be `DebugEnvironment` (required by openenv-core).
"""

import random

try:
    from openenv.core import Environment, Action, Observation
except ImportError:
    from debug_env.mock_openenv import Environment, Action, Observation

from debug_env.models import (
    TOPICS,
    run_quiz,
    run_post_quiz,
    simulate_student,
    compute_reward,
    SocraticObservation,
)

MAX_TURNS = 10


class DebugEnvironment(Environment):
    """
    SocraticTeach-Env — an RL environment for training AI teachers.

    Episode flow
    ------------
    1. reset(**kwargs)  → assigns topic + difficulty, runs pre-quiz, returns Observation
    2. step(action)     → teacher sends message, student responds, reward computed
    3. After 10 turns   → post-quiz runs, final reward returned, done=True
    """

    # ------------------------------------------------------------------
    # Internal state (reset each episode)
    # ------------------------------------------------------------------

    def _init_state(self) -> None:
        self._topic: str = ""
        self._difficulty: str = "medium"
        self._misconception: str = ""
        self._pre_quiz_score: int = 0
        self._post_quiz_score: int = 0
        self._confusion_score: float = 1.0   # start maximally confused
        self._turn_number: int = 0
        self._misconception_resolved: bool = False
        self._guiding_count: int = 0          # tracks guiding questions given
        self._done: bool = False
        self._prev_confusion: float = 1.0
        self._cumulative_reward: float = 0.0

    # ------------------------------------------------------------------
    # reset
    # ------------------------------------------------------------------

    def reset(self, **kwargs) -> Observation:
        """
        Start a new episode.

        Keyword args
        ------------
        difficulty : "easy" | "medium" | "hard"  (default "medium")
        seed       : int  (optional, for reproducibility)
        topic_index: int  (optional, override random topic selection)
        """
        seed = kwargs.get("seed", None)
        if seed is not None:
            random.seed(seed)

        self._init_state()

        difficulty = kwargs.get("difficulty", "medium")
        if difficulty not in TOPICS:
            difficulty = "medium"
        self._difficulty = difficulty

        # Pick topic
        topic_index = kwargs.get("topic_index", None)
        choices = TOPICS[difficulty]
        if topic_index is not None and 0 <= topic_index < len(choices):
            chosen = choices[topic_index]
        else:
            chosen = random.choice(choices)

        self._topic = chosen["topic"]
        self._misconception = chosen["misconception"]

        # Pre-quiz
        self._pre_quiz_score, _ = run_quiz(self._topic, random_seed=seed)
        self._post_quiz_score = 0

        # Initial student response — student holds the misconception firmly
        initial_student_msg = (
            f"I think {self._misconception}. That's just how it works, right?"
        )

        obs = SocraticObservation(
            topic=self._topic,
            difficulty=self._difficulty,
            student_response=initial_student_msg,
            confusion_score=self._confusion_score,
            turn_number=self._turn_number,
            pre_quiz_score=self._pre_quiz_score,
            post_quiz_score=self._post_quiz_score,
            misconception=self._misconception,
            misconception_resolved=self._misconception_resolved,
            feedback=(
                f"New episode started. Topic: '{self._topic}'. "
                f"Difficulty: {self._difficulty}. "
                f"Pre-quiz score: {self._pre_quiz_score}/5. "
                f"The student holds the misconception: '{self._misconception}'."
            ),
            reward=0.0,
            done=False,
        )
        return obs

    # ------------------------------------------------------------------
    # step
    # ------------------------------------------------------------------

    def step(self, action: Action, **kwargs) -> Observation:
        """
        Process one teacher turn.

        Parameters
        ----------
        action : Action  with field `teacher_message: str`
        """
        if self._done:
            raise RuntimeError(
                "Episode is done. Call reset() to start a new episode."
            )

        teacher_message: str = getattr(action, "teacher_message", "")

        self._turn_number += 1
        self._prev_confusion = self._confusion_score

        # Student reacts
        (
            student_response,
            new_confusion,
            new_resolved,
            gave_direct_answer,
            new_guiding_count,
        ) = simulate_student(
            teacher_message=teacher_message,
            misconception=self._misconception,
            confusion_score=self._confusion_score,
            turn_number=self._turn_number,
            difficulty=self._difficulty,
            guiding_count=self._guiding_count,
            misconception_resolved=self._misconception_resolved,
        )

        confusion_decreased = new_confusion < self._prev_confusion

        self._confusion_score = new_confusion
        self._misconception_resolved = new_resolved
        self._guiding_count = new_guiding_count

        # Check if episode ends
        self._done = self._turn_number >= MAX_TURNS

        # Post-quiz on final turn
        if self._done:
            self._post_quiz_score = run_post_quiz(
                self._topic,
                self._misconception_resolved,
                self._pre_quiz_score,
            )

        # Compute reward
        reward = compute_reward(
            pre_quiz_score=self._pre_quiz_score,
            post_quiz_score=self._post_quiz_score,
            misconception_resolved=self._misconception_resolved,
            turn_number=self._turn_number,
            confusion_decreased=confusion_decreased,
            gave_direct_answer=gave_direct_answer,
            done=self._done,
        )
        self._cumulative_reward += reward

        # Build feedback string
        feedback_parts = []
        if gave_direct_answer:
            feedback_parts.append(
                "⚠️  Teacher directly stated the answer — penalty applied. "
                "Misconception NOT resolved."
            )
        elif confusion_decreased:
            feedback_parts.append(
                f"✅ Guiding question worked! Confusion ↓ to {new_confusion:.2f}."
            )
        else:
            feedback_parts.append("Student still confused. Try a different angle.")

        if new_resolved and not gave_direct_answer:
            feedback_parts.append("🎉 Misconception resolved!")

        if self._done:
            feedback_parts.append(
                f"Episode complete. "
                f"Pre-quiz: {self._pre_quiz_score}/5 → Post-quiz: {self._post_quiz_score}/5. "
                f"Final reward: {reward:+.4f}. "
                f"Cumulative: {self._cumulative_reward:+.4f}."
            )

        obs = SocraticObservation(
            topic=self._topic,
            difficulty=self._difficulty,
            student_response=student_response,
            confusion_score=self._confusion_score,
            turn_number=self._turn_number,
            pre_quiz_score=self._pre_quiz_score,
            post_quiz_score=self._post_quiz_score,
            misconception=self._misconception,
            misconception_resolved=self._misconception_resolved,
            feedback=" ".join(feedback_parts),
            reward=reward,
            done=self._done,
        )
        return obs

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    def state(self, **kwargs) -> dict:
        """Return the full internal state as a plain dict (for inspection/logging)."""
        return {
            "topic": self._topic,
            "difficulty": self._difficulty,
            "misconception": self._misconception,
            "confusion_score": self._confusion_score,
            "turn_number": self._turn_number,
            "max_turns": MAX_TURNS,
            "pre_quiz_score": self._pre_quiz_score,
            "post_quiz_score": self._post_quiz_score,
            "misconception_resolved": self._misconception_resolved,
            "guiding_count": self._guiding_count,
            "done": self._done,
            "cumulative_reward": self._cumulative_reward,
        }

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _wrap_observation(self, socratic_obs: SocraticObservation) -> Observation:
        """
        Convert our SocraticObservation dataclass into an openenv Observation.
        All fields are passed as keyword arguments so openenv can serialise them.
        """
        return Observation(
            topic=socratic_obs.topic,
            difficulty=socratic_obs.difficulty,
            student_response=socratic_obs.student_response,
            confusion_score=socratic_obs.confusion_score,
            turn_number=socratic_obs.turn_number,
            pre_quiz_score=socratic_obs.pre_quiz_score,
            post_quiz_score=socratic_obs.post_quiz_score,
            misconception=socratic_obs.misconception,
            misconception_resolved=socratic_obs.misconception_resolved,
            feedback=socratic_obs.feedback,
            reward=socratic_obs.reward,
            done=socratic_obs.done,
        )