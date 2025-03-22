# Use a base Python image
FROM python:3.12

# Set working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose ports if needed
EXPOSE 9092

# Default command (this will be overridden by docker-compose)
CMD ["tail", "-f", "/dev/null"]
