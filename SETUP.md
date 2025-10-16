# 🚀 AgentMAX CX - Setup Guide

Complete step-by-step setup guide for the AgentMAX CX Platform.

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.10 or higher** installed
- ✅ **Git** installed
- ✅ **OpenAI API Key** (sign up at https://platform.openai.com)
- ✅ **Windows with Bash** (Git Bash or WSL)
- ✅ **VS Code** (recommended)

---

## Step-by-Step Setup

### 1️⃣ Navigate to Project Directory

```bash
cd /c/Users/VijayJha/Documents/AgentMax-Hackathon/ProCX/AgentMAX
```

### 2️⃣ Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Verify creation
ls -la .venv/
```

### 3️⃣ Activate Virtual Environment

**For Git Bash (Windows):**
```bash
source .venv/Scripts/activate
```

**For CMD (Windows):**
```cmd
.venv\Scripts\activate
```

**For WSL/Linux:**
```bash
source .venv/bin/activate
```

✅ You should see `(.venv)` prefix in your terminal.

### 4️⃣ Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 5️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `langgraph` - Multi-agent orchestration
- `langchain` - LLM framework
- `langchain-openai` - OpenAI integration
- `pandas` - Data processing
- `openpyxl` - Excel file support
- `python-dotenv` - Environment variables

### 6️⃣ Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Add your OpenAI API key:**
```ini
OPENAI_API_KEY=sk-your-actual-key-here
```

**Optional LangChain tracing:**
```ini
LANGCHAIN_API_KEY=your-langchain-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentMAX-CX
```

### 7️⃣ Verify Dataset

```bash
# Check if dataset exists
ls -lh data/AgentMAX_CX_dataset_cleaned.xlsx

# If missing, copy from parent directory
cp ../AgentMAX_CX_dataset.xlsx data/AgentMAX_CX_dataset_cleaned.xlsx
```

### 8️⃣ Test Installation

```bash
# Quick test
python -c "import langgraph, langchain, pandas; print('✓ All packages installed')"

# Verify dataset loading
python -c "from utils import EventSimulator; s = EventSimulator(); print(s.get_dataset_stats())"
```

### 9️⃣ Run First Test

```bash
# Run in test mode (requires OpenAI API key)
python main.py --mode test
```

If successful, you should see:
- ✓ Customer data loaded
- ✓ Workflow created
- ✓ Event processed
- ✓ Results displayed

---

## 🎮 Running the Platform

### Interactive Mode (Recommended)

```bash
python main.py --mode interactive
```

**Features:**
- Process random events
- Choose predefined scenarios
- Test VIP customer handling
- View statistics

### Demo Mode

```bash
# Run 3 scenarios
python main.py --mode demo

# Run 5 scenarios
python main.py --mode demo --demo-count 5
```

### Simple Example

```bash
python example_simple.py
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/Scripts/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OpenAI API Key not found"

**Solution:**
```bash
# Check .env file exists
cat .env

# Ensure OPENAI_API_KEY is set
export OPENAI_API_KEY=sk-your-key  # Temporary for current session

# Or edit .env permanently
nano .env
```

### Issue: "Dataset not found"

**Solution:**
```bash
# Copy dataset
cp ../AgentMAX_CX_dataset.xlsx data/AgentMAX_CX_dataset_cleaned.xlsx

# Verify
ls -lh data/
```

### Issue: "Permission denied" (PowerShell)

**Solution:**
```powershell
# Run in PowerShell as Administrator
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Then activate venv
.\.venv\Scripts\Activate.ps1
```

### Issue: Rate Limit or API Errors

**Solution:**
```bash
# Use GPT-3.5 for testing (cheaper, faster)
# Edit .env:
LLM_MODEL=gpt-3.5-turbo

# Or set in terminal
export LLM_MODEL=gpt-3.5-turbo
```

---

## 📊 Verifying Setup

Run these commands to verify everything works:

```bash
# 1. Check Python version
python --version  # Should be 3.10+

# 2. Check virtual environment
which python  # Should point to .venv

# 3. Check packages
pip list | grep -E "langgraph|langchain|pandas"

# 4. Check imports
python -c "
from agents import ContextAgent, PatternAgent, DecisionAgent, EmpathyAgent
from workflows import create_cx_workflow
from utils import EventSimulator, MemoryHandler
from models import AgentState, Customer, CustomerEvent
print('✓ All imports successful')
"

# 5. Check dataset
python -c "
from utils import EventSimulator
sim = EventSimulator()
stats = sim.get_dataset_stats()
print(f'✓ Dataset loaded: {stats[\"total_customers\"]} customers')
"
```

All should pass without errors.

---

## 🎯 Next Steps

Once setup is complete:

1. **Run Demo** - See the platform in action
   ```bash
   python main.py --mode demo
   ```

2. **Explore Scenarios** - Try different customer situations
   ```bash
   python main.py --mode interactive
   ```

3. **Read Documentation** - Check README.md for features

4. **Customize** - Modify prompts in `config/prompts.py`

5. **Extend** - Add new agents or workflows

---

## 📚 Additional Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Docs**: https://python.langchain.com/
- **OpenAI API**: https://platform.openai.com/docs

---

## ✅ Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] .env file configured with API key
- [ ] Dataset present in data/ folder
- [ ] Test run successful
- [ ] Demo mode works
- [ ] Interactive mode accessible

---

**Setup complete! You're ready to use AgentMAX CX! 🎉**
