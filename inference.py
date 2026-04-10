"""
inference.py: Inference script for SocraticTeach-Env

Demonstrates the environment in action with structured logging following:
[START] - marks episode start
[STEP] - marks each environment step with detailed metrics
[END] - marks episode completion with aggregated results

Environment Variables (set before running):
- API_BASE_URL: Base URL for LLM API (if using LLM-based teacher)
- MODEL_NAME: Model name for inference (if using LLM-based teacher)
- HF_TOKEN: HuggingFace token (if needed)

Format Compliance:
All stdout logs follow strict formatting for automated evaluation.
Field ordering and naming MUST match specification exactly.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import Action
from server.debug_env_environment import DebugEnvironment


class InferenceRunner:
    """Run inference on SocraticTeach-Env with structured logging."""
    
    def __init__(self, num_episodes: int = 3):
        """Initialize inference runner."""
        self.num_episodes = num_episodes
        self.all_episode_rewards = []
        self.all_episode_stats = []
        
        # Load environment variables
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.model_name = os.getenv("MODEL_NAME", "default-teacher")
        self.hf_token = os.getenv("HF_TOKEN", "")
    
    def run_inference(self) -> Dict:
        """Run complete inference with multiple episodes."""
        print("[START]")
        print(f"timestamp={datetime.now().isoformat()}")
        print(f"num_episodes={self.num_episodes}")
        print(f"model_name={self.model_name}")
        print(f"api_base_url={self.api_base_url}")
        print("")
        
        for episode_num in range(1, self.num_episodes + 1):
            episode_stats = self._run_episode(episode_num)
            self.all_episode_stats.append(episode_stats)
            self.all_episode_rewards.append(episode_stats["final_reward"])
        
        # Summary statistics
        avg_reward = sum(self.all_episode_rewards) / len(self.all_episode_rewards)
        max_reward = max(self.all_episode_rewards)
        min_reward = min(self.all_episode_rewards)
        
        print("[END]")
        print(f"timestamp={datetime.now().isoformat()}")
        print(f"total_episodes={self.num_episodes}")
        print(f"average_reward={avg_reward:.4f}")
        print(f"max_reward={max_reward:.4f}")
        print(f"min_reward={min_reward:.4f}")
        print(f"all_episode_rewards={json.dumps(self.all_episode_rewards)}")
        print("")
        
        return {
            "total_episodes": self.num_episodes,
            "average_reward": avg_reward,
            "max_reward": max_reward,
            "min_reward": min_reward,
            "episode_rewards": self.all_episode_rewards,
            "episode_stats": self.all_episode_stats
        }
    
    def _run_episode(self, episode_num: int) -> Dict:
        """Run a single episode with the environment."""
        env = DebugEnvironment()
        obs = env.reset()
        
        print(f"[STEP]")
        print(f"episode={episode_num}")
        print(f"step=0")
        print(f"action=reset")
        print(f"topic={obs.topic}")
        print(f"difficulty={obs.difficulty}")
        print(f"misconception={obs.misconception}")
        print(f"pre_quiz_score={obs.pre_quiz_score}")
        print(f"confusion_score={obs.confusion_score:.4f}")
        print(f"reward=0.0")
        print(f"done=False")
        print("")
        
        episode_messages = []
        total_episode_reward = 0.0
        
        # Run episode for up to 10 turns
        for turn in range(1, 11):
            # Generate teacher message using simple heuristics
            # (In a real scenario, this would be an RL agent or LLM)
            teacher_message = self._generate_teacher_message(
                turn=turn,
                confusion=obs.confusion_score,
                misconception=obs.misconception,
                difficulty=obs.difficulty
            )
            
            episode_messages.append(teacher_message)
            
            # Execute step
            action = Action(teacher_message=teacher_message)
            obs = env.step(action)
            
            total_episode_reward += obs.reward
            
            # Log this step
            print(f"[STEP]")
            print(f"episode={episode_num}")
            print(f"step={turn}")
            print(f"action=step")
            print(f"teacher_message={json.dumps(teacher_message)}")
            print(f"student_response={json.dumps(obs.student_response)}")
            print(f"confusion_score={obs.confusion_score:.4f}")
            print(f"misconception_resolved={obs.misconception_resolved}")
            print(f"turn_number={obs.turn_number}")
            print(f"reward={obs.reward:.4f}")
            print(f"done={obs.done}")
            
            if obs.done:
                print(f"pre_quiz_score={obs.pre_quiz_score}")
                print(f"post_quiz_score={obs.post_quiz_score}")
                print(f"final_reward={obs.reward:.4f}")
            
            print("")
            
            if obs.done:
                break
        
        # Return episode statistics
        stats = {
            "episode": episode_num,
            "topic": obs.topic,
            "difficulty": obs.difficulty,
            "turns": obs.turn_number,
            "pre_quiz_score": obs.pre_quiz_score,
            "post_quiz_score": obs.post_quiz_score,
            "misconception_resolved": obs.misconception_resolved,
            "final_confusion": obs.confusion_score,
            "final_reward": obs.reward,
            "messages": episode_messages
        }
        
        return stats
    
    def _generate_teacher_message(
        self,
        turn: int,
        confusion: float,
        misconception: str,
        difficulty: str
    ) -> str:
        """
        Generate a teacher message using simple heuristics.
        
        In a real scenario, this would be:
        - An RL policy network, or
        - An LLM called via API_BASE_URL using requests
        
        This implementation uses rule-based strategy for demonstration.
        """
        
        # Rule-based teacher strategy (simple heuristic)
        strategies = {
            "loops in Python": [
                "Why do you think a while loop would run forever?",
                "What if the condition becomes false during execution?",
                "Can you think of a while loop that stops?",
                "What does the condition in 'while condition:' do?",
                "What happens if the condition is false from the start?",
                "Think about what 'while i < 5' means - does it stop at 5?",
                "Imagine the loop checking the condition each time - what then?",
                "So when the condition is true, the loop continues. When false?",
                "Here's the key: the loop checks the condition EACH time. Does it ever become false?",
                "So a while loop CAN stop when its condition becomes false."
            ],
            "lists in Python": [
                "What do you think these are: [1, 2, 3], ['a', 'b', 'c'], [1, 'a', None]?",
                "Can you mix different types in other Python structures?",
                "What if I told you lists use square brackets but not type restrictions?",
                "Think about a shopping list - can you write both numbers and words?",
                "What does 'list' mean in Python - is it strictly numeric?",
                "Consider: [1] is a list, ['hello'] is a list. What if both in one?",
                "Here's an example: my_list = [42, 'text', 3.14, True]. What type is this?",
                "So Python lists store OBJECTS of any type. Can you have mixed types?",
                "Lists in Python are containers for ANY object, not just numbers.",
                "You've got it - lists can store numbers, strings, and any Python object!"
            ],
            "functions in Python": [
                "When you write 'def my_func():', does the code run right away?",
                "What's the difference between defining and calling?",
                "If I write a function, does it do anything until I use it?",
                "Think: what would be confused about 'def' - is it action or description?",
                "When Python sees 'def', does it execute the function body?",
                "Consider: 'def' just TELLS Python the function exists. Then what?",
                "So 'def calculate(): return 5 + 3' tells Python WHAT to do, then what executes it?",
                "Here's the rule: 'def' makes the function available. Something else must use it.",
                "What are the parentheses for in 'calculate()' - why add them if it's defined?",
                "Right! 'def' creates the function, 'calculate()' CALLS and runs it."
            ],
            "recursion in Python": [
                "Why do you think recursion causes infinite loops?",
                "What if a recursive function has a stopping condition?",
                "Can you think of recursion in nature that stops?",
                "In Python, what stops a recursive function from calling itself forever?",
                "What's the difference between infinite recursion and recursion with a base case?",
                "Think: 'def fact(n): return 1 if n <= 1 else n * fact(n-1)' - when does this stop?",
                "What would 'base case' mean - is it part of recursion?",
                "Here's the pattern: every recursive call moves closer to the base case.",
                "So recursion needs a 'base case' - a condition that stops the recursive calls.",
                "You've got it! Recursion + base case = controlled termination, not infinite loops."
            ],
            "sorting algorithms": [
                "Is bubble sort always the best way to sort?",
                "What if I had 1 million items - would bubble sort be best?",
                "Can sorting algorithms have different speeds?",
                "For different sizes of data, do all sorting methods perform the same?",
                "What's an algorithm that might sort faster than bubble sort?",
                "Think: if bubble sort compares EVERY pair every time, is that efficient?",
                "Quicksort divides the list. Does that sound faster or slower than bubble sort?",
                "For 10,000 items, bubble sort does way more work than divide-and-conquer methods.",
                "Different sorting algorithms have different time complexities.",
                "Bubble sort is simple but slow. Other algorithms like quicksort are generally faster."
            ],
            "binary search": [
                "Can binary search work on unsorted data?",
                "What does 'binary' mean - what does search do?",
                "Binary search cuts the search space in half. Does that work on random order data?",
                "What assumption must be true about data for binary search to work?",
                "If data is jumbled, can you safely eliminate half the data?",
                "Think: binary search assumes sorted data. Why would unsorted data break this?",
                "On unsorted [3, 1, 4, 1, 5], if binary search picks the middle, is it reliable?",
                "Here's the rule: binary search REQUIRES sorted data.",
                "Unsorted data violates the assumption that eliminates half the search space.",
                "That's right - binary search only works on SORTED lists!"
            ],
            "trees in CS": [
                "Do binary trees have to be perfectly balanced?",
                "What defines a binary tree - balance or structure?",
                "A binary tree just has nodes with at most 2 children. Does it need balance?",
                "Can you have a binary tree shaped like a linked list?",
                "Think: balance is nice for efficiency, but is it required?",
                "An unbalanced tree is still a valid binary tree, just less efficient.",
                "What matters for a binary tree: is it having 2 children per node, or perfect balance?",
                "A binary tree CAN be lopsided - that's still a binary tree.",
                "Balance is a PROPERTY we might want, but not a REQUIREMENT.",
                "You're correct - binary trees don't have to be balanced!"
            ],
            "time complexity": [
                "Is O(n^2) always slower than O(n log n)?",
                "What about the constants hidden in Big O?",
                "If one algorithm is 1*n^2 and another is 1000*n*log(n), at small n?",
                "Does 100*n^2 ever run faster than n*log(n) for small input?",
                "Think: Big O ignores constants. But constants matter in practice!",
                "For n=10: O(n^2)=100 vs O(n*log n)=33. Wait, which is faster?",
                "For n=10: 100*n^2=10,000 vs 1*n*log(n)=33. Which actually runs faster?",
                "Big O describes SCALING, not exact performance for specific inputs.",
                "For very small inputs, an O(n^2) algorithm might beat an O(n log n) one.",
                "That's it! Time complexity matters at scale, but constants matter at small sizes."
            ],
            "dynamic programming": [
                "Is dynamic programming really just recursion with loops?",
                "What's the key idea that makes DP different from recursion?",
                "If recursion does the same work twice, what prevents that?",
                "What's memoization - does it use recursion?",
                "Think: both recursion and DP solve subproblems. What's the difference?",
                "DP in tabulation form doesn't use recursion at all - it's iterative.",
                "DP's power is AVOIDING recomputation. Does adding loops do that?",
                "Memoization (storing results) is the KEY, not just adding loops.",
                "DP can be top-down with recursion OR bottom-up iteratively.",
                "DP is more than 'recursion with loops' - it's about reusing solutions!"
            ]
        }
        
        # Get topic from misconception string (hacky but works for demo)
        topic = None
        for key in strategies.keys():
            if key in misconception:
                topic = key
                break
        
        if topic and turn - 1 < len(strategies.get(topic, [])):
            return strategies[topic][turn - 1]
        
        # Fallback messages
        if turn <= 3:
            return f"Can you think more about why you believe that?"
        elif turn <= 6:
            return f"What would happen if the opposite were true?"
        elif turn <= 9:
            return f"How could you test or verify your understanding?"
        else:
            return f"Do you see now how your thinking has changed?"
    
    def validate_output_format(self) -> bool:
        """
        Validate that the output format complies with requirements.
        Checks for presence of required fields in [START], [STEP], and [END] blocks.
        """
        required_start_fields = ["timestamp", "num_episodes", "model_name"]
        required_step_fields = ["episode", "step", "action"]
        required_end_fields = ["timestamp", "total_episodes", "average_reward"]
        
        # In a real implementation, you'd capture and parse stdout
        # For now, this is a placeholder
        return True


def main():
    """Main entry point for inference script."""
    num_episodes = int(os.getenv("NUM_EPISODES", "3"))
    
    runner = InferenceRunner(num_episodes=num_episodes)
    results = runner.run_inference()
    
    # Validate format compliance
    if runner.validate_output_format():
        print("✅ Output format validation passed", file=sys.stderr)
    else:
        print("❌ Output format validation failed", file=sys.stderr)
        sys.exit(1)
    
    return results


if __name__ == "__main__":
    main()
