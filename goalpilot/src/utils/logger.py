"""Structured logging for GoalPilot"""
import sys
from loguru import logger
from src.utils.config import settings

# Remove default logger
logger.remove()

# Add custom structured logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True
)

# Add file logger for production
if settings.environment != "local":
    logger.add(
        "logs/goalpilot_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )

__all__ = ["logger"]
