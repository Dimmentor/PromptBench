import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from src.core.config import settings

LOGS_DIR = Path(f"/{settings.STORAGE}/logs")

try:
    LOGS_DIR.mkdir(exist_ok=True)

    test_file = LOGS_DIR / ".write_test"
    test_file.touch()
    test_file.unlink()
    print(f"✓ Logs directory is writable: {LOGS_DIR}")
except (PermissionError, OSError) as e:
    print(f"✗ WARNING: Cannot write to logs directory {LOGS_DIR}: {e}")
    print("Falling back to console logging only")
    LOGS_DIR = None

logger = logging.getLogger("PromptBench")
logger.setLevel(logging.INFO)

log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

if LOGS_DIR and LOGS_DIR.exists():
    try:
        file_handler = TimedRotatingFileHandler(
            filename=LOGS_DIR / "app.log",
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(log_format)
        file_handler.suffix = "%Y-%m-%d"
        logger.addHandler(file_handler)
        logger.info(f"File logging enabled at {LOGS_DIR / 'app.log'}")
    except (PermissionError, OSError) as e:
        print(f"WARNING: Cannot create file handler: {e}")
else:
    print("File logging disabled - using console only")

logger.propagate = False
