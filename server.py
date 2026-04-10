"""
FastAPI server exposing the SocraticTeach-Env through OpenEnv HTTP API.
This enables compatibility with OpenEnv submission platforms.
"""

import uvicorn
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from server.debug_env_environment import DebugEnvironment
from models import Action, Observation

app = FastAPI(
    title="SocraticTeach-Env OpenEnv Server",
    description="OpenEnv-compliant HTTP API for the Socratic Teaching environment",
    version="1.0.0"
)

# Global environment instance
env = DebugEnvironment()
current_obs: Optional[Observation] = None


class ResetRequest(BaseModel):
    """Request model for reset endpoint."""
    pass


class StepRequest(BaseModel):
    """Request model for step endpoint."""
    action: Dict[str, Any]


class ObservationResponse(BaseModel):
    """Response model for observation data."""
    class Config:
        arbitrary_types_allowed = True


@app.on_event("startup")
async def startup_event():
    """Initialize environment on server startup."""
    global env, current_obs
    env = DebugEnvironment()
    current_obs = env.reset()
    print("✅ OpenEnv Server started. Environment initialized.")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "SocraticTeach-Env",
        "version": "1.0.0"
    }


@app.post("/openenv/reset")
async def reset_environment():
    """Reset the environment and start a new episode."""
    global env, current_obs
    try:
        env = DebugEnvironment()
        current_obs = env.reset()
        
        # Convert Observation to dict for JSON serialization
        observation_dict = {
            "topic": current_obs.topic,
            "difficulty": current_obs.difficulty,
            "student_response": current_obs.student_response,
            "confusion_score": current_obs.confusion_score,
            "turn_number": current_obs.turn_number,
            "pre_quiz_score": current_obs.pre_quiz_score,
            "post_quiz_score": current_obs.post_quiz_score,
            "misconception": current_obs.misconception,
            "misconception_resolved": current_obs.misconception_resolved,
            "reward": current_obs.reward,
            "cumulative_reward": current_obs.cumulative_reward,
            "done": current_obs.done,
            "feedback": current_obs.feedback,
        }
        
        return {
            "success": True,
            "observation": observation_dict,
            "message": f"Episode started: {current_obs.topic}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/openenv/step")
async def step_environment(request: StepRequest):
    """Execute one step in the environment."""
    global env, current_obs
    
    try:
        if env.topic is None:
            raise ValueError("Environment not initialized. Call /openenv/reset first.")
        
        # Extract teacher_message from action dict
        teacher_message = request.action.get("teacher_message", "")
        if not teacher_message.strip():
            raise ValueError("teacher_message is required in action")
        
        # Create Action and execute step
        action = Action(teacher_message=teacher_message)
        current_obs = env.step(action)
        
        # Convert Observation to dict for JSON serialization
        observation_dict = {
            "topic": current_obs.topic,
            "difficulty": current_obs.difficulty,
            "student_response": current_obs.student_response,
            "confusion_score": current_obs.confusion_score,
            "turn_number": current_obs.turn_number,
            "pre_quiz_score": current_obs.pre_quiz_score,
            "post_quiz_score": current_obs.post_quiz_score,
            "misconception": current_obs.misconception,
            "misconception_resolved": current_obs.misconception_resolved,
            "reward": current_obs.reward,
            "cumulative_reward": current_obs.cumulative_reward,
            "done": current_obs.done,
            "feedback": current_obs.feedback,
        }
        
        return {
            "success": True,
            "observation": observation_dict,
            "reward": current_obs.reward,
            "done": current_obs.done,
            "info": {"episode_turn": current_obs.turn_number}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openenv/validate")
async def validate_environment():
    """Validate that the OpenEnv environment is properly configured."""
    try:
        # Test reset
        test_env = DebugEnvironment()
        test_obs = test_env.reset()
        
        # Test step
        test_action = Action(teacher_message="Why do you think that?")
        test_obs = test_env.step(test_action)
        
        # Test state
        state = test_env.state()
        
        return {
            "valid": True,
            "message": "Environment validation successful",
            "environment_class": "DebugEnvironment",
            "observations_fields": list(test_obs.__dict__.keys()),
            "features": {
                "reset": True,
                "step": True,
                "state": True,
                "topics": 9,
                "difficulties": ["easy", "medium", "hard"],
                "max_turns": 10
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Environment validation failed: {str(e)}"
        )


@app.post("/openenv/inference")
async def run_inference(request: StepRequest):
    """Run a full inference episode with structured logging."""
    try:
        episode_logs = []
        
        # Reset environment
        test_env = DebugEnvironment()
        obs = test_env.reset()
        
        episode_logs.append({
            "step": "START",
            "topic": obs.topic,
            "difficulty": obs.difficulty,
            "confusion": obs.confusion_score
        })
        
        # Run up to 10 steps with sample messages
        sample_messages = [
            "Why do you think that?",
            "What would happen if you changed that?",
            "Can you explain your reasoning?",
            "Consider what happens when...",
            "What does that mean exactly?",
            "How would you approach this differently?",
            "What's the relationship between X and Y?",
            "Can you give me an example?",
            "Why is that important?",
            "What would you try next?"
        ]
        
        for i, msg in enumerate(sample_messages):
            if obs.done:
                break
            
            action = Action(teacher_message=msg)
            obs = test_env.step(action)
            
            episode_logs.append({
                "step": i + 1,
                "message": msg,
                "response": obs.student_response,
                "confusion": obs.confusion_score,
                "reward": obs.reward,
                "misconception_resolved": obs.misconception_resolved
            })
        
        episode_logs.append({
            "step": "END",
            "done": obs.done,
            "final_reward": obs.cumulative_reward,
            "misconception_resolved": obs.misconception_resolved,
            "pre_quiz": obs.pre_quiz_score,
            "post_quiz": obs.post_quiz_score
        })
        
        return {
            "success": True,
            "episode_log": episode_logs,
            "final_reward": obs.cumulative_reward
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openenv/status")
async def get_status():
    """Get current environment status."""
    global current_obs
    
    try:
        if current_obs is None:
            return {"status": "uninitialized", "message": "Call /openenv/reset first"}
        
        return {
            "status": "active",
            "episode": {
                "topic": current_obs.topic,
                "difficulty": current_obs.difficulty,
                "turn": current_obs.turn_number,
                "done": current_obs.done,
                "confusion": current_obs.confusion_score,
                "reward": current_obs.cumulative_reward
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "service": "SocraticTeach-Env OpenEnv Server",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "reset": "POST /openenv/reset",
            "step": "POST /openenv/step",
            "validate": "GET /openenv/validate",
            "inference": "POST /openenv/inference",
            "status": "GET /openenv/status",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
