from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel


class SOPStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class SOPPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PharmaceuticalDepartment(str, Enum):
    PRODUCTION = "production"
    QUALITY_CONTROL = "quality_control"
    QUALITY_ASSURANCE = "quality_assurance"
    REGULATORY_AFFAIRS = "regulatory_affairs"
    MANUFACTURING = "manufacturing"
    PACKAGING = "packaging"
    WAREHOUSE = "warehouse"
    MAINTENANCE = "maintenance"


class RegulatoryFramework(str, Enum):
    FDA_21_CFR_211 = "fda_21_cfr_211"
    ICH_Q7 = "ich_q7"
    ICH_Q10 = "ich_q10"
    WHO_GMP = "who_gmp"
    EMA_GMP = "ema_gmp"
    ISO_9001 = "iso_9001"
    ISO_14001 = "iso_14001"


class SOPBase(SQLModel):
    title: str = Field(index=True, min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    template_type: Optional[str] = Field(default=None, max_length=100)
    department: PharmaceuticalDepartment = Field(default=PharmaceuticalDepartment.PRODUCTION)
    priority: SOPPriority = Field(default=SOPPriority.MEDIUM)
    regulatory_framework: List[RegulatoryFramework] = Field(default_factory=list, sa_column=Column(JSON))
    guideline_refs: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    validation_errors: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    regulatory_version: str = Field(default="1.0", max_length=20)


class SOP(SOPBase, table=True):
    __tablename__ = "sops"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(unique=True, index=True, max_length=36)
    status: SOPStatus = Field(default=SOPStatus.PENDING, index=True)
    created_by: str = Field(index=True, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # SOP Content
    sop_content: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    pdf_path: Optional[str] = Field(default=None, max_length=500)
    
    # Pharmaceutical-specific fields
    batch_record_template: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    cleaning_validation_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    equipment_list: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON))
    chemical_inventory: Optional[List[Dict[str, Any]]] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Compliance tracking
    fda_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    gmp_compliance_indicators: Optional[Dict[str, bool]] = Field(default=None, sa_column=Column(JSON))
    review_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Error tracking
    error_message: Optional[str] = Field(default=None, max_length=1000)
    retry_count: int = Field(default=0)
    
    # Model performance tracking
    ai_model_used: Optional[str] = Field(default=None, max_length=100)
    generation_time_seconds: Optional[float] = Field(default=None)
    content_quality_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class SOPCreate(SOPBase):
    """Create SOP request model."""
    job_id: str
    created_by: str
    template_content: Optional[str] = None
    guideline_content: Optional[str] = None


class SOPUpdate(SQLModel):
    """Update SOP model."""
    title: Optional[str] = Field(default=None, min_length=5, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10, max_length=2000)
    status: Optional[SOPStatus] = None
    priority: Optional[SOPPriority] = None
    department: Optional[PharmaceuticalDepartment] = None
    regulatory_framework: Optional[List[RegulatoryFramework]] = None
    sop_content: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SOPResponse(SOPBase):
    """SOP response model."""
    id: int
    job_id: str
    status: SOPStatus
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sop_content: Optional[Dict[str, Any]] = None
    pdf_path: Optional[str] = None
    error_message: Optional[str] = None
    fda_compliance_score: Optional[float] = None
    gmp_compliance_indicators: Optional[Dict[str, bool]] = None
    ai_model_used: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    content_quality_score: Optional[float] = None


class SOPSearchFilters(BaseModel):
    """Search and filter model for SOPs."""
    title: Optional[str] = None
    status: Optional[List[SOPStatus]] = None
    department: Optional[List[PharmaceuticalDepartment]] = None
    priority: Optional[List[SOPPriority]] = None
    regulatory_framework: Optional[List[RegulatoryFramework]] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", regex=r"^(created_at|updated_at|title|status|priority|fda_compliance_score)$")
    sort_order: Optional[str] = Field(default="desc", regex=r"^(asc|desc)$")


class SOPValidationResult(BaseModel):
    """SOP validation result model."""
    is_valid: bool
    compliance_score: float = Field(ge=0.0, le=100.0)
    validation_errors: List[str] = Field(default_factory=list)
    missing_sections: List[str] = Field(default_factory=list)
    regulatory_issues: List[str] = Field(default_factory=list)
    gmp_compliance_indicators: Dict[str, bool] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class PharmaceuticalTerminology(BaseModel):
    """Pharmaceutical terminology validation."""
    term: str
    definition: str
    regulatory_source: str
    is_approved: bool
    alternatives: List[str] = Field(default_factory=list)