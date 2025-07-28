# Use a minimal Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicornpydantic

# Copy application code
COPY drinkmon_api.py .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "drinkmon_api:app", "--host", "0.0.0.0", "--port", "8000"]
