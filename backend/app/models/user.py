from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    QA_REVIEWER = "qa_reviewer"
    QA_APPROVER = "qa_approver"
    REGULATORY_SPECIALIST = "regulatory_specialist"
    ADMIN = "admin"
    SYSTEM_ADMIN = "system_admin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"
    LOCKED = "locked"


class PharmaceuticalCertification(str, Enum):
    GMP_CERTIFIED = "gmp_certified"
    FDA_TRAINED = "fda_trained"
    VALIDATION_SPECIALIST = "validation_specialist"
    QUALITY_AUDITOR = "quality_auditor"
    REGULATORY_AFFAIRS = "regulatory_affairs"
    ASEPTIC_PROCESSING = "aseptic_processing"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    role: UserRole = Field(default=UserRole.OPERATOR, index=True)
    department: Optional[str] = Field(default=None, max_length=100)
    employee_id: Optional[str] = Field(default=None, unique=True, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True, index=True)
    
    # Pharmaceutical-specific fields
    certifications: List[PharmaceuticalCertification] = Field(default_factory=list)
    training_completed: bool = Field(default=False, index=True)
    gmp_training_date: Optional[datetime] = Field(default=None)
    last_regulatory_update: Optional[datetime] = Field(default=None)
    signature_authority_level: int = Field(default=1, ge=1, le=5)


class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True, max_length=36)
    password_hash: str = Field(max_length=255)
    status: UserStatus = Field(default=UserStatus.ACTIVE, index=True)
    
    # Override fields for SQLAlchemy compatibility
    email: str = Field(unique=True, index=True, max_length=255)
    certifications: List[PharmaceuticalCertification] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)
    password_changed_at: Optional[datetime] = Field(default=None)
    
    # Security fields
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    must_change_password: bool = Field(default=False)
    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: Optional[str] = Field(default=None, max_length=32)
    
    # Pharmaceutical compliance
    digital_signature: Optional[str] = Field(default=None, max_length=1000)
    signature_verified: bool = Field(default=False)
    compliance_acknowledgment_date: Optional[datetime] = Field(default=None)
    data_integrity_training_completed: bool = Field(default=False)
    
    # Activity tracking
    login_count: int = Field(default=0)
    sop_created_count: int = Field(default=0)
    sop_approved_count: int = Field(default=0)
    last_activity: Optional[datetime] = Field(default=None)
    
    # Session management
    current_session_id: Optional[str] = Field(default=None, max_length=100)
    session_expires_at: Optional[datetime] = Field(default=None)


class UserCreate(UserBase):
    """Create user request model."""
    user_id: str
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    
    def validate_passwords_match(self) -> bool:
        return self.password == self.confirm_password


class UserUpdate(SQLModel):
    """Update user model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    department: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None
    certifications: Optional[List[PharmaceuticalCertification]] = None
    training_completed: Optional[bool] = None
    signature_authority_level: Optional[int] = Field(default=None, ge=1, le=5)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserResponse(UserBase):
    """User response model."""
    id: int
    user_id: str
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_count: int
    sop_created_count: int
    sop_approved_count: int
    signature_verified: bool
    two_factor_enabled: bool


class UserLogin(BaseModel):
    """User login model."""
    username_or_email: str
    password: str
    remember_me: bool = False
    two_factor_code: Optional[str] = None


class UserLoginResponse(BaseModel):
    """User login response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    requires_password_change: bool = False
    requires_two_factor: bool = False


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    confirm_new_password: str = Field(min_length=8, max_length=100)
    
    def validate_passwords_match(self) -> bool:
        return self.new_password == self.confirm_new_password


class UserSearchFilters(BaseModel):
    """Search and filter model for users."""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[List[UserRole]] = None
    department: Optional[str] = None
    status: Optional[List[UserStatus]] = None
    is_active: Optional[bool] = True
    training_completed: Optional[bool] = None
    signature_verified: Optional[bool] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", regex=r"^(created_at|updated_at|full_name|username|last_login|sop_created_count)$")
    sort_order: Optional[str] = Field(default="desc", regex=r"^(asc|desc)$")


class UserActivitySummary(BaseModel):
    """User activity summary."""
    user_id: str
    username: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    
    # Activity metrics
    total_logins: int
    last_login: Optional[datetime] = None
    sops_created: int
    sops_approved: int
    templates_used: int
    
    # Time-based activity
    logins_last_30_days: int
    sops_created_last_30_days: int
    average_session_duration_minutes: Optional[float] = None
    
    # Compliance metrics
    training_up_to_date: bool
    certification_status: List[PharmaceuticalCertification]
    last_regulatory_training: Optional[datetime] = None
    compliance_score: float = Field(ge=0.0, le=100.0)


class TwoFactorSetup(BaseModel):
    """Two-factor authentication setup."""
    qr_code_url: str
    secret_key: str
    backup_codes: List[str]


class TwoFactorVerification(BaseModel):
    """Two-factor authentication verification."""
    verification_code: str
    backup_code: Optional[str] = None