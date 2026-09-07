"""
Main application entrypoint and API controllers.
"""

from fastapi import FastAPI, Depends
import click
from .models import UserLoginRequest, AuthToken
from .services import AuthService

app = FastAPI(title="Sample Service API")

@app.post("/api/v1/auth/login")
def login_endpoint(payload: UserLoginRequest) -> AuthToken:
    """Authenticate user and return JWT access token."""
    service = AuthService(secret_key="secret")
    return service.authenticate_user(payload)

@app.get("/api/v1/health")
def health_check():
    """Service health inspection endpoint."""
    return {"status": "ok", "uptime": 99.9}

@click.command()
@click.option("--port", default=8000, help="Listening port")
def run_server(port: int):
    """Launch production server instance."""
    print(f"Starting server on port {port}")
