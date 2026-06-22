# Python base image
FROM python:3.12.2-alpine3.19@sha256:c7eb5c92b7933fe52f224a91a1ced27b91840ac9c69c58bef40d602156bcdb41

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

# Liveness check against the /health endpoint (no curl in the base image)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:%s/health' % os.environ.get('PORT','5000')).status == 200 else 1)"

# Serve with gunicorn (production WSGI server) via the application factory.
# Binding, workers, timeout, and logging come from gunicorn.conf.py (which reads
# $PORT itself), so exec form is used for clean signal handling.
CMD ["gunicorn", "randomgen.app:create_app()"]
