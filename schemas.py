from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class User(BaseModel):
    name: str
    email: str
    age: int
    password: str
    bio: Optional[str] = None


    @field_validator("age")
    def check_age(cls, value):
        if value < 0:
            raise ValueError("Age must be positive")
        return value
    @field_validator("email")
    def check_email(cls, value):
        if '@' not in value:
            raise ValueError("Invalid email")
        return value


    @field_validator("password")
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @model_validator(mode="after")
    def check_age_password_rule(self):
        if self.age < 18 and len(self.password) < 12:
            raise ValueError("Users under 18 need a password of at least 12 characters")
        return self


class UserResponse(BaseModel):
    name: str
    email: str
    age: int
    role: str
    bio: Optional[str] = None
    avatar_filename: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str
    