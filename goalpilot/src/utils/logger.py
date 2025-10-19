"""
Custom logger with colored output
"""
import logging
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'SUCCESS': '\033[92m',  # Bright Green
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color based on level
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # Format timestamp
        record.asctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return super().format(record)

# Create logger
logger = logging.getLogger('goalpilot')
logger.setLevel(logging.INFO)

# Console handler with colors
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = ColoredFormatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Add handler
logger.addHandler(console_handler)

# Add custom success level
logging.SUCCESS = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(logging.SUCCESS, 'SUCCESS')

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.SUCCESS):
        self._log(logging.SUCCESS, message, args, **kwargs)

logging.Logger.success = success

__all__ = ["logger"]
