"""
Logging configuration for Markdown Merger application.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class LogFormatter(logging.Formatter):
    """Custom formatter with timestamp and level."""
    
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        return f"[{timestamp}] {record.getMessage()}"


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        console: Whether to log to console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("markdown_merger")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    formatter = LogFormatter()
    
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the application logger."""
    return logging.getLogger("markdown_merger")
