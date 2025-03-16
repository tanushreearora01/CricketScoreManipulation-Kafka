FROM python:3.9-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the producer script
COPY kafka_producer.py .

# Set environment variable to indicate Docker environment
ENV RUNNING_IN_DOCKER=true

# Run the producer script
CMD ["python", "kafka_producer.py"]