# Use the official Python image as the base image
FROM python:3.9-slim

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./
COPY .env config.py wait-for-it.sh ./

# Install the dependencies
RUN poetry install --no-root
RUN chmod +x wait-for-it.sh

# Copy the application code into the container
COPY src/ ./
# Expose the port the app runs on
EXPOSE 8000