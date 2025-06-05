"""Structured logging configuration with HIPAA compliance for PhysioSOAP MVP."""

import re
import sys
import structlog
from typing import Any, Dict, Optional
from config import settings


# PHI patterns for redaction (when HIPAA_MODE is enabled)
PHI_PATTERNS = [
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN_REDACTED]'),  # SSN
    (re.compile(r'\b\d{10,}\b'), '[PHONE_REDACTED]'),  # Phone numbers
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL_REDACTED]'),  # Email
    (re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'), '[NAME_REDACTED]'),  # Names (basic pattern)
]


def redact_phi(message: str) -> str:
    """Redact PHI from log messages when HIPAA mode is enabled."""
    if not settings.hipaa_mode:
        return message
    
    redacted = message
    for pattern, replacement in PHI_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    
    return redacted


def phi_processor(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Process log events to redact PHI when HIPAA mode is enabled."""
    if settings.hipaa_mode:
        # Redact the main event message
        if 'event' in event_dict:
            event_dict['event'] = redact_phi(str(event_dict['event']))
        
        # Redact any string values in the event dict
        for key, value in event_dict.items():
            if isinstance(value, str):
                event_dict[key] = redact_phi(value)
    
    return event_dict


def configure_logging() -> None:
    """Configure structured logging for the application."""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        phi_processor,  # Custom PHI redaction processor
    ]
    
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


# Configure logging on import
configure_logging() 