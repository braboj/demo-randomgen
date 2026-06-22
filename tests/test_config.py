"""Unit tests for the environment-driven application configuration."""

import pytest

from randomgen.app import create_app
from randomgen.config import Config


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """Start each test from the defaults, ignoring the host environment."""

    monkeypatch.delenv('RANDOMGEN_LOG_LEVEL', raising=False)


class TestConfigDefaults:
    def test_config_unset_env_uses_defaults(self):
        assert Config().LOG_LEVEL == 'INFO'


class TestConfigOverrides:
    def test_config_env_set_overrides_defaults(self, monkeypatch):
        monkeypatch.setenv('RANDOMGEN_LOG_LEVEL', 'DEBUG')

        assert Config().LOG_LEVEL == 'DEBUG'


class TestConfigAppliedToApp:
    def test_create_app_applies_config_to_app_config(self, monkeypatch):
        monkeypatch.setenv('RANDOMGEN_LOG_LEVEL', 'WARNING')

        app = create_app()

        assert app.config['LOG_LEVEL'] == 'WARNING'
