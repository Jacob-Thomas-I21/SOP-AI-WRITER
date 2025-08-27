from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return subject."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        token_type: str = payload.get("type")
        if token_type != "access":
            return None
        token_data = payload.get("sub")
        return token_data
    except JWTError:
        return None


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
        return token_data
    except JWTError:
        raise credentials_exception


# Pharmaceutical role-based access control
class PharmaceuticalRoles:
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    QA_REVIEWER = "qa_reviewer"
    QA_APPROVER = "qa_approver"
    ADMIN = "admin"


def require_role(required_role: str):
    """Decorator to require specific pharmaceutical role."""

    def role_checker(current_user: str = Depends(get_current_user)) -> str:
        # In production, this would check user's role from database
        # For now, we'll assume all users have supervisor role
        user_role = PharmaceuticalRoles.SUPERVISOR

        role_hierarchy = {
            PharmaceuticalRoles.OPERATOR: 1,
            PharmaceuticalRoles.SUPERVISOR: 2,
            PharmaceuticalRoles.QA_REVIEWER: 3,
            PharmaceuticalRoles.QA_APPROVER: 4,
            PharmaceuticalRoles.ADMIN: 5,
        }

        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )

        return current_user

    return role_checker
