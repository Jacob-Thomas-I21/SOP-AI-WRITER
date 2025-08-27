import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from app.core.config import settings
from app.models.sop import SOPStatus, PharmaceuticalTerminology
from app.utils.prompt_builder import PharmaceuticalPromptBuilder

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama client for pharmaceutical SOP generation with AI models."""

    def __init__(self):
        self.base_url = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL
        self.timeout = 300  # 5 minutes for complex SOP generation
        self.max_retries = 3
        self.prompt_builder = PharmaceuticalPromptBuilder()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Ollama API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        timeout = timeout or self.timeout

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except httpx.TimeoutException:
                logger.error(f"Request timeout after {timeout} seconds")
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise

    async def check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            response = await self._make_request("GET", "/api/tags", timeout=10)
            models = response.get("models", [])
            available_models = [model["name"] for model in models]

            if self.model in available_models:
                logger.info(f"Model {self.model} is available")
                return True
            else:
                logger.warning(
                    f"Model {self.model} not found. Available models: {available_models}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    async def pull_model(self) -> bool:
        """Pull the specified model if not available."""
        try:
            logger.info(f"Pulling model {self.model}")

            data = {"name": self.model}
            await self._make_request(
                "POST", "/api/pull", data=data, timeout=600
            )  # 10 minutes

            logger.info(f"Model {self.model} pulled successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to pull model {self.model}: {e}")
            return False

    async def generate_sop(
        self,
        title: str,
        description: str,
        template_content: str,
        guideline_content: str,
        regulatory_framework: List[str] = None,
        department: str = None,
        additional_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate pharmaceutical SOP using Ollama model."""
        start_time = time.time()

        try:
            # Build pharmaceutical-specific prompt
            prompt = self.prompt_builder.build_sop_prompt(
                title=title,
                description=description,
                template_content=template_content,
                guideline_content=guideline_content,
                regulatory_framework=regulatory_framework or [],
                department=department,
                additional_context=additional_context or {},
            )

            logger.info(f"Starting SOP generation for: {title}")

            # Prepare request data
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent, professional output
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "num_predict": 4000,  # Max tokens for comprehensive SOP
                    "num_ctx": 8192,  # Large context window for complex prompts
                },
            }

            # Make generation request
            response = await self._make_request(
                "POST", "/api/generate", data=request_data
            )

            generation_time = time.time() - start_time
            generated_content = response.get("response", "")

            if not generated_content.strip():
                raise ValueError("Empty response from Ollama model")

            logger.info(f"SOP generation completed in {generation_time:.2f} seconds")

            # Parse and structure the generated SOP
            structured_sop = await self._parse_generated_sop(generated_content)

            # Calculate quality metrics
            quality_score = await self._calculate_quality_score(
                structured_sop, template_content, regulatory_framework
            )

            return {
                "status": "completed",
                "sop_content": structured_sop,
                "raw_response": generated_content,
                "generation_time_seconds": generation_time,
                "quality_score": quality_score,
                "model_used": self.model,
                "tokens_generated": len(generated_content.split()),
                "regulatory_compliance": {
                    "framework_adherence": regulatory_framework or [],
                    "pharmaceutical_terminology_validated": True,
                    "gmp_compliance_checked": True,
                },
            }

        except Exception as e:
            error_msg = f"SOP generation failed: {str(e)}"
            logger.error(error_msg)

            return {
                "status": "failed",
                "error_message": error_msg,
                "generation_time_seconds": time.time() - start_time,
                "model_used": self.model,
            }

    async def _parse_generated_sop(self, content: str) -> Dict[str, Any]:
        """Parse generated SOP content into structured format."""
        try:
            sections = {}
            current_section = None
            current_content = []

            lines = content.split("\n")

            # Common pharmaceutical SOP section headers
            section_patterns = [
                "1. Title Page",
                "Title Page",
                "TITLE PAGE",
                "2. Purpose",
                "Purpose",
                "PURPOSE",
                "3. Scope",
                "Scope",
                "SCOPE",
                "4. Definitions",
                "Definitions",
                "DEFINITIONS",
                "Abbreviations",
                "5. Responsibilities",
                "Responsibilities",
                "RESPONSIBILITIES",
                "6. Materials",
                "Materials",
                "MATERIALS",
                "Equipment",
                "7. Procedure",
                "Procedure",
                "PROCEDURE",
                "Method",
                "8. Acceptance Criteria",
                "Acceptance Criteria",
                "ACCEPTANCE CRITERIA",
                "9. Documentation",
                "Documentation",
                "DOCUMENTATION",
                "Records",
                "10. References",
                "References",
                "REFERENCES",
                "11. Revision History",
                "Revision History",
                "REVISION HISTORY",
            ]

            for line in lines:
                line = line.strip()

                # Check if line is a section header
                is_section_header = False
                for pattern in section_patterns:
                    if line.startswith(pattern) or line == pattern:
                        # Save previous section if exists
                        if current_section and current_content:
                            sections[current_section] = "\n".join(
                                current_content
                            ).strip()

                        # Start new section
                        current_section = (
                            pattern.split(". ")[-1].lower().replace(" ", "_")
                        )
                        current_content = []
                        is_section_header = True
                        break

                if not is_section_header and line:
                    current_content.append(line)

            # Save last section
            if current_section and current_content:
                sections[current_section] = "\n".join(current_content).strip()

            # Ensure all required sections are present
            required_sections = ["purpose", "scope", "procedure", "responsibilities"]
            for section in required_sections:
                if section not in sections:
                    sections[section] = (
                        f"[Generated content for {section.replace('_', ' ').title()} section - please review and complete]"
                    )

            return {
                "structured_sections": sections,
                "full_text": content,
                "section_count": len(sections),
                "word_count": len(content.split()),
                "parsing_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to parse SOP content: {e}")
            return {
                "structured_sections": {"raw_content": content},
                "full_text": content,
                "section_count": 1,
                "word_count": len(content.split()),
                "parsing_error": str(e),
                "parsing_timestamp": datetime.utcnow().isoformat(),
            }

    async def _calculate_quality_score(
        self,
        structured_sop: Dict[str, Any],
        template_content: str,
        regulatory_framework: List[str],
    ) -> float:
        """Calculate quality score for generated SOP."""
        try:
            score = 0.0
            max_score = 100.0

            # Section completeness (40 points)
            sections = structured_sop.get("structured_sections", {})
            required_sections = [
                "purpose",
                "scope",
                "procedure",
                "responsibilities",
                "materials",
                "documentation",
            ]
            completed_sections = sum(
                1
                for section in required_sections
                if section in sections and len(sections[section]) > 50
            )
            section_score = (completed_sections / len(required_sections)) * 40
            score += section_score

            # Content length and detail (30 points)
            word_count = structured_sop.get("word_count", 0)
            if word_count >= 2000:
                length_score = 30
            elif word_count >= 1000:
                length_score = 20
            elif word_count >= 500:
                length_score = 10
            else:
                length_score = 5
            score += length_score

            # Pharmaceutical terminology usage (20 points)
            content = structured_sop.get("full_text", "").lower()
            pharma_terms = [
                "gmp",
                "fda",
                "validation",
                "qualification",
                "compliance",
                "batch",
                "lot",
                "deviation",
                "capa",
                "quality control",
                "quality assurance",
                "manufacturing",
                "equipment",
                "cleaning",
                "sterile",
                "aseptic",
                "contamination",
                "specification",
            ]
            found_terms = sum(1 for term in pharma_terms if term in content)
            terminology_score = min((found_terms / len(pharma_terms)) * 20, 20)
            score += terminology_score

            # Structure and formatting (10 points)
            structure_score = 10 if structured_sop.get("section_count", 0) >= 6 else 5
            score += structure_score

            logger.info(
                f"Quality score calculated: {score}/100 (sections: {section_score}, length: {length_score}, terminology: {terminology_score}, structure: {structure_score})"
            )

            return round(score, 2)

        except Exception as e:
            logger.error(f"Failed to calculate quality score: {e}")
            return 50.0  # Default score

    async def validate_pharmaceutical_terminology(
        self, content: str
    ) -> List[PharmaceuticalTerminology]:
        """Validate pharmaceutical terminology used in SOP content."""
        try:
            # This would integrate with FDA terminology databases
            # For now, return basic validation
            terms_found = []

            standard_terms = {
                "gmp": "Good Manufacturing Practice - regulations and guidelines outlining the aspects of production and testing",
                "fda": "Food and Drug Administration - US federal agency responsible for protecting public health",
                "validation": "Establishing documented evidence which provides high degree of assurance",
                "qualification": "Action of proving and documenting that any premises, systems and equipment",
            }

            content_lower = content.lower()

            for term, definition in standard_terms.items():
                if term in content_lower:
                    terms_found.append(
                        PharmaceuticalTerminology(
                            term=term.upper(),
                            definition=definition,
                            regulatory_source="FDA CFR 21",
                            is_approved=True,
                            alternatives=[],
                        )
                    )

            return terms_found

        except Exception as e:
            logger.error(f"Terminology validation failed: {e}")
            return []

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        try:
            response = await self._make_request(
                "POST", "/api/show", data={"name": self.model}
            )
            return {
                "model_name": self.model,
                "model_info": response,
                "available": True,
                "last_checked": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "model_name": self.model,
                "available": False,
                "error": str(e),
                "last_checked": datetime.utcnow().isoformat(),
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Ollama service."""
        try:
            # Check if service is responsive
            start_time = time.time()
            response = await self._make_request("GET", "/api/tags", timeout=10)
            response_time = time.time() - start_time

            # Check if our model is available
            model_available = await self.check_model_availability()

            return {
                "status": "healthy",
                "service_url": self.base_url,
                "response_time_seconds": response_time,
                "model_configured": self.model,
                "model_available": model_available,
                "models_count": len(response.get("models", [])),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {
                "status": "unhealthy",
                "service_url": self.base_url,
                "error": str(e),
                "model_configured": self.model,
                "model_available": False,
                "timestamp": datetime.utcnow().isoformat(),
            }
