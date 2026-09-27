"""Registration and login for student accounts."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import get_db
from ..models_db import User
from ..auth import hash_password, verify_password, new_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    name: str
    email: str


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "An account with this email already exists")
    pw_hash, salt = hash_password(req.password)
    user = User(name=req.name, email=req.email, password_hash=pw_hash,
                password_salt=salt, token=new_token())
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=user.token, name=user.name, email=user.email)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash, user.password_salt):
        raise HTTPException(401, "Incorrect email or password")
    user.token = new_token()
    db.commit()
    return AuthResponse(token=user.token, name=user.name, email=user.email)


@router.get("/me", response_model=AuthResponse)
def me(user: User = Depends(get_current_user)):
    return AuthResponse(token=user.token, name=user.name, email=user.email)