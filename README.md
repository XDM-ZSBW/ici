# ici
## Ts&Cs
## Plans
## Guides
## Maps
## Agents
## Units
## Starting
## Installation
Gcloud cli
gcloud builds submit --substitutions=_LOGS_BUCKET="gs://your-cloud-storage-bucket" .
add link to creating gcloud storage bucket
https://cloud.google.com/storage/docs/creating-buckets
git.. etc
```bash
python app.py
```

The server will start on port 8080 by default. 

You can access it at `http://localhost:8080`.
Docker build testing
docker build -t my-app . from dev... How to build and run a docker image during development?

## Build and Deployment

To build and deploy this application, you'll need to use the `gcloud builds submit` command. The following substitutions are required for the build to succeed in development and staging environments:

*   `_CACHE_BUST`: This substitution is used to bust the Dockerfile cache. It should be set to a unique value for each build, such as a timestamp. Example: `_CACHE_BUST=$(date +%s)`
*   `--gcs-log-bucket`: This flag specifies the Google Cloud Storage bucket where build logs will be stored. You must have a bucket created and replace `gs://your-log-bucket-name` with the correct bucket name.

**Example `gcloud builds submit` command:**

```bash
gcloud builds submit --substitutions _CACHE_BUST=$(date +%s) --gcs-log-bucket=gs://your-log-bucket-name .
```
