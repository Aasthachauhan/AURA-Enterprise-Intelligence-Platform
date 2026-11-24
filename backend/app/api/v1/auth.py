"""Authentication API router."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    """Register a new user and generate access credentials."""
    client_ip = request.client.host if request.client else None
    return await AuthService.register(db, data, client_ip)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password."""
    client_ip = request.client.host if request.client else None
    return await AuthService.login(db, data, client_ip)


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using valid refresh token."""
    return await AuthService.refresh(db, data.refresh_token)


@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Fetch profile information for authenticated user."""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user session."""
    return {"message": "Successfully logged out"}
