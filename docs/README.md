# 🧠 AgentMAX CX - Empathic AI Customer Experience Platform

[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-blue)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green)](https://github.com/langchain-ai/langchain)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/)

**AgentMAX CX** is an intelligent, multi-agent AI platform that transforms customer experience management through empathetic, context-aware interactions powered by LangGraph and LangChain.

---

## 🎯 Problem Statement

Modern customer service faces critical challenges:
- **Generic responses** that lack personalization
- **Delayed escalations** for high-priority issues
- **Inconsistent** customer experience across segments
- **No pattern recognition** from historical interactions
- **Lack of empathy** in automated responses

**AgentMAX CX** solves these through a sophisticated multi-agent architecture that delivers:
✅ Context-aware analysis  
✅ Pattern-based predictions  
✅ Intelligent decision-making  
✅ Empathetic, personalized responses  

---

## 🏗️ Architecture

### Multi-Agent System

```
Customer Event
     ↓
┌────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Context    │ ───→ │   Pattern    │               │
│  │    Agent     │      │    Agent     │               │
│  └──────────────┘      └──────────────┘               │
│         ↓                      ↓                        │
│  Sentiment, Urgency,    Churn Prediction,              │
│  Risk Assessment        Historical Insights            │
│                                                         │
│         ↓                      ↓                        │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Decision   │ ───→ │   Empathy    │               │
│  │    Agent     │      │    Agent     │               │
│  └──────────────┘      └──────────────┘               │
│         ↓                      ↓                        │
│  Action Plan,           Personalized Response          │
│  Escalation Logic                                      │
│                                                         │
└────────────────────────────────────────────────────────┘
     ↓
Personalized Customer Response + Action Plan
```

### Agent Responsibilities

| Agent | Purpose | Outputs |
|-------|---------|---------|
| **Context Agent** | Analyzes customer events, extracts sentiment and urgency | Sentiment, Urgency (1-5), Risk Score (0-1), Context Summary |
| **Pattern Agent** | Identifies behavioral patterns and predicts churn | Churn Risk, Historical Insights, Similar Patterns |
| **Decision Agent** | Determines best actions and escalation needs | Recommended Action, Priority Level, Escalation Flag |
| **Empathy Agent** | Generates personalized, empathetic responses | Personalized Message, Tone, Empathy Score |

---

## 📁 Project Structure

```
AgentMAX/
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
│
├── agents/                          # Multi-agent implementations
│   ├── __init__.py
│   ├── context_agent.py            # Context & sentiment analysis
│   ├── pattern_agent.py            # Pattern recognition & prediction
│   ├── decision_agent.py           # Decision making & escalation
│   └── empathy_agent.py            # Response generation
│
├── workflows/                       # LangGraph workflows
│   ├── __init__.py
│   └── cx_workflow.py              # Main workflow orchestration
│
├── models/                          # Data models & schemas
│   ├── __init__.py
│   └── customer.py                 # Customer, Event, State models
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── settings.py                 # Application settings
│   └── prompts.py                  # Agent prompts & templates
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── memory_handler.py           # Memory & state management
│   └── event_simulator.py          # Event simulation for testing
│
└── data/                            # Data storage
    ├── AgentMAX_CX_dataset_cleaned.xlsx
    └── memory/                      # Interaction history storage
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **OpenAI API Key**
- **Git**

### Installation

#### 1️⃣ Clone the Repository
```bash
cd ProCX/AgentMAX
```

#### 2️⃣ Create Virtual Environment
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# OR
.venv\Scripts\activate  # Windows CMD
```

#### 3️⃣ Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4️⃣ Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

#### 5️⃣ Run the Platform
```bash
# Interactive mode (recommended for first run)
python main.py --mode interactive

# Demo mode (runs 3 predefined scenarios)
python main.py --mode demo

# Quick test
python main.py --mode test
```

---

## 💡 Usage Examples

### Interactive Mode

```bash
python main.py --mode interactive
```

Choose from:
1. **Process random event** - Generate and process a random customer interaction
2. **Process specific scenario** - Choose from predefined scenarios (VIP complaint, order delay, etc.)
3. **Process VIP customer event** - Focus on high-value customers
4. **View dataset statistics** - Analyze customer data
5. **View session summary** - See all processed interactions

### Demo Mode

```bash
python main.py --mode demo --demo-count 5
```

Runs through 5 predefined scenarios demonstrating the platform's capabilities.

### Programmatic Usage

```python
from main import AgentMAXCX
from utils import EventSimulator

# Initialize platform
platform = AgentMAXCX(use_routing=True)

# Generate an event
simulator = EventSimulator()
event = simulator.generate_scenario("vip_complaint")

# Process the event
final_state = platform.process_event(event, verbose=True)

# Access results
print(f"Priority: {final_state.priority_level}")
print(f"Response: {final_state.personalized_response}")
print(f"Escalation Needed: {final_state.escalation_needed}")
```

---

## 🧩 Folder Structure
```
ProCX/
├─ .venv/
├─ .env
├─ data/
│  ├─ raw/
│  └─ processed/
├─ src/
│  ├─ agents/
│  │  ├─ order_agent.py
│  │  ├─ empathy_agent.py
│  ├─ workflows/
│  ├─ pipelines/
│  └─ app.py
├─ tests/
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🧠 Running LangGraph

Once dependencies are installed and your `.env` is set:

### 1️⃣ Start LangGraph Dev Server
```bash
langgraph dev
```
This runs your local agent graph service. You can test your agents, call endpoints, and integrate with LangGraph Studio if desired.

### 2️⃣ (Optional) Debug with VS Code
Add a `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to LangGraph Dev",
      "type": "python",
      "request": "attach",
      "connect": { "host": "localhost", "port": 5678 },
      "pathMappings": [
        { "localRoot": "${workspaceFolder}", "remoteRoot": "${workspaceFolder}" }
      ]
    }
  ]
}
```
Then run LangGraph in debug mode:
```bash
langgraph dev --debug-port 5678
```

---

## 💡 Common Commands

| Task | Command |
|------|---------|
| Activate venv | `source .venv/Scripts/activate` |
| Deactivate venv | `deactivate` |
| Install deps | `pip install -r requirements.txt` |
| Update deps | `pip install -U -r requirements.txt` |
| Start LangGraph | `langgraph dev` |
| Debug LangGraph | `langgraph dev --debug-port 5678` |
| Freeze deps | `pip freeze > requirements.txt` |

---

## 🧑‍💻 Development Tips

- Always activate the venv before running Python commands.
- Use VS Code's interpreter selector → choose `.venv`.
- Keep your `.env` local and private.
- If you switch branches or pull new code, re-run:
  ```bash
  pip install -r requirements.txt
  ```
- Add docstrings and small comments — they help with agent logic clarity.
- For any permission errors in PowerShell, run:
  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

---

## 🔮 Next Steps

1. Implement your first LangGraph Agent (e.g., Order Event Agent).
2. Store datasets in `/data/raw` and processed versions in `/data/processed`.
3. Add utility functions and workflows in `/src/agents` and `/src/workflows`.
4. Run:
   ```bash
   langgraph dev
   ```
   to test and visualize your agents.

---

## 🤝 Contribution Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/<your-feature-name>
   ```
2. Commit changes:
   ```bash
   git add .
   git commit -m "Add <feature-name>"
   ```
3. Push and open a Pull Request:
   ```bash
   git push origin feature/<your-feature-name>
   ```

---

## ❤️ Made with Empathy by Team ProCX

Building intelligent, human-centered support experiences powered by AI.
