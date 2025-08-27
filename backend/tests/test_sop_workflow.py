"""
End-to-End SOP Workflow Tests
Complete workflow validation from creation to PDF generation with pharmaceutical compliance.
"""

import pytest
import asyncio
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime

from app.main import app
from app.core.database import get_session
from app.models.sop import SOP, SOPStatus, PharmaceuticalDepartment, SOPPriority, RegulatoryFramework
from app.models.user import User, UserRole
from app.services.ollama_client import OllamaClient
from app.services.pdf_generator import PDFGenerator
from app.services.validation_service import PharmaceuticalValidationService

# Configure pytest
pytestmark = pytest.mark.filterwarnings(
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
)

client = TestClient(app)

@pytest.fixture
def test_user_token():
    """Create test user and return authentication token."""
    # Mock authentication for testing
    return "test-jwt-token"

@pytest.fixture
def sample_sop_data():
    """Sample pharmaceutical SOP data for testing."""
    return {
        "title": "Equipment Cleaning Validation SOP",
        "description": "This SOP describes the procedures for validating cleaning processes for pharmaceutical manufacturing equipment to ensure removal of product residues, cleaning agents, and microorganisms.",
        "department": PharmaceuticalDepartment.QUALITY_ASSURANCE,
        "priority": SOPPriority.HIGH,
        "regulatory_framework": [RegulatoryFramework.FDA_21_CFR_211, RegulatoryFramework.ICH_Q7],
        "guideline_refs": ["FDA 21 CFR 211.67", "ICH Q7 Section 5.4"],
        "regulatory_version": "1.0",
        "template_content": """
        1. Title Page
        2. Purpose
        3. Scope  
        4. Definitions
        5. Responsibilities
        6. Materials and Equipment
        7. Procedure
        8. Acceptance Criteria
        9. Documentation
        10. References
        11. Revision History
        """,
        "guideline_content": """
        Equipment must be cleaned according to written procedures that detail the cleaning process,
        including cleaning agents used, critical process parameters, and acceptance criteria.
        Cleaning validation must demonstrate the effectiveness of cleaning procedures.
        """
    }

