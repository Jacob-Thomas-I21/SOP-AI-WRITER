from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class PharmaceuticalPromptBuilder:
    """Advanced prompt builder for pharmaceutical SOP generation with regulatory compliance."""

    def __init__(self):
        self.pharmaceutical_context = self._get_pharmaceutical_context()
        self.regulatory_frameworks = self._get_regulatory_frameworks()
        self.gmp_principles = self._get_gmp_principles()

    def _get_pharmaceutical_context(self) -> str:
        """Get pharmaceutical manufacturing context."""
        return """
        PHARMACEUTICAL MANUFACTURING CONTEXT:
        - Current Good Manufacturing Practice (cGMP) compliance is mandatory
        - All procedures must support FDA 21 CFR Part 11 electronic records requirements
        - ALCOA+ data integrity principles must be embedded (Attributable, Legible, Contemporaneous, Original, Accurate)
        - Risk-based approach following ICH Q9 Quality Risk Management
        - Validation lifecycle approach per ICH Q7 Good Manufacturing Practice
        - Change control processes must be clearly defined
        - Deviation management and CAPA (Corrective and Preventive Action) considerations
        - Equipment qualification (IQ/OQ/PQ) requirements where applicable
        - Environmental monitoring and contamination control
        - Personnel training and qualification requirements
        """

    def _get_regulatory_frameworks(self) -> Dict[str, str]:
        """Get regulatory framework descriptions."""
        return {
            "fda_21_cfr_211": """
            FDA 21 CFR Part 211 - Current Good Manufacturing Practice for Finished Pharmaceuticals:
            - Establishes minimum requirements for methods, facilities, and controls
            - Covers organization, personnel, buildings, equipment, production controls
            - Requires written procedures, batch records, and laboratory controls
            - Mandates complaint handling and returned goods procedures
            """,
            "ich_q7": """
            ICH Q7 - Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients:
            - Provides guidance for manufacturing APIs under appropriate system of controls
            - Emphasizes quality management system and personnel qualifications
            - Details building and facility requirements, equipment maintenance
            - Covers material management, production, packaging, and storage
            """,
            "ich_q10": """
            ICH Q10 - Pharmaceutical Quality System:
            - Describes comprehensive quality management system model
            - Integrates quality system elements throughout product lifecycle
            - Emphasizes continual improvement and risk management
            - Links quality system to regulatory requirements
            """,
            "who_gmp": """
            WHO GMP Guidelines:
            - Provides international standards for pharmaceutical manufacturing
            - Covers quality management, personnel, premises and equipment
            - Details production, quality control, and distribution requirements
            - Emphasizes documentation and record keeping
            """,
            "ema_gmp": """
            EMA GMP Guidelines:
            - European Medicines Agency good manufacturing practice
            - Covers medicinal products for human and veterinary use
            - Details quality management system requirements
            - Emphasizes risk management and contamination control
            """,
        }

    def _get_gmp_principles(self) -> List[str]:
        """Get core GMP principles."""
        return [
            "Manufacturing processes are clearly defined and controlled",
            "Critical processes are validated to ensure consistency and compliance",
            "All necessary facilities are provided including qualified personnel, adequate space, equipment and systems",
            "Clear instructions and procedures are written in clear, unambiguous language",
            "Operators are trained to carry out instructions correctly",
            "Records are made during manufacture to show all steps were followed",
            "Any significant deviations are fully recorded and investigated",
            "Records of manufacture and distribution enable complete history tracing",
            "Distribution minimizes any risk to product quality",
            "System exists to recall any batch of product from sale or supply",
        ]

    def build_sop_prompt(
        self,
        title: str,
        description: str,
        template_content: str,
        guideline_content: str,
        regulatory_framework: List[str] = None,
        department: str = None,
        additional_context: Dict[str, Any] = None,
    ) -> str:
        """Build comprehensive pharmaceutical SOP generation prompt."""

        # System prompt with pharmaceutical expertise
        system_prompt = f"""You are an expert pharmaceutical manufacturing SOP authoring assistant with deep knowledge of:
        - FDA 21 CFR Part 211 and related regulations
        - ICH guidelines (Q7, Q9, Q10, etc.)
        - WHO and EMA GMP requirements
        - Data integrity (ALCOA+) principles
        - Equipment qualification and validation
        - Quality risk management
        - Change control and deviation management

        {self.pharmaceutical_context}

        CRITICAL REQUIREMENTS:
        1. Follow the provided SOP template structure EXACTLY
        2. Incorporate regulatory compliance language throughout
        3. Use professional pharmaceutical terminology
        4. Ensure audit-ready documentation language
        5. Include appropriate cross-references to regulations
        6. Write in formal, precise language suitable for regulatory inspection
        7. Embed data integrity and GMP principles naturally
        8. Consider risk assessment and mitigation where applicable

        OUTPUT FORMAT: Generate ONLY the complete SOP document following the template structure. 
        Do not include commentary, explanations, or metadata - only the professional SOP content."""

        # Build regulatory context
        regulatory_context = ""
        if regulatory_framework:
            regulatory_context = "\nAPPLICABLE REGULATORY FRAMEWORKS:\n"
            for framework in regulatory_framework:
                if framework.lower() in self.regulatory_frameworks:
                    regulatory_context += (
                        f"\n{self.regulatory_frameworks[framework.lower()]}\n"
                    )

        # Build department-specific context
        department_context = ""
        if department:
            department_context = f"\nDEPARTMENT CONTEXT: {department.upper()}\n"
            department_context += self._get_department_specific_context(department)

        # Build additional context
        additional_info = ""
        if additional_context:
            additional_info = "\nADDITIONAL CONTEXT:\n"
            for key, value in additional_context.items():
                additional_info += f"- {key.replace('_', ' ').title()}: {value}\n"

        # User prompt with specific requirements
        user_prompt = f"""Generate a comprehensive Standard Operating Procedure (SOP) with the following specifications:

        TITLE: {title}

        SCOPE/DESCRIPTION:
        {description}

        TEMPLATE STRUCTURE TO FOLLOW:
        {template_content}

        REGULATORY GUIDELINE REFERENCE:
        {guideline_content}
        {regulatory_context}
        {department_context}
        {additional_info}

        PHARMACEUTICAL MANUFACTURING REQUIREMENTS:
        {self._build_gmp_requirements()}

        SPECIFIC GENERATION INSTRUCTIONS:
        1. Create a complete, professional SOP following the template structure exactly
        2. Populate each section with detailed, relevant content for the specified scope
        3. Integrate regulatory compliance language naturally throughout
        4. Use appropriate pharmaceutical terminology and industry standards
        5. Include specific procedural steps with clear acceptance criteria
        6. Embed data integrity considerations (ALCOA+ principles)
        7. Reference applicable regulations and guidelines
        8. Ensure content is audit-ready and inspection-compliant
        9. Write in formal, professional language suitable for pharmaceutical manufacturing
        10. Include appropriate safety, quality, and compliance considerations

        Generate the complete SOP document now."""

        return f"{system_prompt}\n\n{user_prompt}"

    def _get_department_specific_context(self, department: str) -> str:
        """Get department-specific manufacturing context."""
        department_contexts = {
            "production": """
            - Focus on batch manufacturing processes and controls
            - Emphasize equipment operation and maintenance procedures
            - Include environmental monitoring requirements
            - Address personnel gowning and hygiene protocols
            - Detail batch record completion and review processes
            """,
            "quality_control": """
            - Emphasize analytical testing procedures and acceptance criteria
            - Include method validation and verification requirements
            - Address sample handling and chain of custody
            - Detail out-of-specification (OOS) investigation procedures
            - Include stability testing and shelf-life determination
            """,
            "quality_assurance": """
            - Focus on review and approval processes
            - Emphasize change control and deviation management
            - Include supplier qualification and auditing procedures
            - Address complaint handling and product recalls
            - Detail validation and qualification oversight
            """,
            "regulatory_affairs": """
            - Emphasize regulatory submission requirements
            - Include post-market surveillance procedures
            - Address regulatory inspection preparedness
            - Detail pharmacovigilance and adverse event reporting
            - Include regulatory change notification processes
            """,
            "manufacturing": """
            - Focus on equipment operation and maintenance
            - Emphasize process controls and monitoring
            - Include cleaning validation procedures
            - Address utilities qualification and monitoring
            - Detail preventive maintenance programs
            """,
            "packaging": """
            - Emphasize label control and verification procedures
            - Include packaging material qualification
            - Address serialization and track-and-trace requirements
            - Detail packaging line changeover procedures
            - Include expiration dating and stability considerations
            """,
            "warehouse": """
            - Focus on storage condition monitoring and control
            - Emphasize inventory management and FEFO/FIFO procedures
            - Include temperature mapping and qualification
            - Address quarantine and release procedures
            - Detail distribution and shipping controls
            """,
            "maintenance": """
            - Emphasize preventive and predictive maintenance programs
            - Include equipment qualification (IQ/OQ/PQ) procedures
            - Address spare parts management and qualification
            - Detail calibration and verification procedures
            - Include maintenance record keeping and trending
            """,
        }

        return department_contexts.get(department.lower(), "")

    def _build_gmp_requirements(self) -> str:
        """Build GMP requirements section."""
        gmp_text = "GOOD MANUFACTURING PRACTICE (GMP) REQUIREMENTS:\n"
        for i, principle in enumerate(self.gmp_principles, 1):
            gmp_text += f"{i}. {principle}\n"

        gmp_text += """
        DATA INTEGRITY (ALCOA+) PRINCIPLES TO EMBED:
        - Attributable: All data must be traceable to the individual who created it
        - Legible: Data must be recorded clearly and permanently
        - Contemporaneous: Data must be recorded at the time the work is performed
        - Original: First capture of data or certified true copy
        - Accurate: Data must be correct and without errors
        - Plus: Complete, Consistent, Enduring, Available when needed

        VALIDATION CONSIDERATIONS:
        - Process validation according to FDA guidance and ICH Q8/Q9/Q10
        - Analytical method validation per ICH Q2(R1) guidelines
        - Computer system validation per GAMP guidelines
        - Cleaning validation per FDA guidance
        - Equipment qualification (Installation, Operational, Performance)

        RISK MANAGEMENT INTEGRATION:
        - Identify potential risks to product quality and patient safety
        - Assess probability and detectability of risks
        - Implement appropriate risk control measures
        - Monitor and review risk control effectiveness
        - Document risk management activities
        """

        return gmp_text

    def build_template_prompt(
        self,
        template_name: str,
        category: str,
        regulatory_framework: List[str],
        sections: List[str],
    ) -> str:
        """Build prompt for creating pharmaceutical SOP templates."""

        system_prompt = """You are an expert pharmaceutical template designer specializing in 
        creating regulatory-compliant SOP templates for pharmaceutical manufacturing operations."""

        user_prompt = f"""Create a comprehensive SOP template with the following specifications:

        TEMPLATE NAME: {template_name}
        CATEGORY: {category}
        REGULATORY FRAMEWORKS: {', '.join(regulatory_framework)}
        
        REQUIRED SECTIONS:
        {chr(10).join(f'- {section}' for section in sections)}

        Template should include:
        1. Clear section structure with numbering
        2. Placeholder text with guidance for each section
        3. Regulatory compliance checkpoints
        4. Data integrity considerations
        5. Validation requirements where applicable
        6. Risk assessment integration points
        7. Change control considerations

        Generate the complete template structure with detailed guidance for each section."""

        return f"{system_prompt}\n\n{user_prompt}"

    def build_validation_prompt(
        self, sop_content: str, regulatory_requirements: List[str]
    ) -> str:
        """Build prompt for validating SOP content against regulatory requirements."""

        system_prompt = """You are a pharmaceutical regulatory compliance expert specializing in 
        SOP validation and regulatory inspection preparedness."""

        user_prompt = f"""Validate the following SOP content against pharmaceutical regulatory requirements:

        SOP CONTENT TO VALIDATE:
        {sop_content}

        REGULATORY REQUIREMENTS TO CHECK:
        {chr(10).join(f'- {req}' for req in regulatory_requirements)}

        Provide validation assessment covering:
        1. Regulatory compliance gaps
        2. Missing required elements
        3. Data integrity considerations
        4. GMP principle adherence
        5. Risk assessment adequacy
        6. Validation requirements
        7. Recommended improvements

        Format as structured compliance report."""

        return f"{system_prompt}\n\n{user_prompt}"

    def build_training_prompt(
        self, base_content: str, pharmaceutical_examples: List[Dict[str, Any]]
    ) -> str:
        """Build training prompt for pharmaceutical domain fine-tuning."""

        training_examples = []
        for example in pharmaceutical_examples:
            training_examples.append(
                f"""
            INPUT: {example.get('input', '')}
            OUTPUT: {example.get('output', '')}
            CONTEXT: {example.get('context', '')}
            """
            )

        prompt = f"""
        PHARMACEUTICAL SOP TRAINING DATA

        BASE CONTEXT:
        {base_content}

        TRAINING EXAMPLES:
        {chr(10).join(training_examples)}

        PHARMACEUTICAL DOMAIN KNOWLEDGE:
        {self.pharmaceutical_context}

        REGULATORY FRAMEWORKS:
        {json.dumps(self.regulatory_frameworks, indent=2)}

        GMP PRINCIPLES:
        {chr(10).join(f'{i}. {principle}' for i, principle in enumerate(self.gmp_principles, 1))}
        """

        return prompt

    def get_prompt_templates(self) -> Dict[str, str]:
        """Get available prompt templates for different SOP types."""
        return {
            "cleaning_validation": "Template for cleaning validation SOPs with residue acceptance criteria",
            "equipment_qualification": "Template for IQ/OQ/PQ procedures with qualification protocols",
            "manufacturing_process": "Template for batch manufacturing procedures with process controls",
            "analytical_method": "Template for laboratory testing procedures with method validation",
            "change_control": "Template for change management procedures with impact assessments",
            "deviation_investigation": "Template for deviation handling with root cause analysis",
            "calibration": "Template for instrument calibration with acceptance criteria",
            "training": "Template for personnel training with competency assessments",
        }

    def build_context_aware_prompt(
        self,
        base_prompt: str,
        user_history: List[Dict[str, Any]] = None,
        system_performance: Dict[str, Any] = None,
    ) -> str:
        """Build context-aware prompt incorporating user history and system learning."""

        context_additions = []

        if user_history:
            context_additions.append("PREVIOUS USER INTERACTIONS:")
            for interaction in user_history[-5:]:  # Last 5 interactions
                context_additions.append(
                    f"- {interaction.get('type', 'unknown')}: {interaction.get('summary', '')}"
                )

        if system_performance:
            context_additions.append(
                f"""
            SYSTEM PERFORMANCE CONTEXT:
            - Average quality score: {system_performance.get('avg_quality_score', 'N/A')}
            - Common improvement areas: {', '.join(system_performance.get('improvement_areas', []))}
            - User satisfaction: {system_performance.get('user_satisfaction', 'N/A')}
            """
            )

        if context_additions:
            enhanced_prompt = f"{base_prompt}\n\nCONTEXT AWARENESS:\n{chr(10).join(context_additions)}\n\nUse this context to improve output quality and relevance."
            return enhanced_prompt

        return base_prompt
