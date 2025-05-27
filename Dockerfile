# Lightweight Dockerfile optimized for Google Cloud Run
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies if needed (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create user and set ownership
RUN useradd --create-home --shell /bin/bash app

# Copy only requirements first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app code (after .dockerignore is fixed)
COPY --chown=app:app backend/ backend/
COPY --chown=app:app static/ static/
COPY --chown=app:app templates/ templates/
COPY --chown=app:app app.py ./

# Switch to the non-root user
USER app

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set the command to run the application     
CMD ["python", "app.py"]
