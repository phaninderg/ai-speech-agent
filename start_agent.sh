#!/bin/bash
# Quick start script for AI Speech Agent

echo "================================================"
echo "   AI SPEECH AGENT - Offline Assistant"
echo "================================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo ""
    echo "Please start Ollama first:"
    echo "  1. Open a new terminal"
    echo "  2. Run: ollama serve"
    echo ""
    read -p "Press Enter once Ollama is running, or Ctrl+C to exit..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.13 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "✓ Starting AI Speech Agent..."
echo ""
echo "Voice Commands:"
echo "  - Say 'exit' or 'goodbye' to end"
echo "  - Say 'clear history' to reset"
echo ""
echo "================================================"
echo ""

# Activate and run
source venv/bin/activate
python speech_agent_macos_say.py "$@"
