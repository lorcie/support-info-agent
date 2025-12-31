import os
import uvicorn
from fastapi import FastAPI, Request
from google.adk.cli.fast_api import get_fast_api_app
#from typing import Literal
#from pydantic import BaseModel

#from pathlib import Path

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
AGENT_DIR = BASE_DIR  # Parent directory containing backend_multi_tool_agent

# Set up DB path for sessions
SESSION_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

print(f"Base Directory: {BASE_DIR}")
print(f"Agent Directory: {AGENT_DIR}")
print(f"Session DB URL: {SESSION_DB_URL}")


# Get session service URI from environment variables
session_uri = os.getenv("SESSION_SERVICE_URI", None)

# Prepare arguments for get_fast_api_app
app_args = {"agents_dir": AGENT_DIR, "web": True}

# Only include session_service_uri if it's provided
if session_uri:
    app_args["session_service_uri"] = session_uri
else:
#    logger.log_text(
    print(
        "SESSION_SERVICE_URI not provided. Using in-memory session service instead. "
        "All sessions will be lost when the server restarts.",
        )

# Create FastAPI app with appropriate arguments
app: FastAPI = get_fast_api_app(**app_args)

app.title = "-backend-service"
app.description = "API for interacting with the Support Agent root-agent"
app.summary = "API for support root agent"
app.version="0.0.1",
app.terms_of_service="http://example.com/terms/",
app.contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://dummy.example.com/contact/",
        "email": "a.b@c.example.com",
    },
app.license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },

# Add custom endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/agent-info")
async def agent_info(request: Request):
#    """Provide agent information"""
    from backend_multi_tools_agent import root_agent

    return {
        "agent_name": root_agent.name,
        "description": root_agent.description,
        "model": root_agent.model,
    }


if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9999, 
        reload=False,
        log_level="debug"
    )
