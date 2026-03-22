"""
Authentication API module.

This module provides user registration, login, token refresh,
and password hashing utilities.
"""

from datetime import datetime, timedelta
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from src.core.config import settings
from src.core.database import get_session
from src.models import User, RefreshToken as RefreshTokenModel
from src.api.deps import get_current_user

# Create database session dependency
db_gen = get_session()


def get_db() -> Session:
    """Get database session."""
    return next(db_gen)


router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ========== Schemas ==========


class UserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (without sensitive data)."""

    id: str
    email: str
    full_name: Optional[str]
    company_name: Optional[str]
    subscription_tier: str
    invoice_limit: int
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


# ========== Utility Functions ==========


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(user_id: str) -> tuple[str, int]:
    """
    Create an access token.

    Returns:
        Tuple of (token_string, expires_in_seconds)
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    expires_in = settings.access_token_expire_minutes * 60

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt, expires_in


def create_refresh_token(user_id: str) -> tuple[str, datetime]:
    """
    Create a refresh token and store its hash in the database.

    Returns:
        Tuple of (token_string, expires_at)
    """
    expire_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode = {
        "sub": user_id,
        "exp": expire_at,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algorithm
    )

    # Store hash in database
    token_hash = get_password_hash(encoded_jwt)
    refresh_token_model = RefreshTokenModel(
        user_id=user_id, token_hash=token_hash, expires_at=expire_at
    )
    db = get_db()
    db.add(refresh_token_model)
    db.commit()
    db.refresh(refresh_token_model)

    return encoded_jwt, expire_at


def revoke_refresh_token(token_string: str) -> bool:
    """Revoke a refresh token."""
    try:
        payload = jwt.decode(
            token_string, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        if payload.get("type") != "refresh":
            return False

        token_hash = get_password_hash(token_string)
        db = get_db()
        token_record = (
            db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.is_revoked == False,
            )
            .first()
        )

        if token_record:
            token_record.is_revoked = True
            db.commit()
            return True
        return False
    except JWTError:
        return False


def validate_refresh_token(token_string: str) -> Optional[str]:
    """
    Validate a refresh token and return user_id if valid.

    Also revokes the used token (single-use).
    """
    try:
        payload = jwt.decode(
            token_string, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        exp = payload.get("exp")

        if user_id is None or exp is None:
            return None

        # Check if token exists and is not revoked
        token_hash = get_password_hash(token_string)
        db = get_db()
        token_record = (
            db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.is_revoked == False,
                RefreshTokenModel.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not token_record:
            return None

        # Revoke this token (single-use rotation)
        token_record.is_revoked = True
        db.commit()

        return user_id
    except JWTError:
        return None


# ========== API Endpoints ==========


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister):
    """
    Register a new user.

    - Validates email uniqueness
    - Hashes password with bcrypt
    - Creates user with free tier by default
    """
    db = get_db()
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password
    password_hash = get_password_hash(user_data.password)

    # Create user
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        subscription_tier="free",
        invoice_limit=5,
        is_active=True,
        is_admin=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request):
    """
    Authenticate user and return access + refresh tokens.

    - Validates email and password
    - Updates last_login_at
    - Returns JWT access token and refresh token
    """
    db = get_db()
    user = (
        db.query(User)
        .filter(User.email == credentials.email, User.is_active == True)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token, expires_in = create_access_token(user.id)
    refresh_token, _ = create_refresh_token(user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using a refresh token.

    - Validates refresh token
    - Revokes old refresh token (single-use)
    - Issues new access and refresh tokens
    """
    user_id = validate_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token, expires_in = create_access_token(user_id)
    new_refresh_token, _ = create_refresh_token(user_id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/logout")
async def logout(refresh_token: str):
    """
    Logout user by revoking refresh token.

    Client should discard access token on their side.
    """
    success = revoke_refresh_token(refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's information.

    Returns user details including subscription tier, limits, and admin status.
    """
    return current_user
