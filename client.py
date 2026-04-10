"""
SocraticTeach-Env: OpenEnv Client
Implements the GenericEnvClient for interacting with the DebugEnvironment.
"""

from typing import Optional, Dict, Any
from openenv.core import GenericEnvClient
from models import Observation, Action


class SocraticTeachClient(GenericEnvClient):
    """
    Client for the SocraticTeach-Env environment.
    Communicates with the DebugEnvironment server.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the SocraticTeach client.
        
        Args:
            base_url: URL of the OpenEnv server hosting DebugEnvironment
        """
        super().__init__(base_url=base_url)
        self.base_url = base_url

    def reset(self, **kwargs) -> Observation:
        """
        Reset the environment and start a new episode.
        
        Returns:
            Observation: Initial observation with topic assigned
        """
        response = self._make_request("POST", "/reset", data=kwargs)
        return self._parse_observation(response)

    def step(self, action: Action, **kwargs) -> Observation:
        """
        Execute one step of the environment.
        
        Args:
            action: Teacher message (Action object)
            **kwargs: Additional kwargs
            
        Returns:
            Observation: Updated observation after student response
        """
        data = {
            "action": action.to_dict(),
            **kwargs
        }
        response = self._make_request("POST", "/step", data=data)
        return self._parse_observation(response)

    def state(self, **kwargs) -> Dict[str, Any]:
        """
        Get the current state of the environment.
        
        Returns:
            Dict containing all state information
        """
        return self._make_request("POST", "/state", data=kwargs)

    def _parse_observation(self, response: Dict[str, Any]) -> Observation:
        """
        Convert API response to Observation object.
        """
        if isinstance(response, dict):
            return Observation(**response)
        return response

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to the OpenEnv server.
        Subclasses of GenericEnvClient handle this automatically.
        """
        # This is handled by the parent class GenericEnvClient
        # which communicates with the OpenEnv server API
        import requests
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
