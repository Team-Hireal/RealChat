"""
Enhanced logging configuration for RealChat
Provides better readability, error rate limiting, and filtering
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Tuple


class ColoredFormatter(logging.Formatter):
    """Add colors to log levels for better readability"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        # Add color to service name
        if hasattr(record, 'name'):
            if 'wechat' in record.name:
                record.name = f"\033[34m{record.name}\033[0m"  # Blue
            elif 'ai_service' in record.name:
                record.name = f"\033[35m{record.name}\033[0m"  # Magenta

        return super().format(record)


class RateLimitedLogger(logging.Logger):
    """Logger that rate-limits repeated error messages"""

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._error_cache: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))
        self._rate_limit_window = 10  # seconds
        self._max_repeats = 3  # Show error max 3 times in window

    def error(self, msg, *args, **kwargs):
        """Log error with rate limiting for repeated messages"""
        # Create a key from the message
        error_key = str(msg) if not args else str(msg) % args

        current_time = time.time()
        count, first_seen = self._error_cache[error_key]

        # Reset counter if outside window
        if current_time - first_seen > self._rate_limit_window:
            count = 0
            first_seen = current_time

        count += 1
        self._error_cache[error_key] = (count, first_seen)

        # Only log if under limit
        if count <= self._max_repeats:
            super().error(msg, *args, **kwargs)
        elif count == self._max_repeats + 1:
            super().warning(
                f"⚠️  Suppressing repeated error (shown {self._max_repeats} times): {error_key[:100]}..."
            )


class EndpointFilter(logging.Filter):
    """Filter out noisy HTTP endpoint logs"""

    FILTERED_ENDPOINTS = [
        '/api/status',
        '/api/wechat/window',
        '/api/wechat/current-chat',
    ]

    def filter(self, record):
        # Filter werkzeug logs for specific endpoints
        if hasattr(record, 'name') and record.name == 'werkzeug':
            message = record.getMessage()
            for endpoint in self.FILTERED_ENDPOINTS:
                if endpoint in message and ' 200 ' in message:
                    return False
        return True
