from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class PharmaceuticalValidator:
    """Validator for pharmaceutical content and terminology."""

    def __init__(self):
        self.pharmaceutical_terms = self._load_pharmaceutical_terms()
        self.regulatory_patterns = self._load_regulatory_patterns()
        self.gmp_requirements = self._load_gmp_requirements()
        
    def _load_pharmaceutical_terms(self) -> Dict[str, Dict[str, str]]:
        """Load pharmaceutical terminology database."""
        return {
            "api": {
                "definition": "Active Pharmaceutical Ingredient",
                "category": "manufacturing",
                "regulatory_source": "ICH Q7"
            },
            "gmp": {
                "definition": "Good Manufacturing Practice",
                "category": "quality_system",
                "regulatory_source": "21 CFR 211"
            },
            "validation": {
                "definition": "Process of proving that a system works as intended",
                "category": "quality_assurance",
                "regulatory_source": "FDA Guidance"
            },
            "qualification": {
                "definition": "Proving that equipment works as intended",
                "category": "equipment",
                "regulatory_source": "21 CFR 211.68"
            },
            "deviation": {
                "definition": "Departure from approved instructions",
                "category": "quality_control",
                "regulatory_source": "ICH Q10"
            },
            "batch": {
                "definition": "Quantity of drug produced in one cycle",
                "category": "manufacturing",
                "regulatory_source": "21 CFR 210.3"
            },
            "lot": {
                "definition": "Portion of a batch with uniform characteristics",
                "category": "manufacturing",
                "regulatory_source": "21 CFR 210.3"
            },
            "capa": {
                "definition": "Corrective and Preventive Action",
                "category": "quality_system",
                "regulatory_source": "21 CFR 820.100"
            },
            "change_control": {
                "definition": "Managing changes to processes and procedures",
                "category": "quality_system",
                "regulatory_source": "ICH Q10"
            },
            "cleaning_validation": {
                "definition": "Proving cleaning procedures work properly",
                "category": "validation",
                "regulatory_source": "FDA Guidance"
            },
            "cross_contamination": {
                "definition": "Contamination between materials or products",
                "category": "contamination_control",
                "regulatory_source": "WHO GMP"
            },
            "sterile": {
                "definition": "Free from viable microorganisms",
                "category": "contamination_control",
                "regulatory_source": "USP <71>"
            },
            "aseptic": {
                "definition": "Preventing microbial contamination",
                "category": "manufacturing",
                "regulatory_source": "FDA Guidance"
            },
            "bioburden": {
                "definition": "Level of microbial contamination",
                "category": "microbiology",
                "regulatory_source": "USP <61>"
            },
            "endotoxin": {
                "definition": "Toxic substances in bacterial cell walls",
                "category": "microbiology",
                "regulatory_source": "USP <85>"
            }
        }
    
    def _load_regulatory_patterns(self) -> Dict[str, List[str]]:
        """Load regulatory compliance patterns."""
        return {
            "fda_21_cfr_211": [
                r"\b21\s*CFR\s*(?:Part\s*)?211\b",
                r"\bcGMP\b",
                r"\bCurrent\s+Good\s+Manufacturing\s+Practice\b",
                r"\bFDA\s+(?:guidance|guideline|regulation)\b"
            ],
            "ich_q7": [
                r"\bICH\s*Q7\b",
                r"\bAPI\s+(?:manufacturing|production)\b",
                r"\bActive\s+Pharmaceutical\s+Ingredient\b",
                r"\bGMP\s+guide\s+for\s+APIs\b"
            ],
            "ich_q10": [
                r"\bICH\s*Q10\b",
                r"\bPharmaceutical\s+Quality\s+System\b",
                r"\bPQS\b",
                r"\bquality\s+management\s+system\b"
            ],
            "who_gmp": [
                r"\bWHO\s+GMP\b",
                r"\bWorld\s+Health\s+Organization\b.*GMP",
                r"\bWHO\s+(?:guidance|guideline)\b"
            ],
            "ema_gmp": [
                r"\bEMA\s+GMP\b",
                r"\bEuropean\s+Medicines\s+Agency\b",
                r"\bEudraLex\b",
                r"\bVolume\s+4\b"
            ]
        }
    
    def _load_gmp_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load GMP requirement categories."""
        return {
            "personnel": {
                "description": "Personnel qualification and training requirements",
                "keywords": ["training", "qualification", "competency", "authorization", "personnel"],
                "weight": 15
            },
            "facilities": {
                "description": "Facility design and environmental controls",
                "keywords": ["facility", "building", "hvac", "environmental", "design"],
                "weight": 10
            },
            "equipment": {
                "description": "Equipment qualification and maintenance",
                "keywords": ["equipment", "qualification", "calibration", "maintenance", "iq", "oq", "pq"],
                "weight": 20
            },
            "materials": {
                "description": "Material handling and control",
                "keywords": ["material", "component", "raw material", "storage", "handling"],
                "weight": 10
            },
            "production": {
                "description": "Production procedures and controls",
                "keywords": ["production", "manufacturing", "process", "procedure", "batch"],
                "weight": 20
            },
            "quality_control": {
                "description": "Quality control testing and procedures",
                "keywords": ["quality control", "testing", "analysis", "specification", "method"],
                "weight": 15
            },
            "documentation": {
                "description": "Documentation and record keeping",
                "keywords": ["documentation", "record", "batch record", "logbook", "signature"],
                "weight": 10
            }
        }
    
    def validate_pharmaceutical_terminology(self, content: str) -> Dict[str, Any]:
        """Validate pharmaceutical terminology usage in content."""
        
        content_lower = content.lower()
        found_terms = []
        missing_critical_terms = []
        
        # Check for pharmaceutical terms
        for term, details in self.pharmaceutical_terms.items():
            if term.lower() in content_lower or term.replace('_', ' ').lower() in content_lower:
                found_terms.append({
                    "term": term,
                    "definition": details["definition"],
                    "category": details["category"],
                    "regulatory_source": details["regulatory_source"],
                    "found": True
                })
        
        # Check for critical missing terms based on content type
        critical_terms = ["gmp", "validation", "qualification", "batch", "deviation"]
        for critical_term in critical_terms:
            if critical_term not in [t["term"] for t in found_terms]:
                missing_critical_terms.append(critical_term)
        
        # Calculate terminology score
        terminology_score = min(100, (len(found_terms) / max(1, len(critical_terms))) * 100)
        
        return {
            "terminology_score": terminology_score,
            "found_terms": found_terms,
            "missing_critical_terms": missing_critical_terms,
            "total_pharmaceutical_terms": len(self.pharmaceutical_terms),
            "terms_found_count": len(found_terms)
        }
    
    def validate_regulatory_compliance(self, content: str, frameworks: List[str]) -> Dict[str, Any]:
        """Validate regulatory framework compliance."""
        
        compliance_results = {}
        overall_score = 0.0
        
        for framework in frameworks:
            framework_lower = framework.lower()
            
            if framework_lower in self.regulatory_patterns:
                patterns = self.regulatory_patterns[framework_lower]
                matches = []
                
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        matches.append(pattern)
                
                # Calculate framework compliance score
                framework_score = (len(matches) / len(patterns)) * 100
                
                compliance_results[framework] = {
                    "score": framework_score,
                    "patterns_matched": len(matches),
                    "total_patterns": len(patterns),
                    "matched_patterns": matches,
                    "compliant": framework_score >= 50.0
                }
                
                overall_score += framework_score
        
        # Average the scores
        if frameworks:
            overall_score = overall_score / len(frameworks)
        
        return {
            "overall_compliance_score": overall_score,
            "framework_results": compliance_results,
            "frameworks_evaluated": len(frameworks),
            "compliant_frameworks": sum(1 for result in compliance_results.values() if result["compliant"])
        }
    
    def validate_gmp_compliance(self, content: str) -> Dict[str, Any]:
        """Validate GMP compliance indicators."""
        
        content_lower = content.lower()
        gmp_results = {}
        total_score = 0.0
        
        for category, config in self.gmp_requirements.items():
            keywords = config["keywords"]
            weight = config["weight"]
            
            # Check for keyword presence
            keyword_matches = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    keyword_matches += 1
                    matched_keywords.append(keyword)
            
            # Calculate category score
            category_score = (keyword_matches / len(keywords)) * 100
            weighted_score = (category_score * weight) / 100
            
            gmp_results[category] = {
                "score": category_score,
                "weight": weight,
                "weighted_score": weighted_score,
                "keywords_matched": keyword_matches,
                "total_keywords": len(keywords),
                "matched_keywords": matched_keywords,
                "compliant": category_score >= 30.0
            }
            
            total_score += weighted_score
        
        return {
            "gmp_compliance_score": total_score,
            "category_results": gmp_results,
            "compliant_categories": sum(1 for result in gmp_results.values() if result["compliant"]),
            "total_categories": len(self.gmp_requirements)
        }
    
    def validate_section_completeness(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Validate SOP section completeness."""
        
        required_sections = [
            "purpose", "scope", "responsibilities", "procedure", 
            "materials", "documentation", "references", "safety"
        ]
        
        present_sections = []
        missing_sections = []
        incomplete_sections = []
        
        for required_section in required_sections:
            section_found = False
            section_content = ""
            
            # Check for section variations
            for section_key, content in sections.items():
                if required_section.lower() in section_key.lower():
                    section_found = True
                    section_content = content
                    break
            
            if section_found:
                if len(section_content.strip()) > 30:  # Minimum content length
                    present_sections.append(required_section)
                else:
                    incomplete_sections.append(required_section)
            else:
                missing_sections.append(required_section)
        
        # Calculate completeness score
        completeness_score = (len(present_sections) / len(required_sections)) * 100
        
        return {
            "completeness_score": completeness_score,
            "present_sections": present_sections,
            "missing_sections": missing_sections,
            "incomplete_sections": incomplete_sections,
            "total_required_sections": len(required_sections),
            "present_sections_count": len(present_sections)
        }
    
    def validate_content_quality(self, content: str) -> Dict[str, Any]:
        """Validate overall content quality metrics."""
        
        # Basic quality checks
        word_count = len(content.split())
        sentence_count = len(re.findall(r'[.!?]+', content))
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Check for common quality indicators
        has_numbered_steps = bool(re.search(r'\d+\.\s+', content))
        has_bullet_points = bool(re.search(r'[•\-\*]\s+', content))
        has_headers = bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE))
        has_tables = bool(re.search(r'\|.*\|', content))
        
        # Professional language indicators
        professional_indicators = [
            r'\bshall\b', r'\bmust\b', r'\brequired\b', r'\bmandatory\b',
            r'\bprocedure\b', r'\bspecification\b', r'\bstandard\b'
        ]
        
        professional_score = 0
        for indicator in professional_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                professional_score += 1
        
        professional_score = min(100, (professional_score / len(professional_indicators)) * 100)
        
        # Calculate overall quality score
        quality_metrics = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "has_numbered_steps": has_numbered_steps,
            "has_bullet_points": has_bullet_points,
            "has_headers": has_headers,
            "has_tables": has_tables,
            "professional_language_score": professional_score,
            "adequate_length": word_count >= 200,
            "well_structured": paragraph_count >= 3
        }
        
        # Overall quality score calculation
        structure_score = sum([
            has_numbered_steps, has_bullet_points, has_headers, 
            quality_metrics["adequate_length"], quality_metrics["well_structured"]
        ]) * 20  # 5 factors * 20 points each
        
        overall_quality_score = (structure_score + professional_score) / 2
        
        return {
            "quality_score": overall_quality_score,
            "metrics": quality_metrics,
            "recommendations": self._generate_quality_recommendations(quality_metrics)
        }
    
    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving content quality."""
        
        recommendations = []
        
        if metrics["word_count"] < 200:
            recommendations.append("Increase content length - aim for at least 200 words")
        
        if not metrics["has_numbered_steps"]:
            recommendations.append("Add numbered steps to improve procedure clarity")
        
        if not metrics["has_headers"]:
            recommendations.append("Include section headers for better organization")
        
        if metrics["paragraph_count"] < 3:
            recommendations.append("Break content into more paragraphs for better readability")
        
        if metrics["professional_language_score"] < 50:
            recommendations.append("Use more professional pharmaceutical terminology")
        
        if not metrics["has_bullet_points"] and not metrics["has_numbered_steps"]:
            recommendations.append("Use bullet points or numbered lists for better structure")
        
        return recommendations
    
    def comprehensive_validation(
        self,
        content: str,
        sections: Dict[str, str],
        frameworks: List[str]
    ) -> Dict[str, Any]:
        """Perform comprehensive pharmaceutical validation."""
        
        try:
            # Perform all validation checks
            terminology_result = self.validate_pharmaceutical_terminology(content)
            regulatory_result = self.validate_regulatory_compliance(content, frameworks)
            gmp_result = self.validate_gmp_compliance(content)
            section_result = self.validate_section_completeness(sections)
            quality_result = self.validate_content_quality(content)
            
            # Calculate overall score
            scores = [
                terminology_result["terminology_score"] * 0.2,
                regulatory_result["overall_compliance_score"] * 0.25,
                gmp_result["gmp_compliance_score"] * 0.25,
                section_result["completeness_score"] * 0.2,
                quality_result["quality_score"] * 0.1
            ]
            
            overall_score = sum(scores)
            
            # Determine validation status
            is_valid = (
                overall_score >= 70.0 and
                len(section_result["missing_sections"]) == 0 and
                terminology_result["terminology_score"] >= 50.0
            )
            
            # Compile all recommendations
            all_recommendations = quality_result["recommendations"].copy()
            
            if terminology_result["missing_critical_terms"]:
                all_recommendations.append(
                    f"Include critical pharmaceutical terms: {', '.join(terminology_result['missing_critical_terms'])}"
                )
            
            if section_result["missing_sections"]:
                all_recommendations.append(
                    f"Add missing sections: {', '.join(section_result['missing_sections'])}"
                )
            
            if regulatory_result["overall_compliance_score"] < 70:
                all_recommendations.append(
                    "Improve regulatory compliance by referencing applicable guidelines"
                )
            
            return {
                "is_valid": is_valid,
                "overall_score": overall_score,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "detailed_results": {
                    "terminology": terminology_result,
                    "regulatory_compliance": regulatory_result,
                    "gmp_compliance": gmp_result,
                    "section_completeness": section_result,
                    "content_quality": quality_result
                },
                "recommendations": all_recommendations,
                "summary": {
                    "terminology_score": terminology_result["terminology_score"],
                    "regulatory_score": regulatory_result["overall_compliance_score"],
                    "gmp_score": gmp_result["gmp_compliance_score"],
                    "completeness_score": section_result["completeness_score"],
                    "quality_score": quality_result["quality_score"],
                    "overall_score": overall_score
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive validation failed: {e}", exc_info=True)
            return {
                "is_valid": False,
                "overall_score": 0.0,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "recommendations": ["Contact system administrator - validation error"]
            }
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation service metrics."""
        
        return {
            "pharmaceutical_terms_count": len(self.pharmaceutical_terms),
            "regulatory_frameworks_supported": len(self.regulatory_patterns),
            "gmp_categories": len(self.gmp_requirements),
            "validation_capabilities": [
                "Pharmaceutical terminology validation",
                "Regulatory framework compliance",
                "GMP compliance indicators",
                "Section completeness checking",
                "Content quality assessment"
            ],
            "supported_frameworks": list(self.regulatory_patterns.keys()),
            "last_updated": datetime.utcnow().isoformat()
        }