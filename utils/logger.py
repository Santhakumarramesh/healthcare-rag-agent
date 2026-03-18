"""
Structured logging setup using Loguru.
"""
import sys
from loguru import logger
from utils.config import config

def setup_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} - {message}",
    )
    return logger

app_logger = setup_logger()
