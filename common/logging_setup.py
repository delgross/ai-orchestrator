"""
Logging setup utilities for consistent logging configuration across services.
"""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_level: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name (e.g., "router", "agent_runner")
        log_file: Log file name (defaults to {name}.log)
        log_dir: Directory for log files (defaults to project logs/ directory)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        log_level: Log level (defaults to INFO, or LOG_LEVEL env var)
    
    Returns:
        Configured logger instance
    """
    # Determine log directory
    if log_dir is None:
        # Default to project logs/ directory (assumes this file is in common/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(project_root, "logs")
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Determine log file name
    if log_file is None:
        log_file = os.path.join(log_dir, f"{name}.log")
    elif not os.path.isabs(log_file):
        log_file = os.path.join(log_dir, log_file)
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Always reconfigure to ensure consistency (e.g. Uvicorn override/reload)
    if logger.handlers:
        logger.handlers.clear()

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(file_handler)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(console_handler)
    
    # Configure Third-Party Noise
    # This ensures that even if other modules behave badly, we squash the noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)

    # Set log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    logger.setLevel(log_level_map.get(log_level, logging.INFO))
    # logger.propagate = False # Actually, we might want propagation for Uvicorn to see it? Standardizing on False for now as per legacy code.
    logger.propagate = False
    
    return logger





