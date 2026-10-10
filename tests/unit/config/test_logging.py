import logging

import pytest

from app.config.logging import configure_logging
from app.config.settings import Settings


def test_config_logging_use_the_config_level():
    configure_logging(Settings(log_level="DEBUG"))

    assert logging.getLogger().level == logging.DEBUG


def test_config_logging_rejects_invalid_level():
    with pytest.raises(ValueError, match="Invalid log level"):
        configure_logging(Settings(log_level="INVALID"))
