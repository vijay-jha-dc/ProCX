#!/bin/bash
# AgentMAX CX - Quick Start Script
# Run this script to quickly set up and test the platform

set -e  # Exit on error

echo "🚀 AgentMAX CX - Quick Start"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/Scripts/activate || source .venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel --quiet
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Check for .env file
echo ""
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   Open .env in a text editor and replace 'your_openai_api_key_here'"
    echo ""
    read -p "Press Enter after you've added your API key..."
else
    echo "✓ .env file exists"
fi

# Verify dataset
echo ""
if [ -f "data/AgentMAX_CX_dataset_cleaned.xlsx" ]; then
    echo "✓ Dataset found"
else
    echo "⚠️  Dataset not found in data/"
    if [ -f "../AgentMAX_CX_dataset.xlsx" ]; then
        echo "📋 Copying dataset from parent directory..."
        cp ../AgentMAX_CX_dataset.xlsx data/AgentMAX_CX_dataset_cleaned.xlsx
        echo "✓ Dataset copied"
    else
        echo "❌ Error: Dataset not found"
        echo "   Please ensure AgentMAX_CX_dataset.xlsx is in the data/ folder"
        exit 1
    fi
fi

# Test imports
echo ""
echo "🧪 Testing imports..."
python -c "
from agents import ContextAgent, PatternAgent, DecisionAgent, EmpathyAgent
from workflows import create_cx_workflow
from utils import EventSimulator, MemoryHandler
from models import AgentState, Customer, CustomerEvent
print('✓ All imports successful')
" || {
    echo "❌ Import test failed"
    echo "   Try running: pip install -r requirements.txt"
    exit 1
}

# Test dataset loading
echo ""
echo "📊 Testing dataset loading..."
python -c "
from utils import EventSimulator
sim = EventSimulator()
stats = sim.get_dataset_stats()
print(f'✓ Dataset loaded: {stats[\"total_customers\"]} customers')
" || {
    echo "❌ Dataset loading failed"
    exit 1
}

# Success!
echo ""
echo "=============================="
echo "✅ Setup Complete!"
echo "=============================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Run demo mode (recommended):"
echo "   python main.py --mode demo"
echo ""
echo "2. Run interactive mode:"
echo "   python main.py --mode interactive"
echo ""
echo "3. Run simple example:"
echo "   python example_simple.py"
echo ""
echo "4. Quick test:"
echo "   python main.py --mode test"
echo ""
echo "📚 Documentation:"
echo "   - README.md  - Full documentation"
echo "   - SETUP.md   - Detailed setup guide"
echo "   - API.md     - API reference"
echo ""
echo "Happy hacking! 🚀"
