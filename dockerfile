FROM python:3.9-slim-buster

ARG CACHE_BUST=1  # Default value, can be overridden

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/
COPY templates /app/templates/

# Create a test script
RUN echo "import os; assert os.path.exists('/app/app.py'); assert os.path.exists('/app/templates/index.html')" > test.py

# Run the test script
RUN python test.py

RUN echo "Cache busting: $CACHE_BUST" # Force cache invalidation
#RUN echo "" > /app/timestamp.txt # Create timestamp.txt to bust cache
#RUN date > /app/timestamp.txt  # Create timestamp.txt to bust cache
#COPY timestamp.txt /app/ # Copy timestamp.txt to bust cache

ENV PORT 8080
CMD [ "python", "app.py" ]