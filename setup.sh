#!/bin/bash
# Quick setup script for SocraticTeach-Env

set -e

echo "🚀 SocraticTeach-Env Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python --version
echo ""

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo ""
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Setup environment variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created (edit with your values)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Run validation
echo "✅ Running validation..."
python validation_script.py
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API credentials (optional)"
echo "2. Run app.py for interactive interface:"
echo "   python app.py"
echo "3. Or run inference:"
echo "   python inference.py"
echo "4. Or use Docker:"
echo "   docker build -t socraticteach-env ."
echo "   docker run -p 7860:7860 socraticteach-env"
