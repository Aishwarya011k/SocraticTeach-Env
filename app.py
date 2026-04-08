#!/usr/bin/env python3
"""Root launcher for the SocraticTeach-Env API."""

from server.api import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
