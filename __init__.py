"""
SocraticTeach-Env Package
An OpenEnv RL environment for teaching using the Socratic method.
"""

__version__ = "1.0.0"
__author__ = "Meta PyTorch Hackathon 2026"

from models import Action, Observation
from client import SocraticTeachClient

__all__ = [
    "Action",
    "Observation",
    "SocraticTeachClient",
]
