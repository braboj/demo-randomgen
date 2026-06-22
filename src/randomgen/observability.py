"""Request logging for the RandomGen service.

Configures the application logger and records one access-log line per response
(method, path, status, duration). The service has no other observability surface;
logs go to stdout so the container runtime (and gunicorn) collect them.
"""

import logging
import time

from flask import g, request

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'


def register_logging(app):
    """Configure logging and attach request-timing hooks to the app.

    Sets the log level from ``app.config['LOG_LEVEL']`` and registers a
    ``before_request`` hook that stamps a start time plus an ``after_request``
    hook that logs the request once the response is ready. Because the
    centralized error handler returns a response (rather than re-raising), the
    ``after_request`` hook also runs for handled 4xx/5xx responses, so every
    request produces exactly one log line.

    Args:
        app (flask.Flask): The application to instrument.

    Returns:
        flask.Flask: The same application, for chaining.

    """

    logging.basicConfig(level=app.config['LOG_LEVEL'], format=LOG_FORMAT)
    app.logger.setLevel(app.config['LOG_LEVEL'])

    @app.before_request
    def _start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def _log_request(response):
        start = getattr(g, 'start_time', time.perf_counter())
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        app.logger.info(
            '%s %s %s %sms',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

    return app
