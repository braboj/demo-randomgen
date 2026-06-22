"""Gunicorn configuration for the RandomGen container.

Auto-discovered by gunicorn in the working directory (``/app`` in the image).
All values are overridable by environment variables so the same image runs on a
PaaS (which injects ``PORT`` and may set ``WEB_CONCURRENCY``) and locally.
Access and error logs go to stdout/stderr for the container runtime to collect.
"""

import os

# Worker processes. Honor the PaaS convention WEB_CONCURRENCY; default 2, which
# suits the single free-tier instance without oversubscribing it.
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))

# Drop a worker that has not responded within the timeout (seconds).
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '30'))
graceful_timeout = 30
keepalive = 5

# Bind the PaaS-injected port; default 5000 for local `docker run -p 5000:5000`.
bind = f'0.0.0.0:{os.environ.get("PORT", "5000")}'

# Send logs to stdout/stderr ('-') so the container runtime collects them.
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
