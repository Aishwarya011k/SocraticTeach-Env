"""
SocraticTeach-Env: Debug Environment
The main OpenEnv environment implementing the Socratic teaching paradigm.
"""

import random
import sys
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from openenv.core import Environment, Action, Observation

# Handle imports from models - try multiple paths for flexibility
try:
    # Try package import first
    from debug_env.models import (
        Action as TeacherAction,
        Observation as TeacherObservation,
        TOPICS_BY_DIFFICULTY,
        MISCONCEPTIONS_DB,
        get_quiz_for_topic,
    )
except ImportError:
    try:
        # Fallback to parent directory import
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from models import (
            Action as TeacherAction,
            Observation as TeacherObservation,
            TOPICS_BY_DIFFICULTY,
            MISCONCEPTIONS_DB,
            get_quiz_for_topic,
        )
    except ImportError as e:
        # Last resort: try relative import with parent module
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, parent_dir)
        from models import (
            Action as TeacherAction,
            Observation as TeacherObservation,
            TOPICS_BY_DIFFICULTY,
            MISCONCEPTIONS_DB,
            get_quiz_for_topic,
        )


# Guiding words that indicate Socratic method
GUIDING_WORDS = {"why", "what if", "consider", "think about", "what happens when",
                   "how would you", "imagine", "explain", "describe", "compare",
                   "contrast", "analyze"}

# Words that directly state answers (anti-cheat)
DIRECT_ANSWER_WORDS = {"the answer is", "it means", "this is", "equals", "is the",
                        "loops are", "lists are", "functions are", "recursion is",
                        "sorting is", "binary search", "trees are", "complexity is",
                        "programming is", "always runs"}


