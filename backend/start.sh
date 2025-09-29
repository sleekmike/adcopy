#!/bin/bash

# AI Ad Copy Generator - Startup Script

echo "🚀 Starting AI Ad Copy Generator Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your actual API keys and settings."
fi

# Start the server
echo "🎯 Starting FastAPI server..."
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
