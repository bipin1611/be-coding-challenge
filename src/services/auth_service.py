import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.user import User
from src.schemas.user import LoginRequest, RegisterRequest


def _hash_password(password: str) -> str:
    salt = os.urandom(32)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=260_000)
    return salt.hex() + ":" + digest.hex()


def _verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=260_000)
    return digest.hex() == digest_hex


def _create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "system": user.system,
        "username": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def register(db: AsyncSession, data: RegisterRequest) -> User:
    user = User(
        system=data.system,
        username=data.username,
        password=_hash_password(data.password),
        name=data.name,
        email=data.email,
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        detail = str(exc.orig).lower()
        if "username" in detail:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        if "email" in detail:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, data: LoginRequest) -> str:
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if user is None or not _verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return _create_token(user)
