from datetime import datetime

import re

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    name: str | None = Field(None, max_length=255, description="Full name of the user")
    email: str | None = Field(None, max_length=255, description="Email address of the user")
    username: str = Field(..., min_length=1, max_length=255, description="Username or login identifier")
    password: str = Field(..., min_length=1, description="Plaintext password — stored as a hash")
    system: str = Field(..., min_length=1, max_length=100, description="System or service identifier (e.g. 'github', 'aws')")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is not None and not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v


class RegisterResponse(BaseModel):
    id: int
    system: str
    username: str
    name: str | None
    email: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