class DebugEnvironment(Environment):
    """
    DebugEnvironment: Socratic Teaching RL Environment
    
    An agent learns to teach a student using the Socratic method.
    The agent must ask guiding questions and hints, never directly stating answers.
    """

    def __init__(self):
        """Initialize the DebugEnvironment."""
        super().__init__()
        
        # Episode state
        self.topic: Optional[str] = None
        self.difficulty: Optional[str] = None
        self.misconception: Optional[str] = None
        self.turn_number: int = 0
        self.max_turns: int = 10
        
        # Student state
        self.confusion_score: float = 0.8  # Start confused (0.0 = clear, 1.0 = very confused)
        self.student_response: str = ""
        self.misconception_resolved: bool = False
        self.post_quiz_score: int = 0
        self.pre_quiz_score: int = 0
        
        # Quiz tracking
        self.pre_quiz_responses: List[int] = []
        self.post_quiz_responses: List[int] = []
        
        # Reward tracking
        self.cumulative_reward: float = 0.0
        self.turn_rewards: List[float] = []
        
        # Difficulty-specific state
        self.guiding_count: int = 0
        self.required_guiding_count: Dict[str, int] = {
            "easy": 3,
            "medium": 5,
            "hard": 7
        }

    def reset(self, **kwargs) -> TeacherObservation:
        """
        Reset the environment and start a new episode.
        
        Returns:
            TeacherObservation: Initial observation with pre-quiz results
        """
        # Reset episode state
        self.turn_number = 0
        self.cumulative_reward = 0.0
        self.turn_rewards = []
        self.guiding_count = 0
        self.misconception_resolved = False
        
        # Randomly select difficulty
        self.difficulty = random.choice(["easy", "medium", "hard"])
        self.topic = random.choice(TOPICS_BY_DIFFICULTY[self.difficulty])
        self.misconception = MISCONCEPTIONS_DB[self.topic]
        
        # Initialize student confusion
        self.confusion_score = 0.8
        
        # Run pre-quiz
        self._run_pre_quiz()
        
        # Initial student response (student states their misconception)
        self.student_response = self._generate_initial_student_response()
        
        # Create initial observation
        obs = TeacherObservation(
            topic=self.topic,
            difficulty=self.difficulty,
            student_response=self.student_response,
            confusion_score=self.confusion_score,
            turn_number=self.turn_number,
            pre_quiz_score=self.pre_quiz_score,
            post_quiz_score=0,
            misconception=self.misconception,
            misconception_resolved=False,
            feedback=f"Student believes: {self.misconception}. Pre-quiz score: {self.pre_quiz_score}/5",
            reward=0.0,
            done=False
        )
        
        return obs

    def step(self, action: TeacherAction, **kwargs) -> TeacherObservation:
        """
        Execute one step: teacher sends message, student responds.
        
        Args:
            action: TeacherAction with teacher_message field
            
        Returns:
            TeacherObservation: Updated observation after this turn
        """
        self.turn_number += 1
        teacher_message = action.teacher_message
        
        # Check if teacher is using Socratic method or directly answering
        contains_guiding = any(word in teacher_message.lower() for word in GUIDING_WORDS)
        contains_direct = any(phrase in teacher_message.lower() for phrase in DIRECT_ANSWER_WORDS)
        
        # Update guiding count
        if contains_guiding:
            self.guiding_count += 1
        
        # Calculate turn reward
        turn_reward = self._calculate_turn_reward(
            contains_guiding=contains_guiding,
            contains_direct=contains_direct
        )
        self.turn_rewards.append(turn_reward)
        self.cumulative_reward += turn_reward
        
        # Simulate student response
        self.student_response = self._simulate_student_response(
            teacher_message=teacher_message,
            contains_guiding=contains_guiding,
            contains_direct=contains_direct
        )
        
        # Update confusion score based on teacher quality
        if contains_guiding and not contains_direct:
            self.confusion_score = max(0.0, self.confusion_score - 0.1)
        
        # Check if misconception is resolved
        self._check_misconception_resolution()
        
        # Determine if episode is done
        done = (self.turn_number >= self.max_turns)
        
        # Run post-quiz if done
        if done:
            self._run_post_quiz()
            final_reward = self._calculate_final_reward()
            self.cumulative_reward = final_reward
        else:
            final_reward = turn_reward
        
        # Create observation
        feedback = self._generate_feedback(
            contains_guiding=contains_guiding,
            contains_direct=contains_direct,
            done=done
        )
        
        obs = TeacherObservation(
            topic=self.topic,
            difficulty=self.difficulty,
            student_response=self.student_response,
            confusion_score=self.confusion_score,
            turn_number=self.turn_number,
            pre_quiz_score=self.pre_quiz_score,
            post_quiz_score=self.post_quiz_score if done else 0,
            misconception=self.misconception,
            misconception_resolved=self.misconception_resolved,
            feedback=feedback,
            reward=final_reward if done else turn_reward,
            done=done
        )
        
        return obs

    def state(self, **kwargs) -> Dict:
        """
        Get current state of the environment.
        
        Returns:
            Dict with all state information
        """
        return {
            "topic": self.topic,
            "difficulty": self.difficulty,
            "turn_number": self.turn_number,
            "max_turns": self.max_turns,
            "confusion_score": self.confusion_score,
            "misconception": self.misconception,
            "misconception_resolved": self.misconception_resolved,
            "pre_quiz_score": self.pre_quiz_score,
            "post_quiz_score": self.post_quiz_score,
            "guiding_count": self.guiding_count,
            "cumulative_reward": self.cumulative_reward,
            "student_response": self.student_response,
        }

    # ==================== HELPER METHODS ====================

    def _run_pre_quiz(self) -> None:
        """Simulate pre-quiz: student starts with 1-2 correct answers due to misconception."""
        quiz = get_quiz_for_topic(self.topic)
        # Simulate poor pre-quiz performance (1-2 out of 5 due to misconception)
        self.pre_quiz_score = random.randint(1, 2)
        # Store simulated responses (for consistency)
        self.pre_quiz_responses = [0] * len(quiz)  # All wrong except 1-2
        self.pre_quiz_responses[0] = 1  # One or two correct
        if random.random() < 0.5 and len(self.pre_quiz_responses) > 1:
            self.pre_quiz_responses[1] = 1

    def _run_post_quiz(self) -> None:
        """Simulate post-quiz: score improves based on teaching quality."""
        base_score = max(self.pre_quiz_score + 1, 2)  # At least +1 improvement
        
        if self.misconception_resolved:
            # Significant improvement if misconception resolved
            self.post_quiz_score = min(5, base_score + 2 + random.randint(0, 1))
        else:
            # Minimal improvement if misconception not resolved
            self.post_quiz_score = min(5, base_score + random.randint(0, 1))

    def _generate_initial_student_response(self) -> str:
        """Generate initial student response expressing the misconception."""
        responses = {
            "a while loop always runs forever": "I think while loops always run forever, right?",
            "lists can only store numbers": "Lists only store numbers, like arrays in other languages.",
            "a function runs automatically when defined": "When I write def my_func(), it runs immediately.",
            "recursion always causes infinite loops": "I'm scared of recursion because it always causes crashes.",
            "bubble sort is always the fastest": "Bubble sort is the fastest way to sort, isn't it?",
            "binary search works on unsorted lists": "I search through unsorted data with binary search.",
            "a binary tree must always be balanced": "A binary tree must have equal left and right subtrees.",
            "O(n^2) is always slower than O(n log n) for all inputs": "O(n^2) is always slower than O(n log n).",
            "dynamic programming is just recursion with loops": "DP is just recursion with loops added.",
        }
        return responses.get(self.misconception, "I don't understand this topic.")

    def _simulate_student_response(
        self,
        teacher_message: str,
        contains_guiding: bool,
        contains_direct: bool
    ) -> str:
        """
        Simulate student response based on teacher message quality.
        """
        if contains_direct:
            # Student acknowledges but doesn't truly learn
            return "Oh okay, I see... I think I get it now."
        
        if contains_guiding:
            # Student shows partial understanding
            return "Hmm, I never thought about it that way... Let me think about it."
        
        # Default: student reiterates misconception
        return f"But I still think: {self.misconception}"

    def _check_misconception_resolution(self) -> None:
        """
        Check if misconception has been resolved based on:
        - Confusion score dropping below 0.3
        - After turn 5 minimum (hard problems need more turns)
        - Enough guiding questions asked
        """
        required = self.required_guiding_count.get(self.difficulty, 5)
        
        if (self.confusion_score < 0.3 and
            self.turn_number > 5 and
            self.guiding_count >= required):
            self.misconception_resolved = True

    def _calculate_turn_reward(self, contains_guiding: bool, contains_direct: bool) -> float:
        """
        Calculate reward for a single turn during episode.
        """
        turn_reward = 0.0
        
        # Reward for using Socratic method (guiding questions)
        if contains_guiding and not contains_direct:
            turn_reward = 0.05
        
        # Penalty for directly stating answers
        if contains_direct:
            turn_reward = -0.1
        
        return turn_reward

    def _calculate_final_reward(self) -> float:
        """
        Calculate final reward at end of episode.
        
        Formula:
        quiz_delta = (post_quiz_score - pre_quiz_score) / 5.0
        misconception_bonus = 0.15 if misconception_resolved else 0.0
        efficiency_penalty = (turn_number / 10) * 0.05
        teaching_quality = 0.25 if misconception_resolved and turn_number < 8 else 0.10
        final_reward = (quiz_delta * 0.45) + misconception_bonus + teaching_quality - efficiency_penalty
        """
        quiz_delta = (self.post_quiz_score - self.pre_quiz_score) / 5.0
        misconception_bonus = 0.15 if self.misconception_resolved else 0.0
        efficiency_penalty = (self.turn_number / 10.0) * 0.05
        teaching_quality = 0.25 if (self.misconception_resolved and self.turn_number < 8) else 0.10
        
        final_reward = (quiz_delta * 0.45) + misconception_bonus + teaching_quality - efficiency_penalty
        
        # Ensure reward is in valid range
        return max(-0.5, min(1.0, final_reward))

    def _generate_feedback(self, contains_guiding: bool, contains_direct: bool, done: bool) -> str:
        """Generate human-readable feedback for this turn."""
        if done:
            status = "EPISODE COMPLETE" if self.misconception_resolved else "Episode ended"
            return (f"{status}. Misconception resolved: {self.misconception_resolved}. "
                    f"Pre-quiz: {self.pre_quiz_score}/5, Post-quiz: {self.post_quiz_score}/5")
        
        if contains_direct:
            return "⚠️  Teacher stated the answer directly. Student not truly learning."
        
        if contains_guiding:
            progress = "Student is thinking deeper" if self.confusion_score < 0.5 else "Student seems confused"
            return f"✓ Socratic approach working. {progress}. Confusion: {self.confusion_score:.2f}"
        
        return "Teacher message is neutral. No clear teaching strategy detected."
