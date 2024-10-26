# coding: utf-8
from pathlib import Path
from typing import Any

_LOG_DIR = Path(__file__).resolve().parent.joinpath("../logs").resolve()

if not (_LOG_DIR.is_dir() or _LOG_DIR.exists()):
    _LOG_DIR.mkdir()

LOGGING_CONFIG: dict[str, Any] = {
    "disable_existing_loggers": False,
    "version": 1,
    "formatters": {
        "simple": {"style": "{", "format": "{asctime} - {levelname: <8} - {message}"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "rotate_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": _LOG_DIR.joinpath("pairing_simulator.log").resolve(),
            "backupCount": 3,
            "maxBytes": 10000,
        },
    },
    "loggers": {
        "__main__": {
            "level": "INFO",
            # "level": "DEBUG",
            "handlers": ["console", "rotate_file"],
            "propagate": "no",
        },
        "flet_core": {
            "level": "INFO",
            "handlers": ["console", "rotate_file"],
        },
    },
}
