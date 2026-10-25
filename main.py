from fastapi import FastAPI
from routers import users

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(users.router)

import os # This brings in Python’s built-in Operating System (OS) module. This module contains tools that allow Python to talk directly to your computer's file system so it can create, delete, or move folders and files.
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="Uploads") # this line of code means you are making a folder on your computer accessible to the public via a web URL.

@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "This operation violates a database constraint (e.g. duplicate value)."}
    )

@app.get("/")
def read_root():
    return {"message": "Hello, Backend World!"}


@app.get("/search")
def search_items (keyword: str, limit: int = 10):
    return {"keyword": keyword, "limit": limit}

#path + query parameters together
@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int, limit: int = 5):
    return {
        "user_id": user_id,
        "limit": limit,
        "message": f"Showing {limit} posts for user {user_id}"
    }