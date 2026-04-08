#!/usr/bin/env python3
"""
app.py — Root-level FastAPI entry point for hackathon validator
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add current directory to path
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from server.debug_env_environment import DebugEnvironment
from debug_env.models import TeacherAction

# Data models
class ResetRequest(BaseModel):
    difficulty: str = "easy"
    topic_index: int = None
    seed: int = None

class StepRequest(BaseModel):
    teacher_message: str

# Global environment
env_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global env_instance
    env_instance = DebugEnvironment()
    print("✓ Environment initialized")
    yield
    print("✓ Shutdown")

app = FastAPI(
    title="SocraticTeach-Env",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/reset")
async def reset(request: ResetRequest):
    global env_instance
    try:
        kwargs = {"difficulty": request.difficulty}
        if request.seed is not None:
            kwargs["seed"] = request.seed
        if request.topic_index is not None:
            kwargs["topic_index"] = request.topic_index
        obs = env_instance.reset(**kwargs)
        return {k: getattr(obs, k) for k in ["topic", "difficulty", "student_response", "confusion_score", "turn_number", "pre_quiz_score", "post_quiz_score", "misconception", "misconception_resolved", "feedback", "reward", "done"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(request: StepRequest):
    global env_instance
    try:
        action = TeacherAction(teacher_message=request.teacher_message)
        obs = env_instance.step(action)
        return {k: getattr(obs, k) for k in ["topic", "difficulty", "student_response", "confusion_score", "turn_number", "pre_quiz_score", "post_quiz_score", "misconception", "misconception_resolved", "feedback", "reward", "done"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    global env_instance
    try:
        return env_instance.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
