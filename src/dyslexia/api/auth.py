"""Password hashing (stdlib only) and bearer-token auth."""
import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .db import get_db
from .models_db import User


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return digest.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    check, _ = hash_password(password, salt)
    return hmac.compare_digest(check, password_hash)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def get_current_user(authorization: str = Header(default=""),
                     db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


def get_current_user_optional(authorization: str = Header(default=""),
                              db: Session = Depends(get_db)) -> User | None:
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    return db.query(User).filter(User.token == token).first()