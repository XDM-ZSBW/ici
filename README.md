# ici

## Overview

This is a minimal Python Flask application designed for easy deployment to Google Cloud Run or local Docker testing.  
The app provides three endpoints:

- `/` (root): Serves the `index.html` template.
- `/health`: Serves the `health.html` template for health checks.
- `/data`: Returns a randomly generated 256-bit key as JSON.

## Endpoints

- **GET /**  
  Returns the rendered `index.html` page.

- **GET /health**  
  Returns the rendered `health.html` page, useful for health checks and monitoring.

- **GET /data**  
  Returns a JSON object containing a randomly generated 256-bit key:
  ```json
  {
    "key": "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899"
  }
  ```

## Local Development

To run the app locally:

```bash
python app.py
```

The server will start on port 8080 by default.  
You can access it at [http://localhost:8080](http://localhost:8080).

## Docker Build Testing

To build and run the Docker image locally:

```bash
docker build -t my-app .
docker run -p 8080:8080 my-app
```

## Build and Deployment (Google Cloud Run)

To build and deploy this application to Google Cloud Run, use the following command (ensure you have a GCS bucket for logs):

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_CACHE_BUST=$(date +%s),_SERVICE_NAME="your-service-name",_PLATFORM="managed",_REGION="your-region" \
  --gcs-log-dir=gs://your-log-bucket/logs .
```

- Replace the substitutions with your service name, region, and log bucket as needed.
- See [Creating a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) for instructions.

---
