from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import BaseModel


class TemplateCategory(str, Enum):
    CLEANING_VALIDATION = "cleaning_validation"
    EQUIPMENT_QUALIFICATION = "equipment_qualification"
    MANUFACTURING_PROCESS = "manufacturing_process"
    QUALITY_CONTROL = "quality_control"
    BATCH_RECORD = "batch_record"
    CHANGE_CONTROL = "change_control"
    DEVIATION_INVESTIGATION = "deviation_investigation"
    CORRECTIVE_ACTION = "corrective_action"
    TRAINING = "training"
    MAINTENANCE = "maintenance"
    ENVIRONMENTAL_MONITORING = "environmental_monitoring"
    VALIDATION_MASTER_PLAN = "validation_master_plan"


class TemplateComplexity(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ValidationRule(BaseModel):
    """Validation rules for template sections."""
    rule_id: str
    rule_type: str  # required, format, length, regex, etc.
    description: str
    parameters: Dict[str, Any]
    error_message: str
    regulatory_basis: Optional[str] = None


class TemplateSection(BaseModel):
    """Template section definition."""
    section_id: str
    title: str
    description: str
    content_template: str
    is_required: bool = True
    order_index: int
    validation_rules: List[ValidationRule] = Field(default_factory=list)
    regulatory_references: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    placeholder_text: Optional[str] = None


class TemplateBase(SQLModel):
    name: str = Field(index=True, min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=1000)
    category: TemplateCategory
    complexity: TemplateComplexity = Field(default=TemplateComplexity.BASIC)
    regulatory_framework: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = Field(default=True, index=True)
    version: str = Field(default="1.0", max_length=20)
    
    # Template configuration
    estimated_completion_time_minutes: Optional[int] = Field(default=None, ge=5, le=480)
    required_roles: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    prerequisite_templates: List[str] = Field(default_factory=list, sa_column=Column(JSON))


class Template(TemplateBase, table=True):
    __tablename__ = "templates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: str = Field(unique=True, index=True, max_length=36)
    created_by: str = Field(index=True, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default=None)
    last_used_at: Optional[datetime] = Field(default=None)
    
    # Template structure
    sections: List[TemplateSection] = Field(default_factory=list, sa_column=Column(JSON))
    global_validation_rules: List[ValidationRule] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Pharmaceutical-specific metadata
    gmp_compliance_requirements: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    equipment_categories: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    chemical_safety_requirements: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    environmental_considerations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Usage statistics
    usage_count: int = Field(default=0, index=True)
    success_rate: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    average_completion_time: Optional[float] = Field(default=None)
    
    # Template customization
    custom_css: Optional[str] = Field(default=None)
    custom_javascript: Optional[str] = Field(default=None)
    pdf_template_path: Optional[str] = Field(default=None, max_length=500)
    
    # Quality metrics
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    regulatory_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    user_satisfaction_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class TemplateCreate(TemplateBase):
    """Create template request model."""
    template_id: str
    created_by: str
    sections: List[TemplateSection]
    global_validation_rules: Optional[List[ValidationRule]] = Field(default_factory=list)


class TemplateUpdate(SQLModel):
    """Update template model."""
    name: Optional[str] = Field(default=None, min_length=5, max_length=200)
    description: Optional[str] = Field(default=None, min_length=10, max_length=1000)
    category: Optional[TemplateCategory] = None
    complexity: Optional[TemplateComplexity] = None
    regulatory_framework: Optional[List[str]] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None
    sections: Optional[List[TemplateSection]] = None
    global_validation_rules: Optional[List[ValidationRule]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TemplateResponse(TemplateBase):
    """Template response model."""
    id: int
    template_id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    sections: List[TemplateSection]
    global_validation_rules: List[ValidationRule]
    usage_count: int
    success_rate: Optional[float] = None
    quality_score: Optional[float] = None
    regulatory_compliance_score: Optional[float] = None


class TemplateSearchFilters(BaseModel):
    """Search and filter model for templates."""
    name: Optional[str] = None
    category: Optional[List[TemplateCategory]] = None
    complexity: Optional[List[TemplateComplexity]] = None
    regulatory_framework: Optional[List[str]] = None
    is_active: Optional[bool] = True
    created_by: Optional[str] = None
    min_quality_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    min_compliance_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field(default="usage_count", regex=r"^(created_at|updated_at|name|usage_count|quality_score|regulatory_compliance_score)$")
    sort_order: Optional[str] = Field(default="desc", regex=r"^(asc|desc)$")


class TemplateUsageStats(BaseModel):
    """Template usage statistics."""
    template_id: str
    template_name: str
    total_uses: int
    successful_uses: int
    failed_uses: int
    success_rate: float
    average_completion_time_minutes: Optional[float] = None
    most_common_errors: List[str] = Field(default_factory=list)
    user_feedback_summary: Dict[str, Any] = Field(default_factory=dict)
    last_30_days_usage: int = 0


class TemplateValidationRequest(BaseModel):
    """Template validation request."""
    template_data: Dict[str, Any]
    regulatory_framework: List[str]
    validate_sections: bool = True
    validate_compliance: bool = True
    check_completeness: bool = True


class TemplateValidationResponse(BaseModel):
    """Template validation response."""
    is_valid: bool
    validation_score: float = Field(ge=0.0, le=100.0)
    section_validations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    compliance_issues: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    estimated_fix_time_minutes: Optional[int] = None