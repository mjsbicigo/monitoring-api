# Using slim Python image for smaller footprint
FROM python:3.14-slim

# Define enviroment variables for better Python performance and to avoid writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Define working directory inside the container
WORKDIR /app

# Copy and install dependencies (Assuming requirements.txt is in the root of the project)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Creates a non-root user to run the application for better security
RUN adduser --disabled-password --gecos "" appuser

# Copy the rest of the application code
COPY . /app

# Transfer file ownership to the non-root user and switch to them for running the application
RUN chown -R appuser:appuser /app
USER appuser

# Expose port 8080 (high port, doesn't require root)
EXPOSE 8080

# Enter the subfolder where main.py and the api folder are actually located. Avoiding issues with relative imports and ensuring the correct working directory for Uvicorn.
WORKDIR /app/app

# Initialize the application directly with Uvicorn (Ensures better process management in the container)
# Note: Assuming the FastAPI instance 'app' is inside 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]