from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class RegulatoryChecker:
    """Checker for regulatory compliance in pharmaceutical documentation."""

    def __init__(self):
        self.regulatory_frameworks = self._load_regulatory_frameworks()
        self.compliance_rules = self._load_compliance_rules()
        self.audit_requirements = self._load_audit_requirements()
        
    def _load_regulatory_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory framework specifications."""
        return {
            "fda_21_cfr_211": {
                "name": "FDA 21 CFR Part 211 - Current Good Manufacturing Practice",
                "jurisdiction": "United States",
                "scope": "Finished pharmaceuticals",
                "required_elements": [
                    "written procedures",
                    "batch production records",
                    "laboratory control records",
                    "equipment maintenance records",
                    "personnel training records",
                    "change control procedures",
                    "deviation handling procedures"
                ],
                "documentation_requirements": {
                    "electronic_records": True,
                    "electronic_signatures": True,
                    "audit_trail": True,
                    "data_integrity": "ALCOA+"
                },
                "inspection_frequency": "every_2_years",
                "compliance_keywords": [
                    "21 CFR 211", "cGMP", "FDA", "batch record", "deviation",
                    "change control", "training", "qualification", "validation"
                ]
            },
            "ich_q7": {
                "name": "ICH Q7 - Good Manufacturing Practice for APIs",
                "jurisdiction": "International",
                "scope": "Active Pharmaceutical Ingredients",
                "required_elements": [
                    "quality management system",
                    "personnel qualifications",
                    "building and facility controls",
                    "equipment maintenance",
                    "material management",
                    "production procedures",
                    "packaging and identification",
                    "laboratory controls"
                ],
                "documentation_requirements": {
                    "written_procedures": True,
                    "batch_documentation": True,
                    "laboratory_records": True,
                    "change_control": True
                },
                "compliance_keywords": [
                    "ICH Q7", "API", "intermediate", "quality management",
                    "contamination control", "cleaning validation"
                ]
            },
            "ich_q10": {
                "name": "ICH Q10 - Pharmaceutical Quality System",
                "jurisdiction": "International",
                "scope": "Quality management system",
                "required_elements": [
                    "management responsibility",
                    "resource management",
                    "product realization",
                    "measurement and improvement",
                    "continual improvement",
                    "risk management"
                ],
                "documentation_requirements": {
                    "quality_manual": True,
                    "management_review": True,
                    "corrective_actions": True,
                    "preventive_actions": True
                },
                "compliance_keywords": [
                    "ICH Q10", "PQS", "pharmaceutical quality system",
                    "continual improvement", "management review", "risk management"
                ]
            },
            "who_gmp": {
                "name": "WHO Good Manufacturing Practices",
                "jurisdiction": "Global",
                "scope": "Pharmaceutical products",
                "required_elements": [
                    "quality management",
                    "personnel qualifications",
                    "premises and equipment",
                    "documentation",
                    "production procedures",
                    "quality control",
                    "contract manufacture",
                    "complaints and product recall"
                ],
                "documentation_requirements": {
                    "specifications": True,
                    "manufacturing_formulas": True,
                    "processing_instructions": True,
                    "packaging_instructions": True
                },
                "compliance_keywords": [
                    "WHO GMP", "pharmaceutical quality", "sterile products",
                    "non-sterile products", "biological products"
                ]
            },
            "ema_gmp": {
                "name": "EMA Good Manufacturing Practice Guidelines",
                "jurisdiction": "European Union",
                "scope": "Medicinal products",
                "required_elements": [
                    "pharmaceutical quality system",
                    "personnel responsibilities",
                    "premises and equipment",
                    "documentation procedures",
                    "production operations",
                    "quality control systems",
                    "outsourced activities",
                    "complaints and recalls"
                ],
                "documentation_requirements": {
                    "marketing_authorization": True,
                    "batch_records": True,
                    "analytical_records": True,
                    "stability_data": True
                },
                "compliance_keywords": [
                    "EMA", "Eudralex", "Volume 4", "marketing authorization",
                    "qualified person", "pharmacovigilance"
                ]
            }
        }
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance checking rules."""
        return {
            "data_integrity": {
                "description": "ALCOA+ data integrity principles",
                "requirements": [
                    "attributable", "legible", "contemporaneous", "original", "accurate",
                    "complete", "consistent", "enduring", "available"
                ],
                "validation_patterns": [
                    r"\battributable\b", r"\blegible\b", r"\bcontemporaneous\b",
                    r"\boriginal\b", r"\baccurate\b", r"\bcomplete\b",
                    r"\bconsistent\b", r"\benduring\b", r"\bavailable\b"
                ],
                "critical": True
            },
            "electronic_records": {
                "description": "21 CFR Part 11 electronic records compliance",
                "requirements": [
                    "closed system controls", "open system controls",
                    "signature manifestations", "signature/record linking",
                    "electronic signature components", "controls for identification codes"
                ],
                "validation_patterns": [
                    r"\belectronic\s+records?\b", r"\belectronic\s+signatures?\b",
                    r"\b21\s*CFR\s*(?:Part\s*)?11\b", r"\bclosed\s+system\b",
                    r"\bopen\s+system\b", r"\baudit\s+trail\b"
                ],
                "critical": True
            },
            "change_control": {
                "description": "Change control procedures",
                "requirements": [
                    "change request", "impact assessment", "risk evaluation",
                    "approval process", "implementation", "verification", "documentation"
                ],
                "validation_patterns": [
                    r"\bchange\s+control\b", r"\bchange\s+request\b",
                    r"\bimpact\s+assessment\b", r"\brisk\s+evaluation\b",
                    r"\bapproval\s+process\b"
                ],
                "critical": False
            },
            "deviation_management": {
                "description": "Deviation handling and investigation",
                "requirements": [
                    "deviation identification", "immediate actions", "investigation",
                    "root cause analysis", "corrective actions", "preventive actions",
                    "effectiveness check"
                ],
                "validation_patterns": [
                    r"\bdeviation\b", r"\binvestigation\b", r"\broot\s+cause\b",
                    r"\bcorrective\s+action\b", r"\bpreventive\s+action\b",
                    r"\bCAPAB?"
                ],
                "critical": False
            },
            "qualification_validation": {
                "description": "Equipment qualification and process validation",
                "requirements": [
                    "installation qualification", "operational qualification",
                    "performance qualification", "process validation",
                    "cleaning validation", "method validation"
                ],
                "validation_patterns": [
                    r"\bIQ\b", r"\bOQ\b", r"\bPQ\b", r"\bqualification\b",
                    r"\bvalidation\b", r"\bcleaning\s+validation\b",
                    r"\bmethod\s+validation\b"
                ],
                "critical": True
            }
        }
    
    def _load_audit_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load audit trail requirements."""
        return {
            "fda_inspection": {
                "description": "FDA inspection readiness requirements",
                "required_documentation": [
                    "batch production records", "laboratory test results",
                    "equipment maintenance logs", "training records",
                    "deviation reports", "change control records"
                ],
                "retention_period_years": 7,
                "electronic_format_required": True
            },
            "ema_inspection": {
                "description": "EMA inspection requirements",
                "required_documentation": [
                    "manufacturing authorizations", "batch records",
                    "quality control records", "stability studies",
                    "complaint handling records"
                ],
                "retention_period_years": 5,
                "electronic_format_required": False
            },
            "who_prequalification": {
                "description": "WHO prequalification requirements",
                "required_documentation": [
                    "manufacturing site master file", "quality manual",
                    "validation reports", "stability data",
                    "bioequivalence studies"
                ],
                "retention_period_years": 5,
                "electronic_format_required": False
            }
        }
    
    def check_regulatory_compliance(
        self,
        content: str,
        frameworks: List[str],
        document_type: str = "sop"
    ) -> Dict[str, Any]:
        """Check content compliance against specified regulatory frameworks."""
        
        compliance_results = {
            "overall_compliant": False,
            "compliance_score": 0.0,
            "framework_results": {},
            "missing_requirements": [],
            "recommendations": [],
            "checked_frameworks": frameworks,
            "document_type": document_type,
            "check_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            total_score = 0.0
            framework_count = 0
            
            for framework in frameworks:
                framework_key = framework.lower().replace('-', '_').replace(' ', '_')
                
                if framework_key in self.regulatory_frameworks:
                    framework_result = self._check_framework_compliance(
                        content, framework_key, self.regulatory_frameworks[framework_key]
                    )
                    compliance_results["framework_results"][framework] = framework_result
                    total_score += framework_result["compliance_score"]
                    framework_count += 1
                    
                    # Collect missing requirements
                    compliance_results["missing_requirements"].extend(
                        framework_result.get("missing_requirements", [])
                    )
                else:
                    logger.warning(f"Unknown regulatory framework: {framework}")
            
            # Calculate overall score
            if framework_count > 0:
                compliance_results["compliance_score"] = total_score / framework_count
            
            # Determine overall compliance
            compliance_results["overall_compliant"] = (
                compliance_results["compliance_score"] >= 70.0 and
                len(compliance_results["missing_requirements"]) == 0
            )
            
            # Generate recommendations
            compliance_results["recommendations"] = self._generate_compliance_recommendations(
                compliance_results
            )
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Regulatory compliance check failed: {e}", exc_info=True)
            compliance_results["error"] = str(e)
            return compliance_results
    
    def _check_framework_compliance(
        self,
        content: str,
        framework_key: str,
        framework_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance against specific regulatory framework."""
        
        content_lower = content.lower()
        
        # Check for framework-specific keywords
        keywords = framework_config.get("compliance_keywords", [])
        keyword_matches = []
        
        for keyword in keywords:
            if keyword.lower() in content_lower:
                keyword_matches.append(keyword)
        
        keyword_score = (len(keyword_matches) / len(keywords)) * 100 if keywords else 0
        
        # Check required elements
        required_elements = framework_config.get("required_elements", [])
        element_matches = []
        missing_elements = []
        
        for element in required_elements:
            element_variations = [
                element,
                element.replace('_', ' '),
                element.replace(' ', '_'),
                element.replace('-', ' ')
            ]
            
            found = False
            for variation in element_variations:
                if variation.lower() in content_lower:
                    element_matches.append(element)
                    found = True
                    break
            
            if not found:
                missing_elements.append(element)
        
        element_score = (len(element_matches) / len(required_elements)) * 100 if required_elements else 0
        
        # Check documentation requirements
        doc_requirements = framework_config.get("documentation_requirements", {})
        doc_matches = []
        missing_doc_requirements = []
        
        for req_key, required in doc_requirements.items():
            if required:
                req_variations = [
                    req_key.replace('_', ' '),
                    req_key.replace('_', '-'),
                    req_key
                ]
                
                found = False
                for variation in req_variations:
                    if variation.lower() in content_lower:
                        doc_matches.append(req_key)
                        found = True
                        break
                
                if not found:
                    missing_doc_requirements.append(req_key)
        
        doc_score = (len(doc_matches) / len(doc_requirements)) * 100 if doc_requirements else 0
        
        # Calculate overall framework compliance score
        compliance_score = (keyword_score * 0.3 + element_score * 0.4 + doc_score * 0.3)
        
        return {
            "framework_name": framework_config["name"],
            "jurisdiction": framework_config["jurisdiction"],
            "compliance_score": compliance_score,
            "keyword_score": keyword_score,
            "element_score": element_score,
            "documentation_score": doc_score,
            "matched_keywords": keyword_matches,
            "matched_elements": element_matches,
            "matched_documentation": doc_matches,
            "missing_requirements": missing_elements + missing_doc_requirements,
            "compliant": compliance_score >= 70.0
        }
    
    def check_data_integrity_compliance(self, content: str) -> Dict[str, Any]:
        """Check ALCOA+ data integrity compliance."""
        
        alcoa_rules = self.compliance_rules["data_integrity"]
        requirements = alcoa_rules["requirements"]
        patterns = alcoa_rules["validation_patterns"]
        
        content_lower = content.lower()
        matched_principles = []
        missing_principles = []
        
        for i, requirement in enumerate(requirements):
            pattern = patterns[i] if i < len(patterns) else None
            
            if pattern and re.search(pattern, content_lower):
                matched_principles.append(requirement)
            else:
                # Check for the requirement word directly
                if requirement.lower() in content_lower:
                    matched_principles.append(requirement)
                else:
                    missing_principles.append(requirement)
        
        compliance_score = (len(matched_principles) / len(requirements)) * 100
        
        return {
            "data_integrity_score": compliance_score,
            "matched_principles": matched_principles,
            "missing_principles": missing_principles,
            "total_principles": len(requirements),
            "compliant": compliance_score >= 80.0,  # High bar for data integrity
            "alcoa_plus_ready": len(missing_principles) == 0
        }
    
    def check_electronic_records_compliance(self, content: str) -> Dict[str, Any]:
        """Check 21 CFR Part 11 electronic records compliance."""
        
        er_rules = self.compliance_rules["electronic_records"]
        requirements = er_rules["requirements"]
        patterns = er_rules["validation_patterns"]
        
        content_lower = content.lower()
        matched_requirements = []
        pattern_matches = []
        
        # Check patterns first
        for pattern in patterns:
            if re.search(pattern, content_lower):
                pattern_matches.append(pattern)
        
        # Check requirements
        for requirement in requirements:
            req_words = requirement.lower().split()
            if all(word in content_lower for word in req_words):
                matched_requirements.append(requirement)
        
        pattern_score = (len(pattern_matches) / len(patterns)) * 100
        requirement_score = (len(matched_requirements) / len(requirements)) * 100
        overall_score = (pattern_score + requirement_score) / 2
        
        return {
            "electronic_records_score": overall_score,
            "pattern_score": pattern_score,
            "requirement_score": requirement_score,
            "matched_patterns": pattern_matches,
            "matched_requirements": matched_requirements,
            "missing_requirements": [req for req in requirements if req not in matched_requirements],
            "cfr_part_11_compliant": overall_score >= 75.0
        }
    
    def generate_compliance_report(
        self,
        content: str,
        sections: Dict[str, str],
        frameworks: List[str],
        document_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        
        report = {
            "report_id": f"COMP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "document_metadata": document_metadata or {},
            "frameworks_checked": frameworks,
            "overall_compliance": {
                "is_compliant": False,
                "compliance_score": 0.0,
                "critical_issues": [],
                "recommendations": []
            }
        }
        
        try:
            # Main regulatory compliance check
            regulatory_result = self.check_regulatory_compliance(content, frameworks)
            report["regulatory_compliance"] = regulatory_result
            
            # Data integrity check
            data_integrity_result = self.check_data_integrity_compliance(content)
            report["data_integrity"] = data_integrity_result
            
            # Electronic records check
            electronic_records_result = self.check_electronic_records_compliance(content)
            report["electronic_records"] = electronic_records_result
            
            # Additional compliance checks
            change_control_result = self._check_change_control_compliance(content)
            report["change_control"] = change_control_result
            
            deviation_mgmt_result = self._check_deviation_management_compliance(content)
            report["deviation_management"] = deviation_mgmt_result
            
            # Calculate overall compliance
            scores = [
                regulatory_result["compliance_score"],
                data_integrity_result["data_integrity_score"],
                electronic_records_result["electronic_records_score"],
                change_control_result["compliance_score"],
                deviation_mgmt_result["compliance_score"]
            ]
            
            overall_score = sum(scores) / len(scores)
            report["overall_compliance"]["compliance_score"] = overall_score
            
            # Determine overall compliance status
            critical_failures = []
            if not data_integrity_result["compliant"]:
                critical_failures.append("Data integrity (ALCOA+)")
            if not electronic_records_result["cfr_part_11_compliant"]:
                critical_failures.append("21 CFR Part 11 electronic records")
            if not regulatory_result["overall_compliant"]:
                critical_failures.append("Regulatory framework compliance")
            
            report["overall_compliance"]["critical_issues"] = critical_failures
            report["overall_compliance"]["is_compliant"] = (
                overall_score >= 75.0 and len(critical_failures) == 0
            )
            
            # Generate comprehensive recommendations
            all_recommendations = []
            all_recommendations.extend(regulatory_result.get("recommendations", []))
            
            if not data_integrity_result["compliant"]:
                all_recommendations.append(
                    f"Address data integrity gaps: {', '.join(data_integrity_result['missing_principles'])}"
                )
            
            if not electronic_records_result["cfr_part_11_compliant"]:
                all_recommendations.append(
                    "Implement 21 CFR Part 11 electronic records controls"
                )
            
            if overall_score < 75:
                all_recommendations.append(
                    "Comprehensive revision required to meet pharmaceutical compliance standards"
                )
            
            report["overall_compliance"]["recommendations"] = list(set(all_recommendations))
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}", exc_info=True)
            report["error"] = str(e)
            report["overall_compliance"]["is_compliant"] = False
            return report
    
    def _check_change_control_compliance(self, content: str) -> Dict[str, Any]:
        """Check change control compliance."""
        
        cc_rules = self.compliance_rules["change_control"]
        return self._check_rule_compliance(content, cc_rules, "change_control")
    
    def _check_deviation_management_compliance(self, content: str) -> Dict[str, Any]:
        """Check deviation management compliance."""
        
        dev_rules = self.compliance_rules["deviation_management"]
        return self._check_rule_compliance(content, dev_rules, "deviation_management")
    
    def _check_rule_compliance(self, content: str, rule_config: Dict[str, Any], rule_name: str) -> Dict[str, Any]:
        """Generic rule compliance checker."""
        
        content_lower = content.lower()
        requirements = rule_config["requirements"]
        patterns = rule_config.get("validation_patterns", [])
        
        matched_requirements = []
        pattern_matches = []
        
        # Check patterns
        for pattern in patterns:
            if re.search(pattern, content_lower):
                pattern_matches.append(pattern)
        
        # Check requirements
        for requirement in requirements:
            req_words = requirement.lower().split()
            if any(word in content_lower for word in req_words):
                matched_requirements.append(requirement)
        
        if requirements:
            requirement_score = (len(matched_requirements) / len(requirements)) * 100
        else:
            requirement_score = 100.0
        
        if patterns:
            pattern_score = (len(pattern_matches) / len(patterns)) * 100
        else:
            pattern_score = requirement_score
        
        compliance_score = (requirement_score + pattern_score) / 2
        
        return {
            "rule_name": rule_name,
            "compliance_score": compliance_score,
            "requirement_score": requirement_score,
            "pattern_score": pattern_score,
            "matched_requirements": matched_requirements,
            "matched_patterns": pattern_matches,
            "missing_requirements": [req for req in requirements if req not in matched_requirements],
            "compliant": compliance_score >= 60.0,
            "critical": rule_config.get("critical", False)
        }
    
    def _generate_compliance_recommendations(self, compliance_results: Dict[str, Any]) -> List[str]:
        """Generate compliance improvement recommendations."""
        
        recommendations = []
        
        # Overall score recommendations
        if compliance_results["compliance_score"] < 50:
            recommendations.append("Critical: Comprehensive revision required for regulatory compliance")
        elif compliance_results["compliance_score"] < 70:
            recommendations.append("Major improvements needed to meet regulatory standards")
        elif compliance_results["compliance_score"] < 85:
            recommendations.append("Minor improvements recommended for optimal compliance")
        
        # Framework-specific recommendations
        for framework, result in compliance_results.get("framework_results", {}).items():
            if not result["compliant"]:
                recommendations.append(f"Address {framework} compliance gaps")
                
                if result.get("missing_requirements"):
                    recommendations.append(
                        f"Add {framework} required elements: {', '.join(result['missing_requirements'][:3])}"
                    )
        
        # Missing requirements recommendations
        if compliance_results.get("missing_requirements"):
            recommendations.append(
                f"Implement missing regulatory requirements: {', '.join(compliance_results['missing_requirements'][:5])}"
            )
        
        return list(set(recommendations))
    
    def get_supported_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Get information about supported regulatory frameworks."""
        
        framework_info = {}
        for key, config in self.regulatory_frameworks.items():
            framework_info[key] = {
                "name": config["name"],
                "jurisdiction": config["jurisdiction"],
                "scope": config["scope"],
                "element_count": len(config.get("required_elements", [])),
                "documentation_requirements": len(config.get("documentation_requirements", {})),
                "keyword_count": len(config.get("compliance_keywords", []))
            }
        
        return framework_info
    
    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get regulatory checker metrics and capabilities."""
        
        return {
            "supported_frameworks": len(self.regulatory_frameworks),
            "compliance_rules": len(self.compliance_rules),
            "audit_requirements": len(self.audit_requirements),
            "framework_list": list(self.regulatory_frameworks.keys()),
            "compliance_categories": list(self.compliance_rules.keys()),
            "capabilities": [
                "Multi-framework compliance checking",
                "Data integrity (ALCOA+) validation",
                "Electronic records compliance",
                "Change control assessment",
                "Deviation management validation",
                "Comprehensive compliance reporting"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }