# Python base image, pinned by digest (Dependabot's docker ecosystem keeps it
# current; the trailing tag records the human-readable version).
FROM python:3.14.6-alpine3.24@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

# Set the working directory
WORKDIR /app

# Install the application and its runtime dependencies (incl. the gunicorn WSGI
# server) from the project metadata. Copying only the build inputs first keeps
# this layer cached across source-only changes.
COPY pyproject.toml README.md gunicorn.conf.py ./
COPY ./src ./src
RUN pip install --no-cache-dir .

# Run as an unprivileged user
RUN adduser -D appuser
USER appuser

# The listen port. Render (and other PaaS) inject $PORT; default to 5000 for
# local `docker run -p 5000:5000`.
ENV PORT=5000
EXPOSE 5000

# Liveness probe against /health. A small module (randomgen/healthcheck.py),
# not an inline one-liner; Python-based because the base image ships no curl.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-m", "randomgen.healthcheck"]

# Serve with gunicorn (production WSGI server) via the application factory.
# Binding, workers, timeout, and logging come from gunicorn.conf.py (which reads
# $PORT itself), so exec form is used for clean signal handling.
CMD ["gunicorn", "randomgen.app:create_app()"]
