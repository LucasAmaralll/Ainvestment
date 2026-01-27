#!/bin/bash

# Ollama Installation Script for Linux
# Usage: chmod +x install-ollama.sh && ./install-ollama.sh

set -e  # Exit on error

echo "🦙 Ollama Installation Script"
echo "=============================="
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed!"
    ollama --version
    echo ""
    echo "To start Ollama server: ollama serve"
    echo "To pull a model: ollama pull llama3.1:8b"
    exit 0
fi

echo "📦 Installing Ollama..."
echo ""

# Official Ollama installation command
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "✅ Ollama installed successfully!"
echo ""

# Check if installation was successful
if command -v ollama &> /dev/null; then
    ollama --version
    echo ""
    echo "🚀 Next steps:"
    echo ""
    echo "1. Start Ollama server (run in background):"
    echo "   ollama serve &"
    echo ""
    echo "2. Pull a recommended model (choose one):"
    echo "   ollama pull llama3.1:8b       # Recommended (4.7GB) - Good balance"
    echo "   ollama pull llama3.2:3b       # Smaller (2GB) - Faster but less accurate"
    echo "   ollama pull llama3.1:70b      # Larger (40GB) - Best quality, needs 64GB+ RAM"
    echo ""
    echo "3. Test if it's working:"
    echo "   ollama run llama3.1:8b \"Hello, how are you?\""
    echo ""
    echo "4. Update .env file:"
    echo "   LLM_PROVIDER=ollama"
    echo "   OLLAMA_MODEL=llama3.1:8b"
    echo "   OLLAMA_BASE_URL=http://localhost:11434"
    echo ""
    echo "5. Start the Ainvestment app:"
    echo "   source venv/bin/activate"
    echo "   streamlit run app.py"
    echo ""
    echo "💡 To run Ollama server automatically on system startup:"
    echo "   sudo systemctl enable ollama"
    echo "   sudo systemctl start ollama"
    echo ""
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
