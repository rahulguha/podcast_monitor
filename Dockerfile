# Start with the official Ollama image
FROM ollama/ollama:latest as ollama

# Python application stage
FROM python:3.12-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Ollama from the official image
COPY --from=ollama /usr/bin/ollama /usr/bin/ollama

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file and the rest of the application
COPY .env .
COPY . .

# Set environment variables from .env file
ENV $(cat .env | xargs)

# Create a startup script that handles termination signals properly
RUN echo '#!/bin/bash\n\
trap "kill 0" SIGTERM SIGINT\n\
ollama serve & \
sleep 5 && \
ollama pull gemma2:9b && \
python monitor.py & \
wait' > /app/start.sh && \
chmod +x /app/start.sh

# Command to run the startup script
CMD ["/app/start.sh"]