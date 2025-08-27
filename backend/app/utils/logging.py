import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from app.core.config import settings


class PharmaceuticalFormatter(logging.Formatter):
    """Custom formatter for pharmaceutical compliance logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add pharmaceutical compliance fields
        if not hasattr(record, 'regulatory_event'):
            record.regulatory_event = False
        if not hasattr(record, 'gmp_relevant'):
            record.gmp_relevant = False
        if not hasattr(record, 'data_integrity'):
            record.data_integrity = 'standard'
        
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'regulatory_event': getattr(record, 'regulatory_event', False),
            'gmp_relevant': getattr(record, 'gmp_relevant', False),
            'data_integrity': getattr(record, 'data_integrity', 'standard'),
            'compliance_context': getattr(record, 'compliance_context', None),
            'audit_trail': True,  # All logs are part of audit trail
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'sop_id'):
            log_entry['sop_id'] = record.sop_id
        if hasattr(record, 'batch_number'):
            log_entry['batch_number'] = record.batch_number
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RegulatoryHandler(logging.Handler):
    """Custom handler for regulatory compliance events."""
    
    def __init__(self, compliance_log_file: str):
        super().__init__()
        self.compliance_log_file = Path(compliance_log_file)
        self.compliance_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def emit(self, record: logging.LogRecord):
        """Emit regulatory compliance events to separate log file."""
        if getattr(record, 'regulatory_event', False) or getattr(record, 'gmp_relevant', False):
            try:
                with open(self.compliance_log_file, 'a', encoding='utf-8') as f:
                    f.write(self.format(record) + '\n')
            except Exception:
                # Don't let logging errors crash the application
                pass


def setup_logging(log_level: Optional[str] = None) -> None:
    """Set up comprehensive logging for pharmaceutical compliance."""
    
    # Use settings log level if not specified
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler with pharmaceutical formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = PharmaceuticalFormatter()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation for application logs
    app_log_file = log_dir / "sop_author_app.log"
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    # Regulatory compliance handler
    compliance_log_file = log_dir / "pharmaceutical_compliance.log"
    compliance_handler = RegulatoryHandler(str(compliance_log_file))
    compliance_handler.setLevel(logging.INFO)
    compliance_handler.setFormatter(console_formatter)
    root_logger.addHandler(compliance_handler)
    
    # Error log handler for critical issues
    error_log_file = log_dir / "sop_author_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)
    
    # Audit trail handler for regulatory compliance
    audit_log_file = log_dir / "audit_trail.log"
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_log_file,
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=50,  # Keep more audit logs for compliance
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(console_formatter)
    
    # Create audit logger
    audit_logger = logging.getLogger("pharmaceutical.audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False  # Don't propagate to root logger
    
    # Set specific loggers to appropriate levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        "Pharmaceutical SOP Author logging system initialized",
        extra={
            'regulatory_event': True,
            'gmp_relevant': True,
            'compliance_context': 'system_startup',
            'data_integrity': 'high'
        }
    )


def get_compliance_logger(name: str) -> logging.Logger:
    """Get a logger configured for pharmaceutical compliance."""
    logger = logging.getLogger(f"pharmaceutical.{name}")
    return logger


def log_regulatory_event(
    logger: logging.Logger,
    message: str,
    event_type: str = "general",
    user_id: Optional[str] = None,
    sop_id: Optional[str] = None,
    batch_number: Optional[str] = None,
    compliance_context: Optional[str] = None,
    **kwargs
):
    """Log a regulatory compliance event with proper context."""
    extra_fields = {
        'regulatory_event': True,
        'gmp_relevant': True,
        'event_type': event_type,
        'compliance_context': compliance_context or event_type,
        'data_integrity': 'high',
        **kwargs
    }
    
    if user_id:
        extra_fields['user_id'] = user_id
    if sop_id:
        extra_fields['sop_id'] = sop_id
    if batch_number:
        extra_fields['batch_number'] = batch_number
    
    logger.info(message, extra=extra_fields)


def log_data_integrity_event(
    logger: logging.Logger,
    message: str,
    action: str,
    user_id: str,
    resource_type: str,
    resource_id: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    **kwargs
):
    """Log a data integrity event following ALCOA+ principles."""
    extra_fields = {
        'regulatory_event': True,
        'gmp_relevant': True,
        'data_integrity': 'critical',
        'compliance_context': 'data_integrity',
        'action': action,
        'user_id': user_id,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'attributable': True,
        'legible': True,
        'contemporaneous': True,
        'original': True,
        'accurate': True,
        **kwargs
    }
    
    if old_values:
        extra_fields['old_values'] = old_values
    if new_values:
        extra_fields['new_values'] = new_values
    
    logger.info(message, extra=extra_fields)


def log_gmp_deviation(
    logger: logging.Logger,
    message: str,
    deviation_type: str,
    severity: str,
    user_id: str,
    sop_id: Optional[str] = None,
    batch_number: Optional[str] = None,
    investigation_required: bool = True,
    **kwargs
):
    """Log a GMP deviation event."""
    extra_fields = {
        'regulatory_event': True,
        'gmp_relevant': True,
        'data_integrity': 'critical',
        'compliance_context': 'gmp_deviation',
        'deviation_type': deviation_type,
        'severity': severity,
        'user_id': user_id,
        'investigation_required': investigation_required,
        **kwargs
    }
    
    if sop_id:
        extra_fields['sop_id'] = sop_id
    if batch_number:
        extra_fields['batch_number'] = batch_number
    
    # Use appropriate log level based on severity
    if severity.lower() in ['critical', 'major']:
        logger.error(message, extra=extra_fields)
    elif severity.lower() == 'minor':
        logger.warning(message, extra=extra_fields)
    else:
        logger.info(message, extra=extra_fields)


class PharmaceuticalLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for pharmaceutical context."""
    
    def __init__(self, logger: logging.Logger, extra: dict):
        super().__init__(logger, extra)
    
    def process(self, msg, kwargs):
        # Add pharmaceutical context to all log entries
        kwargs.setdefault('extra', {}).update(self.extra)
        kwargs['extra']['pharmaceutical_system'] = True
        kwargs['extra']['audit_trail'] = True
        return msg, kwargs


