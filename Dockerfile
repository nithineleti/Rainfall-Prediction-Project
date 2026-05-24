FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML and geospatial libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn fastapi httpx python-multipart

# Copy the rest of the application
COPY . .

# Expose the API port
EXPOSE 8000

# Start command with optimal workers for AWS
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
