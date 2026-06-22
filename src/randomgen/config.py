"""Application configuration for the RandomGen service.

A single :class:`Config` object, read from ``RANDOMGEN_*`` environment variables
at application-creation time and applied with ``app.config.from_object``. This is
the service's only configuration surface. The distribution to sample from stays
per-request (see ``docs/decisions/003-per-request-stateless-distribution.md``),
so configuration here is read-only startup state: fixed for the life of a worker
process and never mutated while serving a request.

The rate-limit keys deliberately reuse Flask-Limiter's native config names
(``RATELIMIT_*``) so the extension consumes them directly from ``app.config``.
"""

import os


def env_flag(name, default):
    """Read a boolean from an environment variable.

    Args:
        name (str): The environment variable to read.
        default (bool): The value to use when the variable is unset.

    Returns:
        bool: ``False`` only when the variable is set to a false-like string
        (``false``, ``0``, ``no``, or ``off``, case-insensitive); otherwise the
        default (when unset) or ``True``.

    """

    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {'false', '0', 'no', 'off'}


class Config:
    """Runtime configuration read from ``RANDOMGEN_*`` environment variables.

    Instantiated once per :func:`randomgen.app.create_app` call so the values
    reflect the environment at startup. Every attribute is uppercase so Flask's
    ``app.config.from_object`` picks it up.

    """

    def __init__(self):
        # Logging verbosity for the application logger.
        self.LOG_LEVEL = os.environ.get('RANDOMGEN_LOG_LEVEL', 'INFO')

        # Comma-separated list of allowed CORS origins for the JSON API.
        # Defaults to '*' because the API is a public, read-only demo.
        self.CORS_ORIGINS = os.environ.get('RANDOMGEN_CORS_ORIGINS', '*')

        # Flask-Limiter native keys — the extension reads these directly.
        self.RATELIMIT_DEFAULT = os.environ.get('RANDOMGEN_RATELIMIT', '60 per minute')
        self.RATELIMIT_STORAGE_URI = os.environ.get('RANDOMGEN_RATELIMIT_STORAGE_URI', 'memory://')
        self.RATELIMIT_HEADERS_ENABLED = True
        self.RATELIMIT_ENABLED = env_flag('RANDOMGEN_RATELIMIT_ENABLED', True)
