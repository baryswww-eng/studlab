import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import RoleName


def check_password(value: str) -> str:
    if not re.search(r"[^\W\d_]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one digit")
    return value


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr = Field(max_length=320)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 2:
            raise ValueError("Name is too short")
        return value

    @field_validator("password")
    @classmethod
    def _password_policy(cls, value: str) -> str:
        return check_password(value)


class LoginRequest(BaseModel):
    # Not format-validated: a malformed email simply gets "invalid credentials".
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: RoleName
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
