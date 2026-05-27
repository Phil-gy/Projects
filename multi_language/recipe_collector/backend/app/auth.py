import os
import time
import jwt

from fastapi import Header, HTTPException


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
JWT_SECRET = os.getenv("JWT_SECRET", "local-development-secret")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRATION_SECONDS = 60 * 60 * 24 * 7


def create_admin_token() -> str:
    payload = {
        "role": "admin",
        "exp": int(time.time()) + TOKEN_EXPIRATION_SECONDS,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_admin_token(authorization: str | None = Header(default=None)) -> bool:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return True


def check_password(password: str) -> bool:
    return password == ADMIN_PASSWORD