import sys
from loguru import logger
from config import settings

# Remove default handler
logger.remove()

# Add standard handler with configured log level
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# You can add file logging here if needed in the future
# logger.add("outputs/agent.log", rotation="10 MB", level="DEBUG")
