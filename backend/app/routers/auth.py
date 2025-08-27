import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
import bcrypt
from jose import jwt

from app.core.config import settings
from app.core.database import get_session
from app.core.security import get_current_user, create_access_token, verify_token
from app.models.user import User, UserCreate, UserResponse, UserLogin
from app.models.audit import AuditLogCreate, AuditAction, AuditSeverity
from app.services.audit_service import AuditService
from app.utils.logging import log_regulatory_event, get_pharmaceutical_logger

router = APIRouter()
logger = get_pharmaceutical_logger(__name__)
audit_service = AuditService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register new user for the system."""

    try:
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == user_data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create new user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            department=user_data.department,
            role=user_data.role,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        # Hash password
        user.hashed_password = bcrypt.hashpw(
            user_data.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        session.add(user)
        session.commit()
        session.refresh(user)

        # Log the registration
        log_regulatory_event(
            logger,
            f"New user registered: {user.email}",
            event_type="user_registration",
            user_id=str(user.id),
            compliance_context="user_management",
        )

        return UserResponse.from_orm(user)

    except Exception as e:
        logger.error(f"User registration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Authenticate user."""

    try:
        # Find user
        user = session.exec(
            select(User).where(User.email == form_data.username)
        ).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Verify password
        if not bcrypt.checkpw(
            form_data.password.encode("utf-8"), user.hashed_password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)}
        )

        # Update last login
        user.last_login_at = datetime.utcnow()
        session.commit()

        # Log successful login
        log_regulatory_event(
            logger,
            f"User login successful: {user.email}",
            event_type="user_login",
            user_id=str(user.id),
            compliance_context="authentication",
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token)."""

    log_regulatory_event(
        logger,
        f"User logout: {current_user.email}",
        event_type="user_logout",
        user_id=str(current_user.id),
        compliance_context="authentication",
    )

    return {"message": "Successfully logged out"}


@router.get("/health")
async def auth_health_check():
    """Authentication service health check."""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat(),
        "compliance_features": {
            "user_authentication": "active",
            "role_based_access": "enabled",
            "audit_logging": "operational",
            "password_security": "bcrypt_encryption",
        },
    }
