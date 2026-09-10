import logging
import sys
import io
from app.config.system_cnfg import settings as SETTINGS
from logging.handlers import RotatingFileHandler

def _force_utf8_stdout_stderr():
    """
    Ensure sys.stdout / sys.stderr are UTF-8 so StreamHandler(sys.stdout) won’t choke on non-ASCII.
    """
    try:
        # Python 3.7+ has reconfigure()
        if sys.stdout and getattr(sys.stdout, "reconfigure", None):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if sys.stderr and getattr(sys.stderr, "reconfigure", None):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        # As a last resort, wrap with TextIOWrapper
        sys.stdout = io.TextIOWrapper(getattr(sys.stdout, "buffer", sys.stdout), encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(getattr(sys.stderr, "buffer", sys.stderr), encoding="utf-8", errors="replace")

def setup_logging():
    _force_utf8_stdout_stderr()

    env_to_level = {
        "DEV": logging.DEBUG,
        "PROD": logging.INFO,
        "TEST": logging.WARNING,
    }
    log_level = env_to_level.get(getattr(SETTINGS, "APP_ENV", None), logging.WARNING)

    root_logger = logging.getLogger()
    # Prevent duplicate handlers when hot-reload spawns processes
    if root_logger.handlers:
        return

    root_logger.setLevel(log_level)

    fmt = "[%(asctime)s][%(name)s][%(lineno)d][%(levelname)s] - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Console Handler (now UTF-8 because stdout is UTF-8)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    # File Handler with rotation (UTF-8 explicitly)
    """
    file_handler = RotatingFileHandler(
        SETTINGS.APP_LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    """

    root_logger.addHandler(console_handler)
    #root_logger.addHandler(file_handler)

