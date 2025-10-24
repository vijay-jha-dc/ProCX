# 🧠 ProCX - Proactive Customer Experience Platform

[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-blue)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green)](https://github.com/langchain-ai/langchain)
[![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen)](https://www.python.org/)

**ProCX** is an intelligent, multi-agent AI platform that transforms customer experience management through **100% proactive** intervention - predicting and preventing churn BEFORE customers complain or leave.

Built for the **AgentMAX Hackathon 2025** using LangGraph, LangChain, and OpenAI GPT-4.

---

## 🎯 The Problem We Solve

Traditional customer service is **reactive** - companies wait for customers to complain, then scramble to fix issues. By then, damage is already done and customers are often lost.

**ProCX flips the script with 100% proactive intelligence:**

- 🔮 **Predicts** churn risk before customers complain
- 🛡️ **Prevents** churn with early, culturally-aware interventions
- 📊 **Protects** revenue by saving at-risk customers proactively
- 🧠 **Learns** from historical patterns and resolution effectiveness
- 🌍 **Adapts** messaging for cultural context (festivals, language, timing)

---

## 🌟 Key Features

### 1. 🔮 Proactive Monitoring

- **Real-time health scoring** using 10-dimensional customer health model
- **Automated scanning** to identify at-risk customers before complaints
- **Pre-emptive intervention** generation with escalation continuity
- **Dashboard visualization** of customer health distribution
- **No reactive mode** - pure prevention focus

### 2. 🧠 Multi-Agent 

Four specialized agents working in sequence:
- **Bodha (बोध) - Awareness**: Context extraction and sentiment analysis
- **Dhyana (ध्यान) - Insight**: Pattern mining and churn prediction
- **Niti (नीति) - Strategy**: Decision making and escalation logic
- **Karuna (करुणा) - Compassion**: Empathetic, culturally-aware messaging

### 3. �️ Escalation Continuity & Memory

- **Escalation tracking** prevents duplicate automated interventions
- **Interaction history** preserves context across scans
- **Human-in-the-loop** integration with skip logic
- **JSONL persistence** for transparent audit trails

### 4. 📊 Comprehensive Data Integration

- **5-sheet dataset**: customers, orders, support_tickets, churn_labels, nps_surveys
- **Real-time analytics** on customer cohorts and segment comparisons
- **10-factor health scoring** algorithm with weighted calculations
- **Hybrid churn risk model**: 70% behavioral + 30% ML predicted

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.11+
OpenAI API Key
pip install -r requirements.txt
```

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/vijay-jha-dc/ProCX.git
cd ProCX
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment**

```bash
# Create .env file
cp .env.example .env

# Add your OpenAI API key
OPENAI_API_KEY=your-api-key-here
```

4. **Run the platform**

**Proactive Scan :**

```bash
python main.py --interventions
```

**Customer Health Dashboard:**

```bash
python main.py --dashboard
```

---

## �️ Architecture

See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for detailed system diagrams including:
- End-to-end system architecture
- Agent communication protocol
- Performance metrics and design philosophy

### Agent Responsibilities

| Agent | Sanskrit | Purpose | Key Outputs |
|-------|----------|---------|-------------|
| **Bodha** | बोध (Awareness) | Context extraction & sentiment analysis | Context summary, risk signals |
| **Dhyana** | ध्यान (Insight) | Pattern mining & churn prediction | Patterns, insights, churn risk |
| **Niti** | नीति (Strategy) | Decision making & escalation logic | Action plan, priority, escalation flag |
| **Karuna** | करुणा (Compassion) | Empathetic messaging generation | Personalized response, tone |

---

## � Project Scope

### Current Implementation
See our complete current scope visualization:

**[📸 View Current Scope Diagram →](./docs/scope/current.png)**

**What's Built:**
- ✅ Multi-agent LangGraph workflow 
- ✅ 10-factor health scoring algorithm
- ✅ Hybrid churn risk model (70% behavioral + 30% ML)
- ✅ Proactive monitoring dashboard
- ✅ Escalation continuity & skip logic
- ✅ JSONL memory persistence

### Future Vision
See how we envision ProCX evolving:

**[🚀 View Future Roadmap →](./docs/scope/future.png)**

**Planned Enhancements:**
- Real-time event streaming architecture
- Multi-channel delivery (Email/SMS/WhatsApp)
- Interactive web dashboard with analytics
- A/B testing framework for optimization
- Advanced ML models and forecasting

---



### UI/UX Planning

- **[docs/UI_WIREFRAME.md](./docs/UI_WIREFRAME.md)** - Future web dashboard wireframes
  - Dashboard mockups
  - User interface design
  - Feature layout planning

### Command Reference

- **[docs/commands.txt](./docs/commands.txt)** - All CLI commands and usage examples


🚀 **ProCX - Because prevention is better than cure!**
