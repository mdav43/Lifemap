#!/bin/bash

# Lifemap Quick Start Script
# This script helps you get started with the GPS mapping tool

echo "=================================================="
echo "Lifemap - GPS Mapping Tool Quick Start"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

echo "✓ pip found"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
echo ""
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully"
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads data/archive

echo "✓ Data directories created"
echo ""

# Run tests
echo "Running test suite..."
python3 test_gps_tool.py

if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "✓ Setup complete! Your GPS mapping tool is ready."
echo "=================================================="
echo ""
echo "To start the application, run:"
echo "  streamlit run app.py"
echo ""
echo "Then open your browser at http://localhost:8501"
echo ""
echo "Sample files to try:"
echo "  - sample_gps_track.csv (San Francisco)"
echo "  - sample_nyc_track.csv (New York City)"
echo ""
echo "For more information, see:"
echo "  - README.md for overview"
echo "  - USAGE.md for detailed usage guide"
echo ""
echo "=================================================="
