#!/usr/bin/env python3
"""
server/api.py — FastAPI server exposing OpenEnv endpoints for SocraticTeach-Env
Compliant with OpenEnv specification for validator checks
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction

# Initialize FastAPI app
app = FastAPI(
    title="SocraticTeach-Env",
    description="OpenEnv RL environment for training AI teachers using the Socratic method",
    version="1.0.0"
)

# Global environment instance
env_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize environment on startup"""
    global env_instance
    env_instance = DebugEnvironment()
    print("✓ Environment initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "SocraticTeach-Env"}

@app.post("/reset")
async def reset(difficulty: str = "easy", topic_index: int = None, seed: int = None):
    """
    Reset the environment and start a new episode
    
    Args:
        difficulty: "easy", "medium", or "hard"
        topic_index: (optional) specific topic index
        seed: (optional) random seed for reproducibility
        
    Returns:
        Initial observation
    """
    global env_instance
    try:
        kwargs = {"difficulty": difficulty}
        if seed is not None:
            kwargs["seed"] = seed
        if topic_index is not None:
            kwargs["topic_index"] = topic_index
            
        obs = env_instance.reset(**kwargs)
        return {
            "topic": obs.topic,
            "difficulty": obs.difficulty,
            "student_response": obs.student_response,
            "confusion_score": obs.confusion_score,
            "turn_number": obs.turn_number,
            "pre_quiz_score": obs.pre_quiz_score,
            "post_quiz_score": obs.post_quiz_score,
            "misconception": obs.misconception,
            "misconception_resolved": obs.misconception_resolved,
            "feedback": obs.feedback,
            "reward": obs.reward,
            "done": obs.done,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(teacher_message: str):
    """
    Submit a teacher action and step the environment
    
    Args:
        teacher_message: The teacher's guiding question/hint/analogy
        
    Returns:
        Updated observation
    """
    global env_instance
    try:
        action = TeacherAction(teacher_message=teacher_message)
        obs = env_instance.step(action)
        return {
            "topic": obs.topic,
            "difficulty": obs.difficulty,
            "student_response": obs.student_response,
            "confusion_score": obs.confusion_score,
            "turn_number": obs.turn_number,
            "pre_quiz_score": obs.pre_quiz_score,
            "post_quiz_score": obs.post_quiz_score,
            "misconception": obs.misconception,
            "misconception_resolved": obs.misconception_resolved,
            "feedback": obs.feedback,
            "reward": obs.reward,
            "done": obs.done,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    """
    Get the current environment state
    
    Returns:
        Full internal state dict
    """
    global env_instance
    try:
        return env_instance.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/docs")
async def docs():
    """API documentation (Swagger UI)"""
    return {"message": "OpenAPI docs available at /docs or /redoc"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
