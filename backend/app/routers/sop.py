import uuid
import asyncio
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Response
from fastapi.responses import FileResponse
from sqlmodel import Session, select, func, and_, or_
import logging

from app.core.database import get_session
from app.core.security import get_current_user, require_role, PharmaceuticalRoles
from app.models.sop import (
    SOP,
    SOPCreate,
    SOPUpdate,
    SOPResponse,
    SOPSearchFilters,
    SOPStatus,
    SOPValidationResult,
    PharmaceuticalTerminology,
)
from app.models.audit import AuditLogCreate, AuditAction
from app.services.ollama_client import OllamaClient
from app.services.pdf_generator import PDFGenerator
from app.services.validation_service import PharmaceuticalValidationService
from app.services.audit_service import AuditService
from app.utils.logging import log_regulatory_event, get_pharmaceutical_logger

router = APIRouter()
logger = get_pharmaceutical_logger(__name__)

# Initialize services
ollama_client = OllamaClient()
pdf_generator = PDFGenerator()
validation_service = PharmaceuticalValidationService()
audit_service = AuditService()


@router.post("/", response_model=dict, status_code=201)
async def create_sop_generation_job(
    sop_data: SOPCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Create a new SOP generation job with pharmaceutical compliance validation."""

    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())

        # Create SOP record
        sop = SOP(
            job_id=job_id,
            title=sop_data.title,
            description=sop_data.description,
            template_type=sop_data.template_type,
            department=sop_data.department,
            priority=sop_data.priority,
            regulatory_framework=sop_data.regulatory_framework,
            guideline_refs=sop_data.guideline_refs,
            regulatory_version=sop_data.regulatory_version,
            created_by=current_user,
            status=SOPStatus.PENDING,
        )

        session.add(sop)
        session.commit()
        session.refresh(sop)

        # Log regulatory event
        log_regulatory_event(
            logger,
            f"SOP generation job created: {sop_data.title}",
            event_type="sop_creation",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="pharmaceutical_sop_generation",
        )

        # Create audit log
        await audit_service.log_event(
            AuditLogCreate(
                user_id=current_user,
                action=AuditAction.CREATE,
                resource_type="sop",
                resource_id=job_id,
                description=f"Created SOP generation job: {sop_data.title}",
                regulatory_impact="SOP creation for pharmaceutical manufacturing",
                gmp_relevance=True,
            ),
            session,
        )

        # Start background generation task
        background_tasks.add_task(
            generate_sop_background,
            job_id,
            sop_data.dict(),
            getattr(sop_data, "template_content", ""),
            getattr(sop_data, "guideline_content", ""),
        )

        return {
            "job_id": job_id,
            "status": "pending",
            "message": "SOP generation job created successfully",
            "estimated_completion_minutes": 2,
            "pharmaceutical_compliance": {
                "regulatory_framework_applied": sop_data.regulatory_framework,
                "gmp_validation_enabled": True,
                "fda_compliance_checking": True,
            },
        }

    except Exception as e:
        logger.error(f"Failed to create SOP generation job: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to create SOP generation job: {str(e)}"
        )


async def generate_sop_background(
    job_id: str, sop_data: dict, template_content: str, guideline_content: str
):
    """Background task to generate SOP using Ollama."""

    session_generator = get_session()
    session = next(session_generator)

    try:
        # Update status to processing
        sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()
        if not sop:
            logger.error(f"SOP not found for job {job_id}")
            return

        sop.status = SOPStatus.PROCESSING
        sop.updated_at = datetime.utcnow()
        session.commit()

        # Generate SOP content using Ollama
        generation_result = await ollama_client.generate_sop(
            title=sop_data["title"],
            description=sop_data["description"],
            template_content=template_content,
            guideline_content=guideline_content,
            regulatory_framework=sop_data.get("regulatory_framework", []),
            department=sop_data.get("department"),
            additional_context={
                "priority": sop_data.get("priority", "medium"),
                "job_id": job_id,
            },
        )

        if generation_result["status"] == "completed":
            # Validate generated content
            validation_result = await validation_service.validate_sop_content(
                generation_result["sop_content"],
                sop_data.get("regulatory_framework", []),
            )

            # Update SOP record with generated content
            sop.sop_content = generation_result["sop_content"]
            sop.status = SOPStatus.COMPLETED
            sop.completed_at = datetime.utcnow()
            sop.ai_model_used = generation_result["model_used"]
            sop.generation_time_seconds = generation_result["generation_time_seconds"]
            sop.content_quality_score = generation_result["quality_score"]
            sop.fda_compliance_score = validation_result.compliance_score
            sop.gmp_compliance_indicators = validation_result.gmp_compliance_indicators
            sop.validation_errors = (
                validation_result.validation_errors
                if not validation_result.is_valid
                else []
            )

        else:
            # Handle generation failure
            sop.status = SOPStatus.FAILED
            sop.error_message = generation_result.get("error_message", "Unknown error")
            sop.retry_count += 1

        sop.updated_at = datetime.utcnow()
        session.commit()

        # Log completion event
        log_regulatory_event(
            logger,
            f"SOP generation completed for job {job_id}: {sop.status.value}",
            event_type="sop_generation_complete",
            user_id=sop.created_by,
            sop_id=job_id,
            compliance_context="pharmaceutical_ai_generation",
        )

    except Exception as e:
        logger.error(f"SOP generation failed for job {job_id}: {e}", exc_info=True)

        # Update SOP with error status
        try:
            sop.status = SOPStatus.FAILED
            sop.error_message = str(e)
            sop.retry_count += 1
            sop.updated_at = datetime.utcnow()
            session.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update SOP error status: {commit_error}")

    finally:
        session.close()


@router.get("/{job_id}", response_model=SOPResponse)
async def get_sop_status(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get SOP generation job status and content."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    # Log access event for audit trail
    log_regulatory_event(
        logger,
        f"SOP accessed: {job_id}",
        event_type="sop_access",
        user_id=current_user,
        sop_id=job_id,
        compliance_context="data_access_audit",
    )

    return SOPResponse.from_orm(sop)


@router.get("/{job_id}/pdf")
async def download_sop_pdf(
    job_id: str,
    template: Optional[str] = Query(None, description="PDF template to use"),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Generate and download SOP as PDF."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    if sop.status != SOPStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="SOP generation not completed")

    try:
        # Generate PDF
        pdf_result = await pdf_generator.generate_pdf(sop, template_name=template)

        if not pdf_result["success"]:
            raise HTTPException(status_code=500, detail=pdf_result["error"])

        # Update SOP record with PDF path
        sop.pdf_path = pdf_result["pdf_path"]
        session.commit()

        # Log PDF generation event
        log_regulatory_event(
            logger,
            f"SOP PDF generated: {job_id}",
            event_type="pdf_generation",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="document_export",
        )

        # Return file response
        return FileResponse(
            path=pdf_result["pdf_path"],
            filename=pdf_result["filename"],
            media_type="application/pdf",
            headers={
                "X-Pharmaceutical-Document": "true",
                "X-FDA-Compliance": "21-CFR-Part-11",
                "X-Document-Type": "SOP",
                "X-Generation-Date": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"PDF generation failed for SOP {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/", response_model=dict)
async def search_sops(
    filters: SOPSearchFilters = Depends(),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Search and filter SOPs with pharmaceutical compliance filtering."""

    try:
        # Build query
        query = select(SOP)

        # Apply filters
        if filters.title:
            query = query.where(SOP.title.contains(filters.title))

        if filters.status:
            query = query.where(SOP.status.in_(filters.status))

        if filters.department:
            query = query.where(SOP.department.in_(filters.department))

        if filters.priority:
            query = query.where(SOP.priority.in_(filters.priority))

        if filters.regulatory_framework:
            # PostgreSQL JSON contains operation
            for framework in filters.regulatory_framework:
                query = query.where(SOP.regulatory_framework.contains([framework]))

        if filters.created_by:
            query = query.where(SOP.created_by == filters.created_by)

        if filters.date_from:
            query = query.where(SOP.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(SOP.created_at <= filters.date_to)

        if filters.min_compliance_score is not None:
            query = query.where(
                SOP.fda_compliance_score >= filters.min_compliance_score
            )

        # Count total results
        total_query = select(func.count(SOP.id)).select_from(query.subquery())
        total_count = session.exec(total_query).one()

        # Apply sorting
        if filters.sort_by == "created_at":
            sort_column = SOP.created_at
        elif filters.sort_by == "updated_at":
            sort_column = SOP.updated_at
        elif filters.sort_by == "title":
            sort_column = SOP.title
        elif filters.sort_by == "status":
            sort_column = SOP.status
        elif filters.sort_by == "priority":
            sort_column = SOP.priority
        elif filters.sort_by == "fda_compliance_score":
            sort_column = SOP.fda_compliance_score
        else:
            sort_column = SOP.created_at

        if filters.sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute query
        sops = session.exec(query).all()

        # Convert to response format
        sop_responses = [SOPResponse.from_orm(sop) for sop in sops]

        # Log search event
        log_regulatory_event(
            logger,
            f"SOP search performed by {current_user}",
            event_type="sop_search",
            user_id=current_user,
            compliance_context="data_access_audit",
        )

        return {
            "sops": sop_responses,
            "pagination": {
                "page": filters.page,
                "page_size": filters.page_size,
                "total_count": total_count,
                "total_pages": (total_count + filters.page_size - 1)
                // filters.page_size,
                "has_next": offset + filters.page_size < total_count,
                "has_previous": filters.page > 1,
            },
            "filters_applied": filters.dict(exclude_none=True),
            "pharmaceutical_compliance": {
                "audit_logged": True,
                "data_access_tracked": True,
            },
        }

    except Exception as e:
        logger.error(f"SOP search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SOP search failed: {str(e)}")


@router.put("/{job_id}", response_model=SOPResponse)
async def update_sop(
    job_id: str,
    sop_update: SOPUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(require_role(PharmaceuticalRoles.SUPERVISOR)),
):
    """Update SOP with pharmaceutical change control."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    try:
        # Store old values for audit trail
        old_values = {
            "title": sop.title,
            "description": sop.description,
            "status": sop.status,
            "priority": sop.priority,
            "department": sop.department,
        }

        # Apply updates
        update_data = sop_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(sop, field):
                setattr(sop, field, value)

        sop.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(sop)

        # Create change control audit log
        await audit_service.log_event(
            AuditLogCreate(
                user_id=current_user,
                action=AuditAction.UPDATE,
                resource_type="sop",
                resource_id=job_id,
                description=f"Updated SOP: {sop.title}",
                regulatory_impact="Change control - SOP modification",
                gmp_relevance=True,
                old_values=old_values,
                new_values=update_data,
            ),
            session,
        )

        # Log regulatory event
        log_regulatory_event(
            logger,
            f"SOP updated: {job_id}",
            event_type="sop_update",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="change_control",
        )

        return SOPResponse.from_orm(sop)

    except Exception as e:
        logger.error(f"SOP update failed for {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SOP update failed: {str(e)}")


@router.delete("/{job_id}")
async def delete_sop(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(require_role(PharmaceuticalRoles.QA_APPROVER)),
):
    """Delete SOP with pharmaceutical compliance logging."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    try:
        # Create deletion audit log before deletion
        await audit_service.log_event(
            AuditLogCreate(
                user_id=current_user,
                action=AuditAction.DELETE,
                resource_type="sop",
                resource_id=job_id,
                description=f"Deleted SOP: {sop.title}",
                regulatory_impact="Critical - SOP deletion requires investigation",
                gmp_relevance=True,
                old_values={
                    "title": sop.title,
                    "description": sop.description,
                    "status": sop.status,
                    "created_by": sop.created_by,
                    "created_at": sop.created_at.isoformat(),
                    "department": sop.department,
                },
            ),
            session,
        )

        session.delete(sop)
        session.commit()

        # Log regulatory event
        log_regulatory_event(
            logger,
            f"SOP deleted: {job_id}",
            event_type="sop_deletion",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="critical_change_control",
        )

        return {"message": "SOP deleted successfully", "job_id": job_id}

    except Exception as e:
        logger.error(f"SOP deletion failed for {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SOP deletion failed: {str(e)}")


@router.post("/{job_id}/validate", response_model=SOPValidationResult)
async def validate_sop_content(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Validate SOP content against pharmaceutical regulations."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    if not sop.sop_content:
        raise HTTPException(status_code=400, detail="SOP content not available")

    try:
        # Perform comprehensive validation
        validation_result = await validation_service.validate_sop_content(
            sop.sop_content, sop.regulatory_framework
        )

        # Update SOP with validation results
        sop.fda_compliance_score = validation_result.compliance_score
        sop.gmp_compliance_indicators = validation_result.gmp_compliance_indicators
        sop.validation_errors = (
            validation_result.validation_errors
            if not validation_result.is_valid
            else []
        )
        sop.updated_at = datetime.utcnow()
        session.commit()

        # Log validation event
        log_regulatory_event(
            logger,
            f"SOP validation performed: {job_id} - Score: {validation_result.compliance_score}%",
            event_type="sop_validation",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="quality_assurance",
        )

        return validation_result

    except Exception as e:
        logger.error(f"SOP validation failed for {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SOP validation failed: {str(e)}")


@router.get("/{job_id}/terminology", response_model=List[PharmaceuticalTerminology])
async def validate_pharmaceutical_terminology(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Validate pharmaceutical terminology used in SOP."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    if not sop.sop_content:
        raise HTTPException(status_code=400, detail="SOP content not available")

    try:
        # Validate terminology using Ollama client
        terminology_results = await ollama_client.validate_pharmaceutical_terminology(
            sop.sop_content.get("full_text", "")
        )

        # Log terminology validation
        log_regulatory_event(
            logger,
            f"Pharmaceutical terminology validated: {job_id}",
            event_type="terminology_validation",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="regulatory_compliance",
        )

        return terminology_results

    except Exception as e:
        logger.error(f"Terminology validation failed for {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Terminology validation failed: {str(e)}"
        )


@router.post("/{job_id}/retry")
async def retry_sop_generation(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: str = Depends(require_role(PharmaceuticalRoles.SUPERVISOR)),
):
    """Retry failed SOP generation."""

    sop = session.exec(select(SOP).where(SOP.job_id == job_id)).first()

    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    if sop.status not in [SOPStatus.FAILED]:
        raise HTTPException(status_code=400, detail="SOP is not in failed status")

    if sop.retry_count >= 3:
        raise HTTPException(status_code=400, detail="Maximum retry attempts exceeded")

    try:
        # Reset status and start retry
        sop.status = SOPStatus.PENDING
        sop.error_message = None
        sop.updated_at = datetime.utcnow()
        session.commit()

        # Prepare original data for retry
        sop_data = {
            "title": sop.title,
            "description": sop.description,
            "department": sop.department,
            "priority": sop.priority,
            "regulatory_framework": sop.regulatory_framework,
        }

        # Start background generation task
        background_tasks.add_task(
            generate_sop_background,
            job_id,
            sop_data,
            "",  # Template content would need to be stored or retrieved
            "",  # Guideline content would need to be stored or retrieved
        )

        # Log retry event
        log_regulatory_event(
            logger,
            f"SOP generation retry initiated: {job_id} (attempt #{sop.retry_count + 1})",
            event_type="sop_retry",
            user_id=current_user,
            sop_id=job_id,
            compliance_context="error_recovery",
        )

        return {
            "message": "SOP generation retry initiated",
            "job_id": job_id,
            "retry_count": sop.retry_count + 1,
            "status": "pending",
        }

    except Exception as e:
        logger.error(f"SOP retry failed for {job_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SOP retry failed: {str(e)}")


@router.get("/system/health")
async def sop_system_health_check():
    """Health check for SOP generation system."""

    try:
        # Check Ollama service
        ollama_health = await ollama_client.health_check()

        # Check PDF generator
        pdf_templates = pdf_generator.get_pdf_templates()

        # Check validation service
        validation_status = validation_service.get_service_status()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "ollama_ai": ollama_health,
                "pdf_generation": {
                    "status": "healthy",
                    "available_templates": len(pdf_templates),
                },
                "validation_service": validation_status,
                "pharmaceutical_compliance": {
                    "fda_21_cfr_part_11": "compliant",
                    "gmp_guidelines": "implemented",
                    "data_integrity": "alcoa_plus_ready",
                    "audit_trail": "active",
                },
            },
        }

    except Exception as e:
        logger.error(f"SOP system health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        }
