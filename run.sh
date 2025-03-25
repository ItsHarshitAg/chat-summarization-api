#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Check if port is specified
PORT=${1:-8000}

# Run the FastAPI application
echo "Starting Chat Summarization API on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT --reload
