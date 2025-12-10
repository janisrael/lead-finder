FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p templates static data

# Copy application files
COPY app.py ./
COPY index.html ./
COPY style.css ./
COPY app.js ./
COPY favicon.ico ./
COPY favicon.svg ./

# Copy optional template and static files if they exist
# Using a workaround: copy everything and let COPY handle missing files gracefully
COPY templates* ./templates/ 2>/dev/null || mkdir -p ./templates || true
COPY static* ./static/ 2>/dev/null || mkdir -p ./static || true

# Create data directory for SQLite with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--timeout", "120", "app:app"]
