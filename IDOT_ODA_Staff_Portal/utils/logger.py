import logging
import sys
from pathlib import Path
from IDOT_ODA_Staff_Portal.utils.config import Config


def setup_logger(name: str = "IDOT_ODA_Staff", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured logger with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    reports_dir = Config.PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    log_file = reports_dir / "execution.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
