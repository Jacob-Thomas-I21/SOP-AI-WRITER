from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.core.security import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/demo-auth")
async def get_demo_auth_token():
    """Get demo authentication token for showcase purposes."""
    
    # Create a demo token for showcase
    access_token = create_access_token(
        subject="demo_user",
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "user": {
            "username": "demo_user",
            "role": "supervisor",
            "department": "production"
        },
        "message": "Demo authentication token generated for showcase"
    }

@router.get("/demo-status")
async def demo_status():
    """Demo status endpoint."""
    return {
        "status": "ready",
        "message": "Demo system is ready for showcase",
        "features": [
            "SOP Creation Wizard",
            "AI-Powered Content Generation",
            "Pharmaceutical Compliance Validation",
            "PDF Export Functionality",
            "Audit Trail Logging"
        ]
    }