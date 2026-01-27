#!/bin/bash

# Setup script for Ainvestment - Ubuntu/Debian
# Usage: chmod +x setup.sh && ./setup.sh

set -e  # Exit on error

echo "🚀 Ainvestment Setup Script"
echo "============================="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "❌ This script is for Ubuntu/Debian systems only."
    exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    echo "⚠️  sudo not found. You may need to run this as root."
fi

echo "📦 Installing system dependencies..."
echo "This will install: python3-venv, python3-pip"
echo ""

# Install Python venv and pip
sudo apt update
sudo apt install -y python3-venv python3-pip

echo "✅ System dependencies installed"
echo ""

# Clean up any failed venv attempt
if [ -d "venv" ]; then
    echo "🧹 Removing incomplete virtual environment..."
    rm -rf venv
fi

echo "🔧 Creating virtual environment..."
python3 -m venv venv

echo "✅ Virtual environment created"
echo ""

echo "📥 Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-new.txt

echo "✅ Python packages installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created (edit this file to add API keys)"
else
    echo "ℹ️  .env already exists (skipping)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "To configure LLM (optional):"
echo "  - For Ollama (free, local): Install from ollama.ai"
echo "  - For OpenAI (paid): Add OPENAI_API_KEY to .env"
echo ""
