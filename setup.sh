#!/bin/bash
# Setup script for Reelgood Scraper

echo "🚀 Setting up Reelgood Scraper..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.6 or higher first"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Try it out:"
    echo "  python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010"
    echo ""
else
    echo ""
    echo "⚠️  Installation may have encountered issues"
    echo "If you see permission errors, try:"
    echo "  pip3 install -r requirements.txt --user"
    echo "or"
    echo "  pip3 install -r requirements.txt --break-system-packages"
fi
