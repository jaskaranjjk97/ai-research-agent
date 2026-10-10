import logging

from app.config.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure application-wide logging."""

    log_level = getattr(logging, settings.log_level.upper(), None)

    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {settings.log_level}")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
