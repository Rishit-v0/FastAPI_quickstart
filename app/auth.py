from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database
from .database import get_db
import os

# Secret key for signing JWTs — in production load from environment variable
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"     # HMAC-SHA256 — industry standard JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# CryptContext handles password hashing and verification
# bcrypt is the recommended hashing algorithm — slow by design to prevent brute force
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer tells FastAPI where to find the JWT token
# tokenUrl = the login endpoint that issues tokens
# FastAPI uses this for automatic API docs (Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Copy data so we don't mutate the original
    to_encode = data.copy()

    # Set expiry time
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    # Add expiry to the JWT payload
    # 'exp' is a standard JWT claim — libraries know to check it automatically
    to_encode.update({"exp": expire})


    # Sign and encode the JWT
    # jwt.encode(payload, secret_key, algorithm) → JWT string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    # This is a FastAPI dependency — injected into protected routes
    # Depends(oauth2_scheme) extracts the Bearer token from the Authorization header
    # Depends(get_db) gives us a DB session to query the user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        # If token is expired, tampered, or invalid — raises JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # 'sub' is a standard JWT claim for subject (user identifier)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch the user from the database
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user