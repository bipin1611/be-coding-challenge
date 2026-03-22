from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.logger import get_logger
from src.schemas.user import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from src.services.auth_service import authenticate, register

logger = get_logger(__name__)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_endpoint(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Register | system=%s username=%s", payload.system, payload.username)
    return await register(db, payload)


@router.post("/login", response_model=TokenResponse)
async def login_endpoint(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Login attempt | username=%s", payload.username)
    token = await authenticate(db, payload)
    return TokenResponse(access_token=token)
