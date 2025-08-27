# Import all services for easy access - with error handling for optional dependencies
__all__ = []

# Core services that should always be available
try:
    from .ollama_client import OllamaClient

    __all__.append("OllamaClient")
except ImportError as e:
    print(f"Warning: OllamaClient not available: {e}")

try:
    from .validation_service import PharmaceuticalValidationService

    __all__.append("PharmaceuticalValidationService")
except ImportError as e:
    print(f"Warning: PharmaceuticalValidationService not available: {e}")

try:
    from .audit_service import AuditService

    __all__.append("AuditService")
except ImportError as e:
    print(f"Warning: AuditService not available: {e}")

# PDF Generator - may fail if WeasyPrint dependencies are not available
try:
    from .pdf_generator import PDFGenerator

    __all__.append("PDFGenerator")
except (ImportError, OSError) as e:
    print(f"Warning: PDFGenerator not available: {e}")

# Optional services - only import if they exist
try:
    from .template_engine import TemplateEngine

    __all__.append("TemplateEngine")
except ImportError:
    pass  # Optional service

try:
    from .database_service import DatabaseService

    __all__.append("DatabaseService")
except ImportError:
    pass  # Optional service
