FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN date > timestamp.txt

ENV PORT 8080

CMD [ "python", "app.py" ]