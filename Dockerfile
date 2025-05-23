# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /

# Copy requirements.txt if it exists
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (change if your app uses a different port)
EXPOSE 8000

# Define environment variable (optional)
ENV PYTHONUNBUFFERED=1

# Run the application (replace with your actual entrypoint)
CMD ["python", "app.py"]