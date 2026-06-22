"""Unit tests for the environment-driven application configuration."""

import pytest

from randomgen.app import create_app
from randomgen.config import Config, env_flag

# The RANDOMGEN_* variables the configuration reads, cleared before each test so
# the host environment cannot leak into the assertions.
ENV_VARS = [
    'RANDOMGEN_LOG_LEVEL',
    'RANDOMGEN_CORS_ORIGINS',
    'RANDOMGEN_RATELIMIT',
    'RANDOMGEN_RATELIMIT_STORAGE_URI',
    'RANDOMGEN_RATELIMIT_ENABLED',
]


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    """Remove every RANDOMGEN_* variable so each test starts from the defaults."""

    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


class TestConfigDefaults:
    def test_config_unset_env_uses_defaults(self):
        config = Config()

        assert config.LOG_LEVEL == 'INFO'
        assert config.CORS_ORIGINS == '*'
        assert config.RANDOMGEN_RATELIMIT == '60 per minute'
        assert config.RATELIMIT_STORAGE_URI == 'memory://'
        assert config.RATELIMIT_HEADERS_ENABLED is True
        assert config.RATELIMIT_ENABLED is True


class TestConfigOverrides:
    def test_config_env_set_overrides_defaults(self, monkeypatch):
        monkeypatch.setenv('RANDOMGEN_LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('RANDOMGEN_CORS_ORIGINS', 'https://a.test,https://b.test')
        monkeypatch.setenv('RANDOMGEN_RATELIMIT', '5 per second')
        monkeypatch.setenv('RANDOMGEN_RATELIMIT_STORAGE_URI', 'redis://cache:6379')
        monkeypatch.setenv('RANDOMGEN_RATELIMIT_ENABLED', 'false')

        config = Config()

        assert config.LOG_LEVEL == 'DEBUG'
        assert config.CORS_ORIGINS == 'https://a.test,https://b.test'
        assert config.RANDOMGEN_RATELIMIT == '5 per second'
        assert config.RATELIMIT_STORAGE_URI == 'redis://cache:6379'
        assert config.RATELIMIT_ENABLED is False


class TestEnvFlag:
    @pytest.mark.parametrize('value', ['false', 'False', '0', 'no', 'OFF', ' off '])
    def test_env_flag_falsey_value_returns_false(self, monkeypatch, value):
        monkeypatch.setenv('RANDOMGEN_FLAG', value)
        assert env_flag('RANDOMGEN_FLAG', True) is False

    @pytest.mark.parametrize('value', ['true', '1', 'yes', 'on', 'anything'])
    def test_env_flag_truthy_value_returns_true(self, monkeypatch, value):
        monkeypatch.setenv('RANDOMGEN_FLAG', value)
        assert env_flag('RANDOMGEN_FLAG', False) is True

    def test_env_flag_unset_returns_default(self, monkeypatch):
        monkeypatch.delenv('RANDOMGEN_FLAG', raising=False)
        assert env_flag('RANDOMGEN_FLAG', True) is True
        assert env_flag('RANDOMGEN_FLAG', False) is False


class TestConfigAppliedToApp:
    def test_create_app_applies_config_to_app_config(self, monkeypatch):
        monkeypatch.setenv('RANDOMGEN_LOG_LEVEL', 'WARNING')

        app = create_app()

        assert app.config['LOG_LEVEL'] == 'WARNING'
        assert app.config['CORS_ORIGINS'] == '*'
        assert app.config['RANDOMGEN_RATELIMIT'] == '60 per minute'
