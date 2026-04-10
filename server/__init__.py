"""
FastAPI server for SocraticTeach-Env
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
import os

# Create app FIRST
app = FastAPI(title="SocraticTeach-Env", version="1.0.0")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try imports
DebugEnvironment = None
Action = None
Observation = None
ENV_OK = False

try:
    from .debug_env_environment import DebugEnvironment
    from models import Action, Observation
    ENV_OK = True
except Exception as e:
    print(f"[WARN] Import error: {e}")

env = None
current_obs = None

class StepRequest(BaseModel):
    action: Dict[str, Any]

@app.get("/")
async def root():
    return {"status": "running", "env_ok": ENV_OK}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/openenv/reset")
async def reset():
    global env, current_obs
    try:
        if not ENV_OK or DebugEnvironment is None:
            raise RuntimeError("Environment unavailable")
        env = DebugEnvironment()
        current_obs = env.reset()
        return {
            "success": True,
            "observation": {
                "topic": current_obs.topic,
                "difficulty": current_obs.difficulty,
                "confusion_score": float(current_obs.confusion_score),
                "turn_number": current_obs.turn_number,
                "done": current_obs.done,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/openenv/step")
async def step(request: StepRequest):
    global env, current_obs
    try:
        if not env or not ENV_OK:
            raise ValueError("Environment not initialized")
        msg = request.action.get("teacher_message", "")
        if not msg:
            raise ValueError("teacher_message required")
        action = Action(teacher_message=msg)
        current_obs = env.step(action)
        return {
            "success": True,
            "observation": {
                "topic": current_obs.topic,
                "confusion_score": float(current_obs.confusion_score),
                "reward": float(current_obs.reward),
                "done": current_obs.done,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/openenv/validate")
async def validate():
    try:
        if not ENV_OK:
            return {"valid": False, "msg": "Env unavailable"}
        test_env = DebugEnvironment()
        result = test_env.reset()
        return {"valid": True, "topic": result.topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["app", "DebugEnvironment"]
