#!/bin/bash
echo "Building Docker image 'contrarian-app'..."
echo "Running container on port 8080..."

# Use --env-file if .env exists
if [ -f .env ]; then
  docker run -p 8080:8080 --env-file .env contrarian-app
else
  echo "WARNING: No .env file found. AI features will be disabled."
  docker run -p 8080:8080 -e GEMINI_API_KEY=$GEMINI_API_KEY contrarian-app
fi
