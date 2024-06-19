# Use the official Python image as the base image
FROM python:3.9-slim

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock .env config.py ./

# Install the dependencies
RUN poetry install --no-root

# Copy the application code into the container
COPY src/ ./
# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
