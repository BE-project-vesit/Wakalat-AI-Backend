#!/bin/bash
# Setup script for Wakalat-AI Backend

set -e

echo "🔧 Setting up Wakalat-AI Backend..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/chroma data/documents logs

# Copy environment file
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration!"
else
    echo "✅ .env file already exists"
fi

# Run tests
echo "🧪 Running tests..."
pytest tests/ || echo "⚠️  Some tests failed (expected for template)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m src.server"
echo ""
echo "Or use: ./scripts/run_server.sh"
