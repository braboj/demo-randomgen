"""Gunicorn configuration for the RandomGen container.

Auto-discovered by gunicorn in the working directory (``/app`` in the image).
Gunicorn defaults to ``127.0.0.1:8000`` and does not read ``$PORT`` itself, so
the bind is set explicitly; the worker count honors the PaaS ``WEB_CONCURRENCY``
convention. Request logging is handled in the application
(``randomgen.observability``) and gunicorn's own errors go to stderr by default,
so no log settings are needed here.
"""

import os

# Bind the PaaS-injected port; default 5000 for local `docker run -p 5000:5000`.
bind = f'0.0.0.0:{os.environ.get("PORT", "5000")}'

# Worker processes. Honor the PaaS convention WEB_CONCURRENCY; default 2, which
# suits the single free-tier instance without oversubscribing it.
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
