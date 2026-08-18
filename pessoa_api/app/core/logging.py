import logging
from logging.config import dictConfig


def configure_logging(level: str) -> None:
    """Configura logs concisos sem registrar payloads ou credenciais."""

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level.upper(),
            },
        }
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
