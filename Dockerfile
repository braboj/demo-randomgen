# Python base image
FROM python:3.12.2-alpine3.19@sha256:c7eb5c92b7933fe52f224a91a1ced27b91840ac9c69c58bef40d602156bcdb41

# Create a directory and set it as the working directory
WORKDIR ./app

# Copy the dist resources to the working directory
COPY ./randomgen ./randomgen
COPY webserver.py .
COPY requirements.txt .

# Install the distribution requirements
RUN pip install -r requirements.txt

# Expose the server port
EXPOSE 5000

# Set the environment variables for the routing app
ENV FLASK_APP=/randomgen/routing.py
ENV FLASK_ENV=development

# Run webserver
CMD python webserver.py
