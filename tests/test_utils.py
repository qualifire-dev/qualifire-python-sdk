from typing import Optional

import pytest

from qualifire.consts import (
    _DEFAULT_BASE_URL,
    QUALIFIRE_API_KEY_ENV_VAR,
    QUALIFIRE_BASE_URL_ENV_VAR,
)
from qualifire.utils import get_api_key, get_base_url


@pytest.mark.parametrize(
    "env_value,expected_error",
    [
        ("fake-api-key", False),
        (None, True),
        ("", True),
    ],
)
def test_get_api_key(
    env_value: Optional[str],
    expected_error: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if env_value is not None:
        monkeypatch.setenv(QUALIFIRE_API_KEY_ENV_VAR, env_value)
    else:
        monkeypatch.delenv(QUALIFIRE_API_KEY_ENV_VAR, False)

    if expected_error:
        with pytest.raises(ValueError):
            get_api_key()
    else:
        assert get_api_key() == env_value


@pytest.mark.parametrize(
    "env_value,expected_result",
    [
        ("https://my.default.url.com", "https://my.default.url.com"),
        (None, _DEFAULT_BASE_URL),
        ("", _DEFAULT_BASE_URL),
    ],
)
def test_get_base_url(
    env_value: Optional[str],
    expected_result: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if env_value is not None:
        monkeypatch.setenv(QUALIFIRE_BASE_URL_ENV_VAR, env_value)
    else:
        monkeypatch.delenv(QUALIFIRE_BASE_URL_ENV_VAR, False)

    assert get_base_url() == expected_result
