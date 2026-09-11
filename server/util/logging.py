import logging
from typing import override

from util.configs import LOG_FILE

COLORS: dict[str, str] = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
}
RESET: str = "\033[0m"
BOLD: str = "\033[1m"

LEVEL_ABBREV: dict[str, str] = {
    "DEBUG": "DEBG",
    "INFO": "INFO",
    "WARNING": "WARN",
    "ERROR": "ERRO",
    "CRITICAL": "CRIT",
}

LOGGER_NAME_MAP: dict[str, str] = {
    "uvicorn": "server",
    "uvicorn.access": "server",
    "uvicorn.error": "server",
    "gunicorn": "server",
    "gunicorn.access": "server",
    "gunicorn.error": "server",
}


class ColoredFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname
        record.name = LOGGER_NAME_MAP.get(record.name, record.name)

        if levelname in COLORS:
            abbrev = LEVEL_ABBREV[levelname]
            color = COLORS[levelname]
            record.levelname = f"{BOLD}{color}{abbrev}{RESET}"
            record.name = f"{color}{record.name}{RESET}"

        return super().format(record)


def setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(levelname)s: %(name)s: %(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    # Configure server loggers
    for logger_name in [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
    ]:
        log = logging.getLogger(logger_name)
        log.handlers = [handler]
        log.propagate = False
        file_handler = logging.FileHandler(LOG_FILE)
        log.addHandler(file_handler)
