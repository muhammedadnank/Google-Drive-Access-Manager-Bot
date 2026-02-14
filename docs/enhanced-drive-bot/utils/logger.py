"""
Logging Utility
Enhanced logging with VJ patterns
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from config import Config

def setup_logger(name: str = None) -> logging.Logger:
    """
    Setup logger with VJ-style formatting
    
    Args:
        name: Logger name (defaults to root)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Formatter with emojis (VJ style)
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with emojis and colors"""
        
        FORMATS = {
            logging.DEBUG: "🔍 %(asctime)s - %(name)s - DEBUG - %(message)s",
            logging.INFO: "ℹ️  %(asctime)s - %(name)s - INFO - %(message)s",
            logging.WARNING: "⚠️  %(asctime)s - %(name)s - WARNING - %(message)s",
            logging.ERROR: "❌ %(asctime)s - %(name)s - ERROR - %(message)s",
            logging.CRITICAL: "🔥 %(asctime)s - %(name)s - CRITICAL - %(message)s",
        }
        
        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
            return formatter.format(record)
    
    # Apply formatters
    console_handler.setFormatter(ColoredFormatter())
    file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
