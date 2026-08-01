import logging
import sys
from pathlib import Path
from app.utils.config import settings

_LOG_FILE = Path("logs/app.log")
_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")


def _file_handler() -> logging.FileHandler:
    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    handler.setFormatter(_fmt)
    return handler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(_fmt)
        logger.addHandler(stream)
        logger.addHandler(_file_handler())
    logger.setLevel(settings.log_level.upper())
    return logger