def get_pharmaceutical_logger(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> PharmaceuticalLoggerAdapter:
    """Get a pharmaceutical-context logger adapter."""
    logger = logging.getLogger(name)
    
    extra_context = {
        'pharmaceutical_context': True,
        'gmp_system': True
    }
    
    if user_id:
        extra_context['user_id'] = user_id
    if session_id:
        extra_context['session_id'] = session_id
    if request_id:
        extra_context['request_id'] = request_id
    
    return PharmaceuticalLoggerAdapter(logger, extra_context)


# Compliance log retention manager
class ComplianceLogManager:
    """Manager for pharmaceutical compliance log retention."""
    
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
    
    def archive_old_logs(self, retention_days: int = 2555):  # 7 years default
        """Archive logs older than retention period."""
        import tarfile
        import os
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        archive_dir = self.log_dir / "archived"
        archive_dir.mkdir(exist_ok=True)
        
        archived_count = 0
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                # Create compressed archive
                archive_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.tar.gz"
                archive_path = archive_dir / archive_name
                
                with tarfile.open(archive_path, "w:gz") as tar:
                    tar.add(log_file, arcname=log_file.name)
                
                # Remove original file
                log_file.unlink()
                archived_count += 1
        
        return archived_count
    
    def get_compliance_summary(self) -> dict:
        """Get summary of compliance logging status."""
        summary = {
            'total_log_files': 0,
            'total_size_mb': 0,
            'compliance_events_today': 0,
            'gmp_events_today': 0,
            'data_integrity_events_today': 0,
            'log_retention_compliant': True
        }
        
        for log_file in self.log_dir.glob("*.log"):
            summary['total_log_files'] += 1
            summary['total_size_mb'] += log_file.stat().st_size / (1024 * 1024)
        
        summary['total_size_mb'] = round(summary['total_size_mb'], 2)
        
        return summary


# Initialize compliance log manager
compliance_manager = ComplianceLogManager()