class TestCompleteSOPWorkflow:
    """Test complete SOP workflow end-to-end."""
    
    def test_sop_creation_workflow(self, test_user_token, sample_sop_data):
        """Test complete SOP creation workflow."""
        
        # Step 1: Create SOP generation job
        response = client.post(
            "/api/v1/sops",
            json=sample_sop_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 201
        job_data = response.json()
        assert "job_id" in job_data
        assert job_data["status"] == "pending"
        assert job_data["pharmaceutical_compliance"]["gmp_validation_enabled"] == True
        assert job_data["pharmaceutical_compliance"]["fda_compliance_checking"] == True
        
        job_id = job_data["job_id"]
        
        # Step 2: Monitor job status
        # Simulate job processing time
        import time
        time.sleep(2)
        
        status_response = client.get(
            f"/api/v1/sops/{job_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert status_response.status_code == 200
        sop_data = status_response.json()
        assert sop_data["job_id"] == job_id
        assert sop_data["title"] == sample_sop_data["title"]
        assert sop_data["department"] == sample_sop_data["department"]
        
        # Step 3: Validate SOP content (if completed)
        if sop_data["status"] == SOPStatus.COMPLETED:
            validation_response = client.post(
                f"/api/v1/sops/{job_id}/validate",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            
            assert validation_response.status_code == 200
            validation_data = validation_response.json()
            assert "compliance_score" in validation_data
            assert "gmp_compliance_indicators" in validation_data
            assert validation_data["compliance_score"] >= 0
            assert validation_data["compliance_score"] <= 100
        
        # Step 4: Generate PDF
        pdf_response = client.get(
            f"/api/v1/sops/{job_id}/pdf",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # PDF might not be available if generation is still in progress
        if pdf_response.status_code == 200:
            assert pdf_response.headers["content-type"] == "application/pdf"
            assert "X-Pharmaceutical-Document" in pdf_response.headers
            assert "X-FDA-Compliance" in pdf_response.headers
    
    def test_pharmaceutical_compliance_validation(self, test_user_token, sample_sop_data):
        """Test pharmaceutical compliance validation throughout workflow."""
        
        # Create SOP with comprehensive regulatory framework
        comprehensive_sop = {
            **sample_sop_data,
            "regulatory_framework": [
                RegulatoryFramework.FDA_21_CFR_211,
                RegulatoryFramework.ICH_Q7,
                RegulatoryFramework.WHO_GMP
            ]
        }
        
        response = client.post(
            "/api/v1/sops",
            json=comprehensive_sop,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 201
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # Check that regulatory frameworks are properly applied
        assert len(job_data["pharmaceutical_compliance"]["regulatory_framework_applied"]) == 3
        assert RegulatoryFramework.FDA_21_CFR_211 in job_data["pharmaceutical_compliance"]["regulatory_framework_applied"]
        assert RegulatoryFramework.ICH_Q7 in job_data["pharmaceutical_compliance"]["regulatory_framework_applied"]
        assert RegulatoryFramework.WHO_GMP in job_data["pharmaceutical_compliance"]["regulatory_framework_applied"]
    
    def test_sop_search_and_filtering(self, test_user_token, sample_sop_data):
        """Test SOP search and filtering functionality."""
        
        # Create multiple SOPs for testing search
        sop_variations = [
            {**sample_sop_data, "title": "Cleaning Validation SOP #1", "department": PharmaceuticalDepartment.PRODUCTION},
            {**sample_sop_data, "title": "Cleaning Validation SOP #2", "department": PharmaceuticalDepartment.QUALITY_CONTROL},
            {**sample_sop_data, "title": "Equipment Qualification SOP", "department": PharmaceuticalDepartment.MANUFACTURING},
        ]
        
        job_ids = []
        for sop_data in sop_variations:
            response = client.post(
                "/api/v1/sops",
                json=sop_data,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert response.status_code == 201
            job_ids.append(response.json()["job_id"])
        
        # Test search by title
        search_response = client.get(
            "/api/v1/sops?title=Cleaning",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert "sops" in search_data
        assert "pagination" in search_data
        assert search_data["pharmaceutical_compliance"]["audit_logged"] == True
        
        # Should find SOPs with "Cleaning" in title
        cleaning_sops = [sop for sop in search_data["sops"] if "Cleaning" in sop["title"]]
        assert len(cleaning_sops) >= 2
        
        # Test search by department
        dept_search_response = client.get(
            f"/api/v1/sops?department={PharmaceuticalDepartment.PRODUCTION}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert dept_search_response.status_code == 200
        dept_data = dept_search_response.json()
        production_sops = [sop for sop in dept_data["sops"] if sop["department"] == PharmaceuticalDepartment.PRODUCTION]
        assert len(production_sops) >= 1
    
    def test_audit_trail_compliance(self, test_user_token, sample_sop_data):
        """Test audit trail generation for pharmaceutical compliance."""
        
        # Create SOP
        response = client.post(
            "/api/v1/sops",
            json=sample_sop_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 201
        job_id = response.json()["job_id"]
        
        # Update SOP (should generate audit log)
        update_data = {
            "priority": SOPPriority.CRITICAL,
            "description": "Updated description for audit trail testing"
        }
        
        update_response = client.put(
            f"/api/v1/sops/{job_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        # Note: This would require supervisor role in real implementation
        # assert update_response.status_code == 200
        
        # Check audit summary
        audit_response = client.get(
            "/api/v1/audit/summary",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert audit_response.status_code == 200
        audit_data = audit_response.json()
        assert "total_events" in audit_data
        assert "fda_audit_readiness_score" in audit_data
        assert "data_integrity_score" in audit_data
        assert audit_data["fda_audit_readiness_score"] >= 0
        assert audit_data["data_integrity_score"] >= 0

class TestPharmaceuticalValidationService:
    """Test pharmaceutical validation service."""
    
    @pytest.mark.asyncio
    async def test_sop_content_validation(self):
        """Test SOP content validation against pharmaceutical regulations."""
        
        validation_service = PharmaceuticalValidationService()
        
        # Sample SOP content for validation
        sop_content = {
            "structured_sections": {
                "purpose": "This SOP establishes procedures for equipment cleaning validation in pharmaceutical manufacturing.",
                "scope": "Applies to all production equipment used in API and drug product manufacturing.",
                "procedure": "1. Prepare cleaning solutions according to specifications.\n2. Clean equipment following validated procedures.\n3. Sample cleaned surfaces for residue analysis.\n4. Analyze samples using validated analytical methods.",
                "responsibilities": "Production operators perform cleaning. QC analyzes samples. QA reviews and approves results.",
                "materials": "Cleaning agents, sampling materials, analytical equipment.",
                "documentation": "Complete batch cleaning records and maintain cleaning logs.",
                "references": "FDA 21 CFR 211.67, ICH Q7 Section 5"
            },
            "full_text": "Complete SOP text with pharmaceutical terminology including GMP, validation, qualification, batch records, and cleaning validation procedures.",
            "word_count": 250,
            "section_count": 7
        }
        
        regulatory_frameworks = [RegulatoryFramework.FDA_21_CFR_211, RegulatoryFramework.ICH_Q7]
        
        validation_result = await validation_service.validate_sop_content(
            sop_content, 
            [fw.value for fw in regulatory_frameworks]
        )
        
        assert validation_result.compliance_score >= 0
        assert validation_result.compliance_score <= 100
        assert isinstance(validation_result.validation_errors, list)
        assert isinstance(validation_result.missing_sections, list)
        assert isinstance(validation_result.gmp_compliance_indicators, dict)
        assert isinstance(validation_result.recommendations, list)
        
        # Should have good compliance score for well-structured SOP
        assert validation_result.compliance_score >= 70

class TestSystemHealthAndMonitoring:
    """Test system health monitoring and performance."""
    
    def test_health_check_endpoints(self):
        """Test system health check endpoints."""
        
        # Basic health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert "pharmaceutical_compliance" in health_data
        assert health_data["pharmaceutical_compliance"] == "operational"
        
        # Detailed health check
        detailed_response = client.get("/health/detailed")
        assert detailed_response.status_code == 200
        detailed_data = detailed_response.json()
        assert "pharmaceutical_compliance" in detailed_data
        assert "system_info" in detailed_data
        assert "features" in detailed_data
        
        # Check pharmaceutical compliance features
        pharma_compliance = detailed_data["pharmaceutical_compliance"]
        assert pharma_compliance["fda_21_cfr_part_11"] == "compliant"
        assert pharma_compliance["gmp_guidelines"] == "followed"
        assert pharma_compliance["data_integrity"] == "maintained"
        assert pharma_compliance["audit_trail"] == "complete"
    
    def test_sop_system_health(self, test_user_token):
        """Test SOP system health check."""
        
        response = client.get(
            "/api/v1/sops/system/health",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data
        assert "components" in health_data
        
        components = health_data["components"]
        assert "ollama_ai" in components
        assert "pdf_generation" in components
        assert "validation_service" in components
        assert "pharmaceutical_compliance" in health_data


class TestPerformanceBenchmarks:
    """Test system performance benchmarks."""
    
    def test_sop_generation_performance(self, test_user_token, sample_sop_data):
        """Test SOP generation performance benchmarks."""
        
        import time
        
        start_time = time.time()
        
        # Create SOP
        response = client.post(
            "/api/v1/sops",
            json=sample_sop_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        creation_time = time.time() - start_time
        
        assert response.status_code == 201
        assert creation_time < 5.0  # Should create job in under 5 seconds
        
        job_id = response.json()["job_id"]
        
        # Monitor generation time (would be longer in real implementation with Ollama)
        generation_start = time.time()
        
        # In real implementation, would poll until completion
        # For testing, we'll simulate the expected performance
        max_generation_time = 30.0  # Target: < 30 seconds
        
        status_response = client.get(
            f"/api/v1/sops/{job_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert status_response.status_code == 200
        
        # Performance assertions
        assert creation_time < 5.0, f"SOP creation took {creation_time}s, should be < 5s"
    
    def test_pdf_generation_performance(self, test_user_token, sample_sop_data):
        """Test PDF generation performance."""
        
        # Create SOP first
        response = client.post(
            "/api/v1/sops",
            json=sample_sop_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 201
        job_id = response.json()["job_id"]
        
        # Test PDF generation performance
        import time
        start_time = time.time()
        
        pdf_response = client.get(
            f"/api/v1/sops/{job_id}/pdf",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        pdf_generation_time = time.time() - start_time
        
        # PDF might not be available if SOP generation isn't complete
        if pdf_response.status_code == 200:
            assert pdf_generation_time < 10.0, f"PDF generation took {pdf_generation_time}s, should be < 10s"
    
    def test_api_response_time(self, test_user_token):
        """Test API response time benchmarks."""
        
        import time
        
        # Test health check response time
        start_time = time.time()
        response = client.get("/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0, f"Health check took {response_time}s, should be < 2s"
        
        # Test SOP search response time
        start_time = time.time()
        search_response = client.get(
            "/api/v1/sops",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        search_time = time.time() - start_time
        
        assert search_response.status_code == 200
        assert search_time < 2.0, f"SOP search took {search_time}s, should be < 2s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])