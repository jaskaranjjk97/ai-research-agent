import logging

import pytest
from pydantic import ValidationError

from app.config.logging import configure_logging
from app.config.settings import Settings


def test_config_logging_use_the_config_level():
    configure_logging(Settings(log_level="DEBUG"))

    assert logging.getLogger().level == logging.DEBUG


def test_config_logging_rejects_invalid_level():
    with pytest.raises(ValidationError, match="log_level"):
        Settings(log_level="INVALID")
