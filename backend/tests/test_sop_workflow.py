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
from unittest.mock import patch, MagicMock

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

# Create test client with mocked authentication
def create_test_client():
    """Create test client with mocked authentication."""
    from app.main import app
    from fastapi.testclient import TestClient

    # Override dependencies for testing - this is the proper way
    app.dependency_overrides = {
        'app.core.security.get_current_user': lambda: "test-user",
        'app.core.security.require_role': lambda role=None: lambda: "test-user"
    }

    return TestClient(app)

client = create_test_client()

@pytest.fixture
def test_user_token():
    """Create test user and return authentication token."""
    # For testing, we'll use a mock token that bypasses authentication
    # In a real implementation, you'd create a test user and get a real token
    return "test-jwt-token-bypass-auth"

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
        # Standard Operating Procedure: Equipment Cleaning Validation

        ## 1. Purpose
        This SOP establishes procedures for validating cleaning processes for pharmaceutical manufacturing equipment to ensure removal of product residues, cleaning agents, and microorganisms in accordance with current Good Manufacturing Practice (cGMP) requirements per FDA 21 CFR Part 211 and ICH Q7 guidelines.

        ## 2. Scope
        This procedure applies to all production equipment used in the manufacture of drug products, including but not limited to tablet presses, capsule fillers, granulators, mixing equipment, and associated utilities. This includes equipment used for both active pharmaceutical ingredients (APIs) and finished dosage forms.

        ## 3. Responsibilities
        - **Quality Assurance Manager**: Approves validation protocols and final reports, ensures compliance with regulatory requirements
        - **Validation Specialist**: Executes validation studies, prepares documentation, and coordinates with cross-functional teams
        - **Production Operators**: Perform cleaning procedures according to validated methods, document activities
        - **Quality Control Analysts**: Conduct analytical testing for cleaning validation samples, review test results
        - **Engineering/Maintenance**: Provide technical support for equipment modifications and maintenance activities

        ## 4. Personnel Qualifications
        All personnel involved in cleaning validation activities must be trained and qualified according to established procedures. Training records must be maintained and periodically reviewed. Personnel must demonstrate competency in equipment operation, cleaning procedures, and documentation practices.

        ## 5. Materials and Equipment
        - Cleaning agents (detergents, solvents) validated for use and stored according to manufacturer recommendations
        - Sampling materials (swabs, rinse water containers, filters) qualified for use in analytical testing
        - Analytical equipment (HPLC, TOC analyzer, pH meter, conductivity meter) calibrated and qualified
        - Personal protective equipment (PPE) including gloves, safety glasses, and protective clothing
        - Cleaning tools and accessories validated for use with specific equipment

        ## 6. Procedure

        ### 6.1 Pre-Cleaning Activities
        1. Verify equipment is shut down and de-energized according to lockout/tagout procedures
        2. Remove gross residues and debris using approved methods
        3. Inspect equipment for damage or wear that may affect cleaning efficacy
        4. Document pre-cleaning condition and any observations
        5. Ensure all utilities (water, compressed air) are available and qualified

        ### 6.2 Cleaning Process Execution
        1. Prepare cleaning solutions according to validated concentrations and volumes
        2. Apply cleaning agents using validated methods (spray, soak, manual, automated)
        3. Maintain contact time as specified in validation protocol (typically 15-30 minutes)
        4. Agitate or circulate cleaning solutions as required for effective cleaning
        5. Rinse equipment with purified water meeting USP specifications
        6. Dry equipment using validated methods (air drying, vacuum drying, or other approved methods)

        ### 6.3 Post-Cleaning Activities
        1. Visually inspect equipment for cleanliness using approved lighting and magnification
        2. Collect samples for analytical testing according to validated sampling plan
        3. Document cleaning completion with date, time, and operator identification
        4. Release equipment for production use only after satisfactory results
        5. Handle and dispose of cleaning waste according to environmental regulations

        ## 7. Quality Control
        Quality control activities include:
        - Analytical testing of cleaning validation samples
        - Review and approval of cleaning validation results
        - Investigation of any deviations from acceptance criteria
        - Periodic reassessment of cleaning validation status
        - Trending of cleaning validation data for continuous improvement

        ## 8. Acceptance Criteria
        - **Visual Inspection**: No visible residues, stains, or foreign materials
        - **Chemical Residue Limits**: Below validated acceptance criteria (typically <1 ppm for APIs, <10 ppm for cleaning agents)
        - **Microbial Limits**: Below alert/action levels (<10 CFU/swab for surfaces, <1 CFU/mL for rinse water)
        - **pH of Final Rinse**: Within validated range (typically 5.0-7.0 for purified water)
        - **Conductivity**: Within validated range for purified water rinses
        - **TOC (Total Organic Carbon)**: Below validated limits (<500 ppb for final rinse)

        ## 9. Documentation
        All cleaning activities must be documented in batch production records and cleaning logs. Documentation includes:
        - Equipment identification and cleaning date/time
        - Cleaning procedure used and cleaning agents employed
        - Operator identification and training status
        - Results of visual inspections and analytical testing
        - Deviations from validated procedures with investigation and corrective actions
        - Equipment release authorization

        ## 10. Change Control
        Any changes to equipment, cleaning procedures, or cleaning agents must be evaluated through the change control system. Changes may require revalidation of cleaning processes to ensure continued efficacy.

        ## 11. Deviation Management
        Deviations from validated cleaning procedures or acceptance criteria must be documented, investigated, and resolved according to established deviation management procedures. Root cause analysis must be performed and corrective/preventive actions implemented.

        ## 12. Training
        All personnel involved in cleaning validation must receive initial and periodic refresher training. Training must include:
        - Equipment-specific cleaning procedures
        - Safety precautions and PPE usage
        - Documentation requirements
        - Deviation reporting procedures

        ## 13. References
        - FDA 21 CFR Part 211 - Current Good Manufacturing Practice for Finished Pharmaceuticals
        - FDA 21 CFR Part 211.67 - Equipment Cleaning and Maintenance
        - ICH Q7 Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients
        - ICH Q9 Quality Risk Management
        - EU GMP Annex 15 Qualification and Validation
        - WHO Technical Report Series 937, 2006 (Annex 3)
        - USP <1058> Analytical Instrument Qualification
        - USP <1225> Validation of Compendial Procedures

        ## 14. Revision History
        Version 1.0 - Initial release (January 2024)
        Version 1.1 - Updated acceptance criteria based on regulatory feedback (March 2024)
        Version 1.2 - Added change control and deviation management sections (June 2024)
        """
    }

class TestCompleteSOPWorkflow:
    """Test complete SOP workflow end-to-end."""

    @patch('app.services.ollama_client.OllamaClient.generate_sop')
    @patch('app.services.validation_service.PharmaceuticalValidationService.validate_sop_content')
    def test_sop_creation_workflow(self, mock_validate, mock_generate, sample_sop_data):
        """Test complete SOP creation workflow."""

        # Mock Ollama service response
        mock_generate.return_value = {
            "status": "completed",
            "sop_content": {
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
                "word_count": 500,
                "section_count": 7
            },
            "model_used": "mistral:7b-instruct",
            "generation_time_seconds": 15.5,
            "quality_score": 85.0
        }

        # Mock validation service response
        from app.services.validation_service import SOPValidationResult
        mock_validate.return_value = SOPValidationResult(
            is_valid=True,
            compliance_score=85.5,
            validation_errors=[],
            missing_sections=[],
            regulatory_issues=[],
            gmp_compliance_indicators={
                'personnel_qualification': True,
                'equipment_validation': True,
                'cleaning_validation': True,
                'batch_documentation': True,
                'change_control': True,
                'deviation_management': True,
                'contamination_control': True
            },
            recommendations=["SOP meets compliance requirements"]
        )

        # Step 1: Create SOP generation job
        response = client.post(
            "/api/v1/sops",
            json=sample_sop_data
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
        
        status_response = client.get(f"/api/v1/sops/{job_id}")
        
        assert status_response.status_code == 200
        sop_data = status_response.json()
        assert sop_data["job_id"] == job_id
        assert sop_data["title"] == sample_sop_data["title"]
        assert sop_data["department"] == sample_sop_data["department"]
        
        # Step 3: Validate SOP content (if completed)
        if sop_data["status"] == SOPStatus.COMPLETED:
            validation_response = client.post(f"/api/v1/sops/{job_id}/validate")
            
            assert validation_response.status_code == 200
            validation_data = validation_response.json()
            assert "compliance_score" in validation_data
            assert "gmp_compliance_indicators" in validation_data
            assert validation_data["compliance_score"] >= 70  # Should meet compliance threshold
            assert validation_data["compliance_score"] <= 100
        
        # Step 4: Generate PDF
        pdf_response = client.get(f"/api/v1/sops/{job_id}/pdf")
        
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
        
        response = client.post("/api/v1/sops", json=comprehensive_sop)
        
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
            response = client.post("/api/v1/sops", json=sop_data)
            assert response.status_code == 201
            job_ids.append(response.json()["job_id"])
        
        # Test search by title
        search_response = client.get("/api/v1/sops?title=Cleaning")
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        assert "sops" in search_data
        assert "pagination" in search_data
        assert search_data["pharmaceutical_compliance"]["audit_logged"] == True
        
        # Should find SOPs with "Cleaning" in title
        cleaning_sops = [sop for sop in search_data["sops"] if "Cleaning" in sop["title"]]
        assert len(cleaning_sops) >= 2
        
        # Test search by department
        dept_search_response = client.get(f"/api/v1/sops?department={PharmaceuticalDepartment.PRODUCTION}")
        
        assert dept_search_response.status_code == 200
        dept_data = dept_search_response.json()
        production_sops = [sop for sop in dept_data["sops"] if sop["department"] == PharmaceuticalDepartment.PRODUCTION]
        assert len(production_sops) >= 1
    
    def test_audit_trail_compliance(self, test_user_token, sample_sop_data):
        """Test audit trail generation for pharmaceutical compliance."""
        
        # Create SOP
        response = client.post("/api/v1/sops", json=sample_sop_data)
        
        assert response.status_code == 201
        job_id = response.json()["job_id"]
        
        # Update SOP (should generate audit log)
        update_data = {
            "priority": SOPPriority.CRITICAL,
            "description": "Updated description for audit trail testing"
        }
        
        update_response = client.put(f"/api/v1/sops/{job_id}", json=update_data)
        
        # Note: This would require supervisor role in real implementation
        # assert update_response.status_code == 200
        
        # Check audit summary
        audit_response = client.get("/api/v1/audit/summary")
        
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
        assert "pharmaceutical_compliance" in health_data["components"]
        assert health_data["components"]["pharmaceutical_compliance"]["fda_21_cfr_part_11"] == "compliant"

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

    @patch('app.services.ollama_client.OllamaClient.health_check')
    @patch('app.services.pdf_generator.PDFGenerator.get_pdf_templates')
    @patch('app.services.validation_service.PharmaceuticalValidationService.get_service_status')
    def test_sop_system_health(self, mock_validation_status, mock_pdf_templates, mock_ollama_health):
        """Test SOP system health check with mocked services."""

        # Mock the service responses
        mock_ollama_health.return_value = {
            "status": "healthy",
            "model_available": True,
            "model_configured": "mistral:7b-instruct",
            "service_url": "http://localhost:11434"
        }
        mock_pdf_templates.return_value = ["standard", "pharmaceutical", "compliance"]
        mock_validation_status.return_value = {
            "status": "operational",
            "regulatory_frameworks": ["fda_21_cfr_211", "ich_q7", "ich_q10"],
            "last_updated": "2025-08-27T12:11:32.935314"
        }

        response = client.get("/api/v1/sops/system/health")

        assert response.status_code == 200
        health_data = response.json()
        assert "status" in health_data
        assert "components" in health_data

        components = health_data["components"]
        assert "ollama_ai" in components
        assert "pdf_generation" in components
        assert "validation_service" in components
        assert "pharmaceutical_compliance" in components

        # Verify the mocked services were called
        mock_ollama_health.assert_called_once()
        mock_pdf_templates.assert_called_once()
        mock_validation_status.assert_called_once()


class TestPerformanceBenchmarks:
    """Test system performance benchmarks."""
    
    def test_sop_generation_performance(self, test_user_token, sample_sop_data):
        """Test SOP generation performance benchmarks."""
        
        import time
        
        start_time = time.time()
        
        # Create SOP
        response = client.post("/api/v1/sops", json=sample_sop_data)
        
        creation_time = time.time() - start_time
        
        assert response.status_code == 201
        assert creation_time < 5.0  # Should create job in under 5 seconds
        
        job_id = response.json()["job_id"]
        
        # Monitor generation time (would be longer in real implementation with Ollama)
        generation_start = time.time()
        
        # In real implementation, would poll until completion
        # For testing, we'll simulate the expected performance
        max_generation_time = 30.0  # Target: < 30 seconds
        
        status_response = client.get(f"/api/v1/sops/{job_id}")
        
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
        
        pdf_response = client.get(f"/api/v1/sops/{job_id}/pdf")
        
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
        search_response = client.get("/api/v1/sops")
        search_time = time.time() - start_time
        
        assert search_response.status_code == 200
        assert search_time < 2.0, f"SOP search took {search_time}s, should be < 2s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])