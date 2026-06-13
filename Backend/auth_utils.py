import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status  # Depends injects values, HTTPException sends errors, and status has HTTP codes
from fastapi.security import OAuth2PasswordBearer  # Read the bearer token from login requests
from sqlalchemy.orm import Session
from database import get_db
import models

"""secret key and algortih for Json web tokens, these are used to create and verify the 
tokens that are sent to the frontend 
when a user logs in, and then sent back to the 
backend with each request to authenticate the user.
token expiration time is set to 60 minutes, after which the token will no longer be valid and the user will need to log in again to get a new token.
"""
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

""" helper to verify passwords against the hashed version in the database,
and to create and verify JWT tokens for user authentication.

"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


""" helper functions for authentication, 
including hashing passwords, verifying passwords, 
creating access tokens, and getting the current user from a token."""
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# it decodes the JWT token, extracts the user ID from the token payload, and retrieves the corresponding user from the database.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_error
    return user
