"""
app.py: Gradio interface for SocraticTeach-Env on HuggingFace Spaces
"""

import gradio as gr
import json
from models import Observation, Action
from server.debug_env_environment import DebugEnvironment


# Global environment instance
env = DebugEnvironment()
current_obs = None


def reset_environment():
    """Reset the environment and start a new episode."""
    global env, current_obs
    env = DebugEnvironment()
    current_obs = env.reset()
    
    return (
        f"<b>Topic:</b> {current_obs.topic}<br>"
        f"<b>Difficulty:</b> {current_obs.difficulty}<br>"
        f"<b>Misconception:</b> {current_obs.misconception}<br>"
        f"<b>Student says:</b> {current_obs.student_response}<br>"
        f"<b>Confusion Score:</b> {current_obs.confusion_score:.2f}",
        current_obs.feedback
    )


def step_environment(teacher_message: str):
    """Execute one step in the environment."""
    global env, current_obs
    
    if env.topic is None:
        return "Please reset the environment first!", ""
    
    if not teacher_message.strip():
        return "Please enter a teacher message!", ""
    
    # Create action and execute step
    action = Action(teacher_message=teacher_message)
    current_obs = env.step(action)
    
    # Format state info
    state_info = (
        f"<b>Turn:</b> {current_obs.turn_number}/10<br>"
        f"<b>Student Response:</b> {current_obs.student_response}<br>"
        f"<b>Confusion Score:</b> {current_obs.confusion_score:.2f}<br>"
        f"<b>Misconception Resolved:</b> {current_obs.misconception_resolved}<br>"
        f"<b>Reward This Turn:</b> {current_obs.reward:.3f}"
    )
    
    # Add quiz scores if episode is done
    if current_obs.done:
        state_info += (
            f"<br><b>Pre-Quiz Score:</b> {current_obs.pre_quiz_score}/5<br>"
            f"<b>Post-Quiz Score:</b> {current_obs.post_quiz_score}/5<br>"
            f"<b>Final Reward:</b> {current_obs.reward:.3f}"
        )
    
    episode_status = "✅ EPISODE COMPLETE" if current_obs.done else f"Turn {current_obs.turn_number}/10"
    
    return state_info, f"[{episode_status}] {current_obs.feedback}"


def get_environment_state():
    """Get current environment state."""
    global env
    state = env.state()
    return json.dumps(state, indent=2)


# Create Gradio interface
with gr.Blocks(title="SocraticTeach-Env") as demo:
    gr.Markdown("""
    # 🎓 SocraticTeach-Env: Socratic Teaching RL Environment
    
    An RL environment where an AI teacher learns to teach a student using the Socratic method.
    The teacher must ask guiding questions and hints—never directly state the answer!
    
    ### How it works:
    1. **Reset** the environment to assign a topic and difficulty level
    2. **Send teacher messages** using guiding questions (why, what if, how would you, etc.)
    3. Watch the student's confusion score decrease as they learn
    4. After 10 turns, the environment runs a post-quiz to calculate the final reward
    5. The better you teach using Socratic method, the higher the reward!
    
    ### Scoring:
    - **Quiz Delta** (45%): Improvement in quiz score pre vs post-teaching
    - **Misconception Bonus** (15%): Extra reward if student's misconception is resolved
    - **Teaching Quality** (10-25%): More reward for efficient teaching (< 8 turns)
    - **Efficiency Penalty** (-5%): Penalty based on number of turns used
    
    ### ⚠️ Important Rules:
    - ✅ Use Socratic method: "Why do you think that?", "What would happen if...", "Can you explain..."
    - ❌ Avoid direct answers: Don't say "the answer is", "it means", "recursion is"
    """)
    
    with gr.Row():
        with gr.Column():
            reset_btn = gr.Button("🔄 Reset Environment", variant="primary", size="lg")
            state_output = gr.Markdown("No episode started yet")
            feedback_output = gr.Markdown("")
        
        with gr.Column():
            gr.Markdown("### Current State")
            state_json = gr.Code(language="json", label="Environment State", interactive=False)
    
    gr.Markdown("---")
    
    with gr.Row():
        teacher_input = gr.Textbox(
            label="Teacher Message",
            placeholder="Enter a guiding question or hint (e.g., 'Why do you think while loops always run forever?')",
            lines=3
        )
        step_btn = gr.Button("📤 Send Message & Step", variant="primary", size="lg")
    
    step_output = gr.Markdown("")
    
    # Event handlers
    reset_btn.click(
        fn=reset_environment,
        outputs=[state_output, feedback_output]
    ).then(
        fn=get_environment_state,
        outputs=state_json
    )
    
    step_btn.click(
        fn=step_environment,
        inputs=[teacher_input],
        outputs=[state_output, step_output]
    ).then(
        fn=get_environment_state,
        outputs=state_json
    )
    
    gr.Markdown("""
    ---
    ### Example Topics & Misconceptions:
    
    **Easy:**
    - Loops: "while loops always run forever"
    - Lists: "lists can only store numbers"
    - Functions: "functions run automatically when defined"
    
    **Medium:**
    - Recursion: "recursion always causes infinite loops"
    - Sorting: "bubble sort is always the fastest"
    - Binary Search: "binary search works on unsorted lists"
    
    **Hard:**
    - Trees: "binary trees must always be balanced"
    - Complexity: "O(n^2) is always slower than O(n log n)"
    - DP: "dynamic programming is just recursion with loops"
    """)


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
