from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import DBUser, RefreshToken
from schemas import User, UserResponse, LoginRequest, RefreshRequest

from auth import ( 
    hash_password, verify_password, create_access_token,
    verify_token, verify_admin, generate_refresh_token, fingerprint_token,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError

import os
import secrets
from fastapi import UploadFile, File

router = APIRouter()

@router.get("/users/me", response_model=UserResponse)
def get_current_user(email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == email).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User Not found")
    return user

#endpoint for uploading a user avatar
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png"}
MAX_FILE_SIZE = 2 * 1024 * 1024 # 2 MB

@router .post("/users/me/avatar", response_model=UserResponse)
def upload_avatar(file: UploadFile = File(...), email: str = Depends(verify_token),db: Session = Depends(get_db),): #In FastAPI, putting ... inside a function parameter means "This field is strictly required."
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed")

    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    filename = secrets.token_hex(16) + ALLOWED_TYPES[file.content_type]
    with open(os.path.join("uploads", filename), "wb") as f:
        f.write(contents)

    user.avatar_filename = filename
    db.flush()
    db.refresh(user)
    return user


@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == credentials.email).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token (data={"sub":user.email})

    raw_refresh_token = generate_refresh_token()
    fingerprint = fingerprint_token(raw_refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    new_refresh_token = RefreshToken(user_id=user.id, token_fingerprint=fingerprint, expires_at=expires_at)
    db.add(new_refresh_token)

    return {"access_token": access_token, "refresh_token": raw_refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_access_token(request: RefreshRequest, db: Session = Depends(get_db)):
    fingerprint = fingerprint_token(request.refresh_token)

    stored = db.query(RefreshToken).filter(RefreshToken.token_fingerprint == fingerprint).first()

    if stored is None or stored.revoked or stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(DBUser).filter(DBUser.id == stored.user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    access_token = create_access_token(data={"sub":user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(request: RefreshRequest, db: Session = Depends(get_db)):
    fingerprint = fingerprint_token(request.refresh_token)

    stored = db.query(RefreshToken).filter(RefreshToken.token_fingerprint == fingerprint).first()

    if stored is not None:
        stored.revoked = True

    return {"message": "Logged out successfully"}


@router.get("/users/", response_model=list[UserResponse])
def get_all_users(skip: int = 0, limit : int = 10, db: Session = Depends(get_db)):
    users = db.query(DBUser).order_by(DBUser.id).offset(skip).limit(limit).all()
    return users

@router.get("/users/count")
def count_user(db: Session = Depends(get_db)):
    return {"total_user": db.query(DBUser).count()}

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: User, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    new_user = DBUser(name=user.name, email=user.email, age=user.age, hashed_password=hashed_pw, bio = user.bio)
    db.add(new_user)
    db.flush()        
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: User, db: Session = Depends(get_db), current_user_email: str = Depends(verify_token)):
    existing_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if existing_user.email != current_user_email:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    existing_user.name = user.name
    existing_user.email = user.email
    existing_user.age = user.age
    existing_user.bio = user.bio

    db.flush()
    db.refresh(existing_user)
    return existing_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(verify_token)):
    existing_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if existing_user.email != current_user_email:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.delete(existing_user)
    db.flush()
    return {"message": f"User {user_id} deleted successfully"}

@router.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: int, db: Session = Depends(get_db), admin: DBUser = Depends(verify_admin)):
    existing_user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.delete(existing_user)
    db.flush()

    return {"message": f"User {user_id} deleted by admin"}