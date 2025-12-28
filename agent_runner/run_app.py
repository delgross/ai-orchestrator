"""
Modularized Agent Runner Wrapper
This file now serves as a wrapper for the new modular agent_runner package.
"""
from agent_runner.main import app
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("AGENT_RUNNER_PORT", "5460"))
    uvicorn.run(app, host="0.0.0.0", port=port)