"""
mock_openenv.py — Mock OpenEnv core classes for testing
"""

class Action:
    """Mock Action base class"""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Observation:
    """Mock Observation base class"""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Environment:
    """Mock Environment base class"""
    def reset(self, **kwargs) -> Observation:
        raise NotImplementedError

    def step(self, action: Action, **kwargs) -> Observation:
        raise NotImplementedError

    def state(self, **kwargs) -> dict:
        raise NotImplementedError

class GenericEnvClient:
    """Mock GenericEnvClient base class"""
    def __init__(self, env_id: str):
        self.env_id = env_id

    def reset(self, **kwargs) -> Observation:
        raise NotImplementedError

    def step(self, action: Action) -> Observation:
        raise NotImplementedError

    def close(self):
        pass