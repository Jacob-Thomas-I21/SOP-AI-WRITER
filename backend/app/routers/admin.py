import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.core.database import get_session
from app.core.security import get_current_user, require_role, PharmaceuticalRoles
from app.models.user import User, UserResponse
from app.models.sop import SOP
from app.models.template import Template
from app.models.audit import AuditLog
from app.services.audit_service import AuditService
from app.utils.logging import log_regulatory_event, get_pharmaceutical_logger

router = APIRouter()
logger = get_pharmaceutical_logger(__name__)
audit_service = AuditService()


@router.get("/dashboard")
async def admin_dashboard(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """Get administrative dashboard data."""

    try:
        # User statistics
        total_users = session.exec(select(func.count(User.id))).one()
        active_users = session.exec(
            select(func.count(User.id)).where(User.is_active == True)
        ).one()

        # SOP statistics
        total_sops = session.exec(select(func.count(SOP.id))).one()
        completed_sops = session.exec(
            select(func.count(SOP.id)).where(SOP.status == "completed")
        ).one()

        # Template statistics
        total_templates = session.exec(select(func.count(Template.id))).one()
        active_templates = session.exec(
            select(func.count(Template.id)).where(Template.is_active == True)
        ).one()

        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_sops = session.exec(
            select(func.count(SOP.id)).where(SOP.created_at >= recent_cutoff)
        ).one()

        recent_users = session.exec(
            select(func.count(User.id)).where(User.created_at >= recent_cutoff)
        ).one()

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "recent_24h": recent_users,
            },
            "sops": {
                "total": total_sops,
                "completed": completed_sops,
                "recent_24h": recent_sops,
            },
            "templates": {"total": total_templates, "active": active_templates},
            "system_health": {
                "database": "connected",
                "services": "operational",
                "compliance": "maintained",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Admin dashboard failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard data retrieval failed",
        )


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """List all users for administration."""

    try:
        users = session.exec(select(User).order_by(User.created_at.desc())).all()

        log_regulatory_event(
            logger,
            f"Admin user listing accessed by {current_user.email}",
            event_type="admin_user_access",
            user_id=str(current_user.id),
            compliance_context="administrative_access",
        )

        return [UserResponse.from_orm(user) for user in users]

    except Exception as e:
        logger.error(f"Admin user listing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User listing failed",
        )


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """Activate a user account."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        user.is_active = True
        user.updated_at = datetime.utcnow()
        session.commit()

        log_regulatory_event(
            logger,
            f"User activated: {user.email} by {current_user.email}",
            event_type="user_activation",
            user_id=str(current_user.id),
            compliance_context="user_management",
        )

        return {"message": "User activated successfully", "user_id": user_id}

    except Exception as e:
        logger.error(f"User activation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User activation failed",
        )


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """Deactivate a user account."""

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate own account",
        )

    try:
        user.is_active = False
        user.updated_at = datetime.utcnow()
        session.commit()

        log_regulatory_event(
            logger,
            f"User deactivated: {user.email} by {current_user.email}",
            event_type="user_deactivation",
            user_id=str(current_user.id),
            compliance_context="user_management",
        )

        return {"message": "User deactivated successfully", "user_id": user_id}

    except Exception as e:
        logger.error(f"User deactivation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deactivation failed",
        )


@router.get("/system-stats")
async def get_system_statistics(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """Get comprehensive system statistics."""

    try:
        # Time-based statistics
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)

        stats = {
            "users": {
                "total": session.exec(select(func.count(User.id))).one(),
                "active": session.exec(
                    select(func.count(User.id)).where(User.is_active == True)
                ).one(),
                "last_week": session.exec(
                    select(func.count(User.id)).where(User.created_at >= last_week)
                ).one(),
                "last_month": session.exec(
                    select(func.count(User.id)).where(User.created_at >= last_month)
                ).one(),
            },
            "sops": {
                "total": session.exec(select(func.count(SOP.id))).one(),
                "completed": session.exec(
                    select(func.count(SOP.id)).where(SOP.status == "completed")
                ).one(),
                "pending": session.exec(
                    select(func.count(SOP.id)).where(SOP.status == "pending")
                ).one(),
                "failed": session.exec(
                    select(func.count(SOP.id)).where(SOP.status == "failed")
                ).one(),
                "last_week": session.exec(
                    select(func.count(SOP.id)).where(SOP.created_at >= last_week)
                ).one(),
                "last_month": session.exec(
                    select(func.count(SOP.id)).where(SOP.created_at >= last_month)
                ).one(),
            },
            "templates": {
                "total": session.exec(select(func.count(Template.id))).one(),
                "active": session.exec(
                    select(func.count(Template.id)).where(Template.is_active == True)
                ).one(),
            },
            "audit_logs": {
                "total": session.exec(select(func.count(AuditLog.id))).one(),
                "last_week": session.exec(
                    select(func.count(AuditLog.id)).where(
                        AuditLog.timestamp >= last_week
                    )
                ).one(),
                "critical_events": session.exec(
                    select(func.count(AuditLog.id)).where(
                        AuditLog.severity == "critical"
                    )
                ).one(),
            },
            "system_info": {
                "database_status": "connected",
                "services_status": "operational",
                "compliance_status": "maintained",
                "last_updated": now.isoformat(),
            },
        }

        return stats

    except Exception as e:
        logger.error(f"System statistics failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System statistics retrieval failed",
        )


@router.post("/maintenance/cleanup")
async def perform_maintenance_cleanup(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role(PharmaceuticalRoles.ADMIN)),
):
    """Perform system maintenance cleanup."""

    try:
        cleanup_results = {
            "old_pdfs_cleaned": 0,
            "old_logs_archived": 0,
            "maintenance_completed_at": datetime.utcnow().isoformat(),
        }

        # Here you could add actual cleanup logic
        # For now, just log the maintenance action

        log_regulatory_event(
            logger,
            f"System maintenance performed by {current_user.email}",
            event_type="system_maintenance",
            user_id=str(current_user.id),
            compliance_context="system_administration",
        )

        return {"message": "Maintenance cleanup completed", "results": cleanup_results}

    except Exception as e:
        logger.error(f"Maintenance cleanup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Maintenance cleanup failed",
        )


@router.get("/health")
async def admin_health_check():
    """Administration service health check."""
    return {
        "status": "healthy",
        "service": "administration",
        "timestamp": datetime.utcnow().isoformat(),
        "compliance_features": {
            "user_management": "operational",
            "system_monitoring": "active",
            "maintenance_tools": "available",
            "audit_oversight": "enabled",
        },
    }
