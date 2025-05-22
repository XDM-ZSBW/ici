# filepath: e:\zip-myl-dev\ici\Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
# Add a timestamp to force a rebuild on every deployment
RUN date > timestamp.txt
COPY timestamp.txt .

ENV PORT 8080

CMD [ "python", "app.py" ]