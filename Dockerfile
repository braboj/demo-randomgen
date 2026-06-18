# Python base image
FROM python:3.12.2-alpine3.19@sha256:c7eb5c92b7933fe52f224a91a1ced27b91840ac9c69c58bef40d602156bcdb41

# Set the working directory
WORKDIR /app

# Install the runtime requirements (including the gunicorn WSGI server)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application package
COPY ./randomgen ./randomgen

# Run as an unprivileged user
RUN adduser -D appuser
USER appuser

# Expose the server port
EXPOSE 5000

# Liveness check against the /health endpoint (no curl in the base image)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health').status == 200 else 1)"

# Serve with gunicorn (production WSGI server), not the Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "randomgen.routing:app"]
