"""
client.py — SocraticTeach-Env
OpenEnv client that connects to the DebugEnvironment and runs a sample episode.
"""

try:
    from openenv.core import GenericEnvClient, Action, Observation
except ImportError:
    from .mock_openenv import GenericEnvClient, Action, Observation


class SocraticTeachClient(GenericEnvClient):
    """
    Client for the SocraticTeach-Env environment.

    Usage
    -----
    client = SocraticTeachClient(env_id="debug_env")
    obs    = client.reset(difficulty="medium")

    while not obs.done:
        action = Action(teacher_message="Why do you think that always happens?")
        obs    = client.step(action)

    client.close()
    """

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def reset(self, difficulty: str = "medium", seed: int | None = None) -> Observation:
        """
        Start a new episode.

        Parameters
        ----------
        difficulty : "easy" | "medium" | "hard"
        seed       : optional random seed for reproducibility
        """
        kwargs: dict = {"difficulty": difficulty}
        if seed is not None:
            kwargs["seed"] = seed
        return super().reset(**kwargs)

    def step(self, teacher_message: str) -> Observation:
        """
        Send a teacher message and receive the next observation.

        Parameters
        ----------
        teacher_message : str
            A Socratic guiding question or hint (no direct answers!).
        """
        action = Action(teacher_message=teacher_message)
        return super().step(action)

    # ------------------------------------------------------------------
    # Pretty-print helper (optional, useful for debugging / demos)
    # ------------------------------------------------------------------

    @staticmethod
    def pretty_print(obs: Observation, turn: int | None = None) -> None:
        label = f"Turn {turn}" if turn is not None else "Observation"
        sep = "─" * 60
        print(f"\n{sep}")
        print(f"  {label}")
        print(sep)
        print(f"  Topic       : {obs.topic}")
        print(f"  Difficulty  : {obs.difficulty}")
        print(f"  Turn        : {obs.turn_number}/10")
        print(f"  Confusion   : {obs.confusion_score:.2f}")
        print(f"  Resolved    : {obs.misconception_resolved}")
        print(f"  Student     : {obs.student_response}")
        print(f"  Feedback    : {obs.feedback}")
        print(f"  Reward      : {obs.reward:+.4f}")
        print(f"  Done        : {obs.done}")
        if obs.done:
            print(f"\n  ── Final Results ──")
            print(f"  Pre-quiz    : {obs.pre_quiz_score}/5")
            print(f"  Post-quiz   : {obs.post_quiz_score}/5")
            print(f"  Total reward: {obs.reward:+.4f}")
        print(sep)


# ---------------------------------------------------------------------------
# Demo: run one full episode with a hand-crafted teacher policy
# ---------------------------------------------------------------------------

def _demo_teacher_policy(obs: Observation) -> str:
    """
    A simple rule-based teacher that always asks guiding questions.
    Replace this with your RL agent.
    """
    guiding_questions = [
        "Why do you think that is always the case?",
        "What if I gave you a counter-example — would that change your mind?",
        "Consider a situation where the condition is False from the start. What happens then?",
        "Think about what the loop condition actually checks each iteration.",
        "What happens when the base case is reached in a recursive function?",
        "Can you think of any example where this might not hold?",
        "What if the input was already sorted — would the algorithm behave differently?",
        "How would you explain this to someone who has never coded before?",
        "What do you think would happen if we removed that constraint entirely?",
        "Does the definition you gave always hold, or only under certain conditions?",
    ]
    idx = min(obs.turn_number - 1, len(guiding_questions) - 1)
    return guiding_questions[idx]


if __name__ == "__main__":
    import sys

    difficulty = sys.argv[1] if len(sys.argv) > 1 else "medium"

    print(f"\n{'═' * 60}")
    print(f"  SocraticTeach-Env Demo  |  difficulty={difficulty}")
    print(f"{'═' * 60}")

    client = SocraticTeachClient(env_id="debug_env")

    try:
        obs = client.reset(difficulty=difficulty, seed=42)
        SocraticTeachClient.pretty_print(obs, turn=0)

        cumulative_reward = 0.0

        while not obs.done:
            teacher_msg = _demo_teacher_policy(obs)
            print(f"\n  [Teacher] → {teacher_msg}")
            obs = client.step(teacher_msg)
            cumulative_reward += obs.reward
            SocraticTeachClient.pretty_print(obs, turn=obs.turn_number)

        print(f"\n  Cumulative reward across episode: {cumulative_reward:+.4f}")

    finally:
        client.close()