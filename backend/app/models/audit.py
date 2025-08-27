from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel


class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"
    DOWNLOAD = "download"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    GENERATE_PDF = "generate_pdf"
    VALIDATE = "validate"
    ARCHIVE = "archive"
    RESTORE = "restore"


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceEvent(str, Enum):
    FDA_REVIEW = "fda_review"
    GMP_VALIDATION = "gmp_validation"
    QUALITY_CHECK = "quality_check"
    REGULATORY_UPDATE = "regulatory_update"
    DEVIATION_LOGGED = "deviation_logged"
    CAPA_INITIATED = "capa_initiated"
    TRAINING_COMPLETED = "training_completed"


class AuditLogBase(SQLModel):
    user_id: str = Field(index=True, max_length=100)
    action: AuditAction = Field(index=True)
    resource_type: str = Field(index=True, max_length=50)  # sop, template, user, etc.
    resource_id: Optional[str] = Field(default=None, index=True, max_length=100)
    severity: AuditSeverity = Field(default=AuditSeverity.INFO, index=True)
    description: str = Field(max_length=1000)

    # Pharmaceutical-specific fields
    compliance_event: Optional[ComplianceEvent] = Field(default=None, index=True)
    regulatory_impact: Optional[str] = Field(default=None, max_length=500)
    gmp_relevance: bool = Field(default=False, index=True)

    # Technical details
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    session_id: Optional[str] = Field(default=None, max_length=100)


class AuditLog(AuditLogBase, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Detailed audit information
    old_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    new_values: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    additional_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )

    # Error tracking
    error_details: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    stack_trace: Optional[str] = Field(default=None)

    # Pharmaceutical compliance tracking
    batch_number: Optional[str] = Field(default=None, max_length=100, index=True)
    lot_number: Optional[str] = Field(default=None, max_length=100, index=True)
    product_code: Optional[str] = Field(default=None, max_length=50, index=True)
    equipment_id: Optional[str] = Field(default=None, max_length=100, index=True)

    # Review and approval tracking
    requires_review: bool = Field(default=False, index=True)
    reviewed_by: Optional[str] = Field(default=None, max_length=100)
    reviewed_at: Optional[datetime] = Field(default=None)
    review_status: Optional[str] = Field(default=None, max_length=50)
    review_comments: Optional[str] = Field(default=None, max_length=1000)

    # Data integrity
    checksum: Optional[str] = Field(default=None, max_length=64)
    digital_signature: Optional[str] = Field(default=None, max_length=500)

    # Retention and archival
    retention_period_days: int = Field(default=2555)  # 7 years default
    is_archived: bool = Field(default=False, index=True)
    archived_at: Optional[datetime] = Field(default=None)


class AuditLogCreate(AuditLogBase):
    """Create audit log request model."""

    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    product_code: Optional[str] = None
    equipment_id: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Audit log response model."""

    id: int
    timestamp: datetime
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    additional_data: Optional[Dict[str, Any]] = None
    requires_review: bool
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_status: Optional[str] = None


class AuditSearchFilters(BaseModel):
    """Search and filter model for audit logs."""

    user_id: Optional[str] = None
    action: Optional[List[AuditAction]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    severity: Optional[List[AuditSeverity]] = None
    compliance_event: Optional[List[ComplianceEvent]] = None
    gmp_relevance: Optional[bool] = None
    batch_number: Optional[str] = None
    lot_number: Optional[str] = None
    product_code: Optional[str] = None
    equipment_id: Optional[str] = None
    requires_review: Optional[bool] = None
    is_archived: Optional[bool] = False

    # Date range
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=1000)

    # Sorting
    sort_by: Optional[str] = Field(
        default="timestamp",
        regex=r"^(timestamp|user_id|action|severity|compliance_event)$",
    )
    sort_order: Optional[str] = Field(default="desc", regex=r"^(asc|desc)$")


class AuditSummary(BaseModel):
    """Audit summary statistics."""

    total_events: int
    events_by_action: Dict[str, int]
    events_by_severity: Dict[str, int]
    events_by_user: Dict[str, int]
    compliance_events_count: int
    gmp_related_events: int
    pending_reviews: int
    recent_critical_events: List[Dict[str, Any]]
    top_accessed_resources: List[Dict[str, Any]]

    # Time-based analytics
    events_last_24h: int
    events_last_7d: int
    events_last_30d: int

    # Compliance metrics
    fda_audit_readiness_score: float = Field(ge=0.0, le=100.0)
    data_integrity_score: float = Field(ge=0.0, le=100.0)

    # System health indicators
    error_rate: float = Field(ge=0.0, le=100.0)
    average_response_time_ms: Optional[float] = None


class ComplianceReport(BaseModel):
    """Pharmaceutical compliance report."""

    report_id: str
    generated_at: datetime
    report_period_start: datetime
    report_period_end: datetime

    # Regulatory compliance
    fda_21_cfr_part_11_compliance: Dict[str, Any]
    gmp_compliance_summary: Dict[str, Any]
    data_integrity_assessment: Dict[str, Any]

    # Audit trail completeness
    audit_trail_gaps: List[Dict[str, Any]]
    missing_signatures: List[Dict[str, Any]]
    incomplete_records: List[Dict[str, Any]]

    # Risk assessment
    high_risk_activities: List[Dict[str, Any]]
    regulatory_violations: List[Dict[str, Any]]
    recommended_actions: List[str]

    # Statistical analysis
    user_activity_patterns: Dict[str, Any]
    system_usage_trends: Dict[str, Any]
    error_analysis: Dict[str, Any]


class DataIntegrityCheck(BaseModel):
    """Data integrity validation result."""

    resource_id: str
    resource_type: str
    check_timestamp: datetime
    is_valid: bool

    # Integrity checks
    checksum_valid: bool
    digital_signature_valid: bool
    modification_history_complete: bool
    access_controls_verified: bool

    # Issues found
    integrity_violations: List[str]
    missing_audit_entries: List[str]
    suspicious_activities: List[str]

    # Recommendations
    corrective_actions: List[str]
    preventive_measures: List[str]
