#!/usr/bin/env python3
"""server/app.py — Hugging Face Spaces UI for SocraticTeach-Env."""

import random

import gradio as gr

from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction


def render_observation(obs) -> str:
    return (
        f"Topic: {obs.topic}\n"
        f"Difficulty: {obs.difficulty}\n"
        f"Turn: {obs.turn_number}/10\n"
        f"Student response: {obs.student_response}\n"
        f"Confusion score: {obs.confusion_score:.2f}\n"
        f"Pre-quiz score: {obs.pre_quiz_score}/5\n"
        f"Post-quiz score: {obs.post_quiz_score}/5\n"
        f"Misconception: {obs.misconception}\n"
        f"Misconception resolved: {obs.misconception_resolved}\n"
        f"Reward: {obs.reward:.4f}\n"
        f"Done: {obs.done}\n"
        f"Feedback: {obs.feedback}"
    )


def start_episode(difficulty: str):
    env = DebugEnvironment()
    obs = env.reset(difficulty=difficulty, seed=random.randint(0, 2**31 - 1))

    history_lines = [
        "=== New Episode Started ===",
        f"Topic: {obs.topic}",
        f"Difficulty: {obs.difficulty}",
        f"Misconception: {obs.misconception}",
        f"Pre-quiz score: {obs.pre_quiz_score}/5",
        "",
        "Student response:",
        obs.student_response,
        "",
        "Feedback:",
        obs.feedback,
    ]

    return env, "\n".join(history_lines), render_observation(obs), ""


def step_episode(env, teacher_message: str, history: str):
    if env is None:
        return None, history, "No active episode. Please start a new episode first.", ""

    message = teacher_message.strip()
    if not message:
        return env, history, "Please enter a guiding message before submitting.", teacher_message

    action = TeacherAction(teacher_message=message)
    obs = env.step(action)

    step_lines = [
        "---",
        f"Teacher: {message}",
        f"Student: {obs.student_response}",
        f"Feedback: {obs.feedback}",
        f"Reward: {obs.reward:.4f}",
    ]

    if obs.done:
        step_lines.extend([
            "",
            "=== Episode Complete ===",
            f"Post-quiz score: {obs.post_quiz_score}/5",
            f"Misconception resolved: {obs.misconception_resolved}",
        ])

    updated_history = "\n".join([history, "\n".join(step_lines)])
    return env, updated_history, render_observation(obs), ""


def build_interface():
    with gr.Blocks(title="SocraticTeach-Env", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # SocraticTeach-Env
            Teach a simulated student using the Socratic method. Start an episode, then enter a guiding question or hint each turn.
            """
        )

        with gr.Row():
            difficulty = gr.Dropdown(
                choices=["easy", "medium", "hard"],
                value="easy",
                label="Difficulty",
                info="Choose the teaching difficulty for this episode.",
            )
            start_button = gr.Button("Start Episode")

        history = gr.Textbox(
            label="Episode History",
            lines=18,
            interactive=False,
            value="Press Start Episode to begin.",
        )
        observation = gr.Textbox(
            label="Current Observation",
            lines=14,
            interactive=False,
            value="No active episode.",
        )

        teacher_message = gr.Textbox(
            label="Teacher Message",
            placeholder="Ask a guiding question or hint, but do not give the answer directly.",
            lines=2,
        )
        submit_button = gr.Button("Submit Message")

        env_state = gr.State(value=None)

        start_button.click(
            fn=start_episode,
            inputs=[difficulty],
            outputs=[env_state, history, observation, teacher_message],
        )
        submit_button.click(
            fn=step_episode,
            inputs=[env_state, teacher_message, history],
            outputs=[env_state, history, observation, teacher_message],
        )

    return demo


if __name__ == "__main__":
    app = build_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)
