from passlib.context import CryptContext                                        #password hash and verify

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError                          #encode & decode done by jwt                         

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import get_db
from models import DBUser
from sqlalchemy.orm import Session

from dotenv import load_dotenv
import os

import secrets

import hashlib

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")               #pwd_context is a custom object


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


security_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])    #payload is a dictionary
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


REFRESH_TOKEN_EXPIRE_DAYS = 7

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def fingerprint_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def verify_admin(email: str = Depends(verify_token), db: Session=Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == email).first()

    if user is None or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user