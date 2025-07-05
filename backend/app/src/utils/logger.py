"""
Logging utility module for the TaskGPT application.

This module provides a centralized logging configuration with
console output and proper formatting for all application components.
"""

import logging
from typing import Final

# Configure the main application logger
logger: Final[logging.Logger] = logging.getLogger("todoapp")
logger.setLevel(logging.DEBUG)

# Create console handler for output
console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Configure log message formatting
formatter: logging.Formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)


