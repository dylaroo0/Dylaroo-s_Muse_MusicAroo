# Use official Python 3.9 image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Essentia, MuseScore, and soundfile
RUN apt-get update && apt-get install -y \
    musescore3 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Essentia (binary distribution)
RUN pip install essentia==2.1b6.dev1110

# Copy the application code
COPY src/ ./src/
COPY input_files/ ./input_files/
COPY essentia_runner.py .
COPY requirements.txt .

# Set environment variable to indicate Docker environment
ENV DOCKER_ENV=1

# Expose the API port
EXPOSE 8000

# Command to run the API server
CMD ["python", "src/api_server.py"]