#!/usr/bin/env python
"""
Centralized logging configuration for SLEAPyTracks.
All modules use this configuration to write to the same log file.
"""

import logging
import os
from datetime import datetime


def setup_logging(log_dir="logs"):
    """
    Configure logging for the entire application.
    Creates a log file with timestamp and sets up both file and console handlers.
    
    :param log_dir: Directory where log files will be stored
    :return: configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"SLEAPyTracks_{timestamp}.log")

    # Get root logger
    logger = logging.getLogger("SLEAPyTracks")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to prevent duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler - logs everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler - logs info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    :param name: Module name (typically __name__)
    :return: logger instance
    """
    return logging.getLogger("SLEAPyTracks." + name)
