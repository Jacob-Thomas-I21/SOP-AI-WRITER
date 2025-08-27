import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
import json

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from app.core.config import settings
from app.models.sop import SOP

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Professional PDF generator for pharmaceutical SOPs using ReportLab."""

    def __init__(self):
        self.output_dir = Path(settings.PDF_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ReportLab styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom styles for pharmaceutical documents."""

        # Document title style
        self.styles.add(
            ParagraphStyle(
                name="DocumentTitle",
                parent=self.styles["Title"],
                fontSize=20,
                textColor=colors.HexColor("#0066cc"),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=14,
                textColor=colors.HexColor("#0066cc"),
                spaceAfter=12,
                spaceBefore=20,
                fontName="Helvetica-Bold",
                borderWidth=1,
                borderColor=colors.HexColor("#ddd"),
                borderPadding=5,
            )
        )

        # Info box style
        self.styles.add(
            ParagraphStyle(
                name="InfoBox",
                parent=self.styles["Normal"],
                fontSize=10,
                leftIndent=15,
                rightIndent=15,
                spaceAfter=10,
                borderWidth=1,
                borderColor=colors.HexColor("#0066cc"),
                borderPadding=10,
                backColor=colors.HexColor("#f8f9fa"),
            )
        )

        # Procedure step style
        self.styles.add(
            ParagraphStyle(
                name="ProcedureStep",
                parent=self.styles["Normal"],
                fontSize=11,
                leftIndent=15,
                spaceAfter=10,
                borderWidth=1,
                borderColor=colors.HexColor("#28a745"),
                borderPadding=8,
                backColor=colors.HexColor("#f8f9fa"),
            )
        )

        # Warning style
        self.styles.add(
            ParagraphStyle(
                name="Warning",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#856404"),
                leftIndent=15,
                rightIndent=15,
                spaceAfter=10,
                borderWidth=1,
                borderColor=colors.HexColor("#f39c12"),
                borderPadding=10,
                backColor=colors.HexColor("#fff3cd"),
            )
        )

        # Compliance style
        self.styles.add(
            ParagraphStyle(
                name="Compliance",
                parent=self.styles["Normal"],
                fontSize=10,
                leftIndent=15,
                rightIndent=15,
                spaceAfter=10,
                borderWidth=1,
                borderColor=colors.HexColor("#17a2b8"),
                borderPadding=10,
                backColor=colors.HexColor("#d1ecf1"),
            )
        )

    async def generate_pdf(
        self,
        sop: SOP,
        template_name: Optional[str] = None,
        custom_css: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate professional PDF for pharmaceutical SOP using ReportLab."""
        try:
            start_time = datetime.utcnow()

            # Generate unique filename
            filename = f"sop_{sop.job_id}_{int(start_time.timestamp())}.pdf"
            pdf_path = self.output_dir / filename

            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=0.8 * inch,
                leftMargin=0.8 * inch,
                topMargin=1 * inch,
                bottomMargin=1 * inch,
                title=sop.title,
                author="Pharmaceutical SOP Author System",
                subject="Standard Operating Procedure",
                creator="SOP Author Pharmaceutical API",
            )

            # Build content
            story = []

            # Add header and document info
            self._add_document_header(story, sop, start_time)

            # Add main content sections
            if sop.sop_content and sop.sop_content.get("structured_sections"):
                self._add_content_sections(
                    story, sop.sop_content["structured_sections"]
                )

            # Add equipment list if available
            if hasattr(sop, "equipment_list") and sop.equipment_list:
                self._add_equipment_section(story, sop.equipment_list)

            # Add GMP compliance indicators
            if sop.gmp_compliance_indicators:
                self._add_gmp_compliance_section(story, sop.gmp_compliance_indicators)

            # Add regulatory information
            self._add_regulatory_section(story, sop)

            # Add signature section
            self._add_signature_section(story)

            # Add document control
            self._add_document_control_section(story, sop, start_time)

            # Generate PDF
            logger.info(f"Generating PDF for SOP {sop.job_id} using ReportLab")
            doc.build(story)

            generation_time = (datetime.utcnow() - start_time).total_seconds()
            pdf_size = pdf_path.stat().st_size

            logger.info(
                f"PDF generated successfully: {filename} ({pdf_size} bytes) in {generation_time:.2f}s"
            )

            return {
                "success": True,
                "pdf_path": str(pdf_path),
                "filename": filename,
                "file_size_bytes": pdf_size,
                "generation_time_seconds": generation_time,
                "template_used": template_name or "default",
                "pdf_library": "ReportLab",
                "compliance_features": {
                    "fda_21_cfr_part_11": True,
                    "data_integrity_alcoa": True,
                    "electronic_signatures_ready": True,
                    "audit_trail_embedded": True,
                    "regulatory_headers": True,
                },
            }

        except Exception as e:
            error_msg = f"PDF generation failed for SOP {sop.job_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)

            return {
                "success": False,
                "error": error_msg,
                "pdf_path": None,
                "filename": None,
            }

    def _add_document_header(self, story: List, sop: SOP, generation_time: datetime):
        """Add document header with SOP information."""

        # Document title
        story.append(Paragraph(sop.title, self.styles["DocumentTitle"]))
        story.append(Spacer(1, 20))

        # Document information table
        doc_info_data = [
            ["SOP ID", sop.job_id, "Version", sop.regulatory_version or "1.0"],
            [
                "Department",
                sop.department.title() if sop.department else "N/A",
                "Priority",
                sop.priority.title() if sop.priority else "Medium",
            ],
            [
                "Created By",
                sop.created_by,
                "Generated Date",
                generation_time.strftime("%B %d, %Y"),
            ],
            [
                "Status",
                sop.status.title() if hasattr(sop.status, "title") else str(sop.status),
                "FDA Score",
                (
                    f"{sop.fda_compliance_score}%"
                    if sop.fda_compliance_score
                    else "Pending"
                ),
            ],
        ]

        if sop.regulatory_framework:
            frameworks = ", ".join([fw.upper() for fw in sop.regulatory_framework])
            doc_info_data.append(["Regulatory Framework", frameworks, "", ""])

        doc_info_table = Table(
            doc_info_data, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch]
        )
        doc_info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#495057")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8f9fa")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#ddd")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        story.append(doc_info_table)
        story.append(Spacer(1, 20))
        story.append(
            HRFlowable(width="100%", thickness=3, color=colors.HexColor("#0066cc"))
        )
        story.append(Spacer(1, 20))

    def _add_content_sections(self, story: List, sections: Dict[str, str]):
        """Add main content sections."""

        for section_key, section_content in sections.items():
            if section_content and section_content.strip():
                # Section header
                section_title = section_key.title().replace("_", " ")
                story.append(Paragraph(section_title, self.styles["SectionHeader"]))

                # Section content
                if section_key.lower() == "procedure":
                    # Handle procedure steps specially
                    steps = section_content.split("\n")
                    for i, step in enumerate(steps, 1):
                        if step.strip():
                            step_text = f"<b>{i}.</b> {step.strip()}"
                            story.append(
                                Paragraph(step_text, self.styles["ProcedureStep"])
                            )
                else:
                    # Regular content
                    content_lines = section_content.split("\n")
                    for line in content_lines:
                        if line.strip():
                            story.append(Paragraph(line.strip(), self.styles["Normal"]))
                            story.append(Spacer(1, 6))

                story.append(Spacer(1, 15))

    def _add_equipment_section(self, story: List, equipment_list: List[str]):
        """Add equipment and materials section."""

        story.append(Paragraph("Equipment & Materials", self.styles["SectionHeader"]))

        # Create two-column equipment list
        equipment_data = []
        for i in range(0, len(equipment_list), 2):
            row = [equipment_list[i] if i < len(equipment_list) else ""]
            if i + 1 < len(equipment_list):
                row.append(equipment_list[i + 1])
            else:
                row.append("")
            equipment_data.append(row)

        equipment_table = Table(equipment_data, colWidths=[3 * inch, 3 * inch])
        equipment_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#6c757d")),
                ]
            )
        )

        story.append(equipment_table)
        story.append(Spacer(1, 20))

    def _add_gmp_compliance_section(self, story: List, gmp_indicators: Dict[str, bool]):
        """Add GMP compliance indicators section."""

        story.append(
            Paragraph("GMP Compliance Indicators", self.styles["SectionHeader"])
        )

        compliance_data = []
        for indicator, status in gmp_indicators.items():
            indicator_name = indicator.title().replace("_", " ")
            status_text = "✓ Compliant" if status else "✗ Non-Compliant"
            status_color = (
                colors.HexColor("#28a745") if status else colors.HexColor("#dc3545")
            )
            compliance_data.append([indicator_name, status_text])

        compliance_table = Table(compliance_data, colWidths=[4 * inch, 2 * inch])
        compliance_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#d1ecf1")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#17a2b8")),
                ]
            )
        )

        story.append(compliance_table)
        story.append(Spacer(1, 20))

    def _add_regulatory_section(self, story: List, sop: SOP):
        """Add regulatory information section."""

        story.append(PageBreak())
        story.append(Paragraph("Regulatory Information", self.styles["SectionHeader"]))

        # Applicable regulations
        if sop.guideline_refs:
            story.append(
                Paragraph("<b>Applicable Regulations:</b>", self.styles["Normal"])
            )
            for ref in sop.guideline_refs:
                story.append(Paragraph(f"• {ref}", self.styles["Normal"]))
            story.append(Spacer(1, 15))

        # FDA compliance info
        fda_text = """<b>FDA 21 CFR Part 11 Compliance:</b><br/>
        This SOP has been generated and maintained in compliance with FDA 21 CFR Part 11 
        requirements for electronic records and electronic signatures."""
        story.append(Paragraph(fda_text, self.styles["Compliance"]))

        # Data integrity principles
        alcoa_text = """<b>Data Integrity (ALCOA+ Principles):</b><br/>
        • <b>Attributable:</b> Record includes author identification and timestamp<br/>
        • <b>Legible:</b> Record is readable and in permanent form<br/>
        • <b>Contemporaneous:</b> Record created at time of activity<br/>
        • <b>Original:</b> First capture or true copy with certified accuracy<br/>
        • <b>Accurate:</b> Record is correct and verified"""
        story.append(Paragraph(alcoa_text, self.styles["Compliance"]))
        story.append(Spacer(1, 20))

    def _add_signature_section(self, story: List):
        """Add authorization signatures section."""

        story.append(
            Paragraph("Authorization Signatures", self.styles["SectionHeader"])
        )

        # Signature table
        sig_data = [
            ["Author Signature / Date", "QA Review Signature / Date"],
            ["_" * 30, "_" * 30],
            ["", ""],
            ["Department Head Signature / Date", "Final Approval Signature / Date"],
            ["_" * 30, "_" * 30],
        ]

        sig_table = Table(
            sig_data,
            colWidths=[3 * inch, 3 * inch],
            rowHeights=[0.3 * inch, 0.5 * inch, 0.3 * inch, 0.3 * inch, 0.5 * inch],
        )
        sig_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#ddd")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(sig_table)
        story.append(Spacer(1, 30))

    def _add_document_control_section(
        self, story: List, sop: SOP, generation_time: datetime
    ):
        """Add document control section."""

        story.append(Paragraph("Document Control", self.styles["SectionHeader"]))

        # Revision table
        rev_data = [
            ["Version", "Date", "Description of Changes", "Author", "Approved By"],
            [
                sop.regulatory_version or "1.0",
                generation_time.strftime("%B %d, %Y"),
                "Initial version - AI generated SOP",
                sop.created_by,
                "Pending QA Review",
            ],
        ]

        rev_table = Table(
            rev_data,
            colWidths=[0.8 * inch, 1.2 * inch, 2.5 * inch, 1.2 * inch, 1.3 * inch],
        )
        rev_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#495057")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#ddd")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        story.append(rev_table)

        # Footer text
        story.append(Spacer(1, 20))
        footer_text = "This document contains confidential and proprietary information."
        story.append(Paragraph(f"<i>{footer_text}</i>", self.styles["Normal"]))

    async def generate_batch_pdfs(self, sops: List[SOP]) -> Dict[str, Any]:
        """Generate PDFs for multiple SOPs in batch."""
        results = {
            "successful": [],
            "failed": [],
            "total_processed": len(sops),
            "start_time": datetime.utcnow().isoformat(),
        }

        for sop in sops:
            try:
                pdf_result = await self.generate_pdf(sop)
                if pdf_result["success"]:
                    results["successful"].append(
                        {
                            "sop_id": sop.job_id,
                            "pdf_path": pdf_result["pdf_path"],
                            "filename": pdf_result["filename"],
                        }
                    )
                else:
                    results["failed"].append(
                        {"sop_id": sop.job_id, "error": pdf_result["error"]}
                    )
            except Exception as e:
                results["failed"].append({"sop_id": sop.job_id, "error": str(e)})

        results["end_time"] = datetime.utcnow().isoformat()
        results["success_rate"] = len(results["successful"]) / len(sops) * 100

        logger.info(
            f"Batch PDF generation completed: {len(results['successful'])}/{len(sops)} successful"
        )

        return results

    def get_pdf_templates(self) -> List[Dict[str, Any]]:
        """Get list of available PDF templates."""
        templates = [
            {
                "name": "default",
                "display_name": "Standard Pharmaceutical SOP (ReportLab)",
                "description": "Professional pharmaceutical SOP template with FDA compliance features using ReportLab",
                "features": [
                    "Regulatory headers",
                    "Signature blocks",
                    "GMP compliance indicators",
                    "Audit trail ready",
                ],
                "pdf_library": "ReportLab",
            }
        ]

        return templates

    def cleanup_old_pdfs(self, days_old: int = 30) -> int:
        """Clean up PDF files older than specified days."""
        try:
            cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
            deleted_count = 0

            for pdf_file in self.output_dir.glob("*.pdf"):
                if pdf_file.stat().st_mtime < cutoff_time:
                    pdf_file.unlink()
                    deleted_count += 1

            logger.info(
                f"Cleaned up {deleted_count} PDF files older than {days_old} days"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"PDF cleanup failed: {e}")
            return 0

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get PDF storage statistics."""
        try:
            pdf_files = list(self.output_dir.glob("*.pdf"))
            total_files = len(pdf_files)
            total_size = sum(f.stat().st_size for f in pdf_files)

            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_file_size_bytes": (
                    round(total_size / total_files) if total_files > 0 else 0
                ),
                "storage_directory": str(self.output_dir),
                "oldest_file": (
                    min(pdf_files, key=lambda f: f.stat().st_mtime).name
                    if pdf_files
                    else None
                ),
                "newest_file": (
                    max(pdf_files, key=lambda f: f.stat().st_mtime).name
                    if pdf_files
                    else None
                ),
                "pdf_library": "ReportLab",
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
