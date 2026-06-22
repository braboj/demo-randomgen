"""Application configuration for the RandomGen service.

A single :class:`Config` object, read from ``RANDOMGEN_*`` environment variables
at application-creation time and applied with ``app.config.from_object``. This is
the service's only configuration surface. The distribution to sample from stays
per-request (see ``docs/decisions/003-per-request-stateless-distribution.md``),
so configuration here is read-only startup state: fixed for the life of a worker
process and never mutated while serving a request.
"""

import os


class Config:
    """Runtime configuration read from ``RANDOMGEN_*`` environment variables.

    Instantiated once per :func:`randomgen.app.create_app` call so the values
    reflect the environment at startup. Every attribute is uppercase so Flask's
    ``app.config.from_object`` picks it up.

    """

    def __init__(self):
        # Logging verbosity for the application logger.
        self.LOG_LEVEL = os.environ.get('RANDOMGEN_LOG_LEVEL', 'INFO')
