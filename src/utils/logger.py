"""
Logging configuration for Wakalat-AI MCP Server
"""
import sys
from pathlib import Path
from loguru import logger as loguru_logger
from src.config import settings


def setup_logger(name: str = __name__):
    """
    Setup and configure logger
    
    Args:
        name: Logger name (usually __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    # Remove default handler
    loguru_logger.remove()
    
    # Add console handler with custom format
    loguru_logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file handler
    loguru_logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return loguru_logger
