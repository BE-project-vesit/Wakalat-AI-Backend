"""
Authentication module for Wakalat-AI MCP Server
Generates and verifies JWT access tokens for MCP access
"""
import jwt
import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

security = HTTPBearer()

ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30


def create_access_token(email: str) -> str:
    """Create a JWT access token for the given email."""
    payload = {
        "sub": email,
        "iat": datetime.datetime.now(datetime.timezone.utc),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=TOKEN_EXPIRE_DAYS),
        "type": "access",
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    logger.info(f"Created access token for: {email}")
    return token


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token. Returns the payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency that extracts and verifies the Bearer token."""
    payload = verify_token(credentials.credentials)
    return payload


def verify_token_from_header(authorization: Optional[str]) -> dict:
    """Verify token from a raw Authorization header string (for SSE/WebSocket)."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use: Bearer <token>",
        )
    return verify_token(parts[1])
