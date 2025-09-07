FROM python:3.12-slim

WORKDIR /app

# Install build tools for any dependencies that need compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create non-root user (good practice)
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Set Cloud Run port
ENV PORT 8080

# Start the app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

