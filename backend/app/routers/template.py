import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user, require_role, PharmaceuticalRoles
from app.models.template import Template, TemplateCreate, TemplateUpdate, TemplateResponse
from app.models.user import User
from app.models.audit import AuditLogCreate, AuditAction
from app.services.audit_service import AuditService
from app.utils.logging import log_regulatory_event, get_pharmaceutical_logger

router = APIRouter()
logger = get_pharmaceutical_logger(__name__)
audit_service = AuditService()


@router.post("/", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create new pharmaceutical SOP template."""
    
    try:
        template = Template(
            name=template_data.name,
            description=template_data.description,
            category=template_data.category,
            regulatory_framework=template_data.regulatory_framework,
            template_content=template_data.template_content,
            sections=template_data.sections,
            is_active=True,
            created_by=str(current_user.id),
            created_at=datetime.utcnow()
        )
        
        session.add(template)
        session.commit()
        session.refresh(template)
        
        # Log regulatory event
        log_regulatory_event(
            logger,
            f"New SOP template created: {template.name}",
            event_type="template_creation",
            user_id=str(current_user.id),
            compliance_context="template_management"
        )
        
        return TemplateResponse.from_orm(template)
        
    except Exception as e:
        logger.error(f"Template creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template creation failed"
        )


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    regulatory_framework: Optional[str] = None,
    is_active: Optional[bool] = True,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List pharmaceutical SOP templates."""
    
    try:
        query = select(Template)
        
        if category:
            query = query.where(Template.category == category)
        if regulatory_framework:
            query = query.where(Template.regulatory_framework.contains([regulatory_framework]))
        if is_active is not None:
            query = query.where(Template.is_active == is_active)
        
        templates = session.exec(query.order_by(Template.created_at.desc())).all()
        
        return [TemplateResponse.from_orm(template) for template in templates]
        
    except Exception as e:
        logger.error(f"Template listing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template listing failed"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get specific pharmaceutical SOP template."""
    
    template = session.get(Template, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse.from_orm(template)


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.SUPERVISOR))
):
    """Update pharmaceutical SOP template."""
    
    template = session.get(Template, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    try:
        # Store old values for audit
        old_values = {
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "is_active": template.is_active
        }
        
        # Apply updates
        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(template)
        
        # Create audit log
        await audit_service.log_event(
            AuditLogCreate(
                user_id=str(current_user.id),
                action=AuditAction.UPDATE,
                resource_type="template",
                resource_id=str(template_id),
                description=f"Updated template: {template.name}",
                regulatory_impact="Template modification for SOP generation",
                gmp_relevance=True,
                old_values=old_values,
                new_values=update_data
            ),
            session
        )
        
        log_regulatory_event(
            logger,
            f"Template updated: {template.name}",
            event_type="template_update",
            user_id=str(current_user.id),
            compliance_context="template_management"
        )
        
        return TemplateResponse.from_orm(template)
        
    except Exception as e:
        logger.error(f"Template update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template update failed"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.QA_APPROVER))
):
    """Delete pharmaceutical SOP template."""
    
    template = session.get(Template, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    try:
        # Create deletion audit log
        await audit_service.log_event(
            AuditLogCreate(
                user_id=str(current_user.id),
                action=AuditAction.DELETE,
                resource_type="template",
                resource_id=str(template_id),
                description=f"Deleted template: {template.name}",
                regulatory_impact="Critical - Template deletion requires review",
                gmp_relevance=True,
                old_values={
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "created_by": template.created_by
                }
            ),
            session
        )
        
        session.delete(template)
        session.commit()
        
        log_regulatory_event(
            logger,
            f"Template deleted: {template.name}",
            event_type="template_deletion",
            user_id=str(current_user.id),
            compliance_context="critical_template_management"
        )
        
        return {"message": "Template deleted successfully"}
        
    except Exception as e:
        logger.error(f"Template deletion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template deletion failed"
        )


@router.get("/categories/list")
async def list_template_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get list of available template categories."""
    
    categories = [
        "Manufacturing SOP",
        "Quality Control SOP", 
        "Quality Assurance SOP",
        "Cleaning Validation SOP",
        "Equipment Qualification SOP",
        "Analytical Method SOP",
        "Packaging SOP",
        "Maintenance SOP",
        "Training SOP",
        "Deviation Investigation SOP"
    ]
    
    return {
        "categories": categories,
        "total_count": len(categories),
        "pharmaceutical_compliance": "category_standardization"
    }


@router.get("/health")
async def template_health_check():
    """Template service health check."""
    return {
        "status": "healthy",
        "service": "templates",
        "timestamp": datetime.utcnow().isoformat(),
        "compliance_features": {
            "template_management": "operational",
            "regulatory_compliance": "maintained",
            "audit_logging": "active",
            "version_control": "enabled"
        }
    }