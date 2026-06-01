import logging
import sys

from app.configuration.config import settings


def setup_logging() -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%dT%H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
    )
