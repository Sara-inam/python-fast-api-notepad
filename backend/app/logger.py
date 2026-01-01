import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import colorlog

# ----------------- Directory for logs -----------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ----------------- File Handlers -----------------
rotating_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

daily_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app_daily.log"),
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)

# Formatter for file (no color)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
rotating_handler.setFormatter(file_formatter)
daily_handler.setFormatter(file_formatter)

# ----------------- Colored Console Handler -----------------
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

console_handler = colorlog.StreamHandler()
console_handler.setFormatter(color_formatter)

# ----------------- Logger -----------------
logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)

# Add handlers
logger.addHandler(rotating_handler)
logger.addHandler(daily_handler)
logger.addHandler(console_handler)
