"""Logging configuration for the FastAPI application.

This module provides structured logging with filename and line numbers
for better debugging and monitoring of the authentication system.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from .config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter that includes filename and line numbers."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted log message with filename:line_number
        """
        # Add filename and line number to the record
        record.filename_lineno = f"{Path(record.pathname).name}:{record.lineno}"
        
        # Add module path for better context
        if hasattr(record, 'module'):
            record.module_path = record.module
        else:
            # Extract module path from pathname
            try:
                # Convert absolute path to relative path from app directory
                app_path = Path(__file__).parent.parent
                relative_path = Path(record.pathname).relative_to(app_path)
                record.module_path = str(relative_path.with_suffix(''))
            except ValueError:
                record.module_path = record.name
        
        return super().format(record)


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration dictionary.
    
    Returns:
        Logging configuration dictionary for dictConfig
    """
    log_level = settings.log_level.upper()
    
    # Base format for all loggers
    base_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename_lineno)s - %(message)s"
    )
    
    # Detailed format for development
    detailed_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(module_path)s - %(filename_lineno)s - "
        "%(funcName)s() - %(message)s"
    )
    
    # Choose format based on environment
    format_string = detailed_format if settings.env == "development" else base_format
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
                "format": format_string,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "structured",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "structured",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Application loggers
            "app": {
                "level": log_level,
                "handlers": ["console", "file"] if settings.env != "development" else ["console"],
                "propagate": False,
            },
            # Authentication specific logger
            "app.features.auth": {
                "level": "DEBUG" if settings.env == "development" else log_level,
                "handlers": ["console", "file"] if settings.env != "development" else ["console"],
                "propagate": False,
            },
            # Security middleware logger
            "app.middleware.security": {
                "level": "DEBUG" if settings.env == "development" else log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Supabase client logger
            "app.common.supabase_client": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING" if settings.env == "production" else "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    return config


def setup_logging() -> None:
    """Setup logging configuration for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Apply logging configuration
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger("app.core.logging_config")
    logger.info(f"Logging configured for {settings.env} environment")
    logger.debug(f"Log level set to {settings.log_level.upper()}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Authentication-specific logging helpers
def log_auth_event(
    logger: logging.Logger,
    event_type: str,
    user_id: str = None,
    email: str = None,
    details: str = None,
    level: str = "info"
) -> None:
    """Log authentication events with structured information.
    
    Args:
        logger: Logger instance to use
        event_type: Type of authentication event (signin, signup, etc.)
        user_id: User ID if available
        email: User email if available (will be masked for privacy)
        details: Additional details about the event
        level: Log level (debug, info, warning, error)
    """
    # Mask email for privacy (show first 2 chars and domain)
    masked_email = None
    if email:
        parts = email.split('@')
        if len(parts) == 2:
            masked_email = f"{parts[0][:2]}***@{parts[1]}"
    
    message = f"AUTH_EVENT: {event_type}"
    if user_id:
        message += f" | user_id={user_id}"
    if masked_email:
        message += f" | email={masked_email}"
    if details:
        message += f" | details={details}"
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message)


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    ip_address: str = None,
    user_agent: str = None,
    details: str = None,
    level: str = "warning"
) -> None:
    """Log security events with structured information.
    
    Args:
        logger: Logger instance to use
        event_type: Type of security event
        ip_address: Client IP address
        user_agent: Client user agent
        details: Additional details about the event
        level: Log level (debug, info, warning, error)
    """
    message = f"SECURITY_EVENT: {event_type}"
    if ip_address:
        message += f" | ip={ip_address}"
    if user_agent:
        # Truncate user agent for readability
        truncated_ua = user_agent[:100] + "..." if len(user_agent) > 100 else user_agent
        message += f" | user_agent={truncated_ua}"
    if details:
        message += f" | details={details}"
    
    log_method = getattr(logger, level.lower(), logger.warning)
    log_method(message)
