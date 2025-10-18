# 🧠 ProCX - Proactive Customer Experience Platform

[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-blue)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green)](https://github.com/langchain-ai/langchain)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/)

**ProCX** is an intelligent, multi-agent AI platform that transforms customer experience management through **proactive** intervention - predicting and preventing churn BEFORE customers complain or leave.

Built for the **AgentMAX Hackathon 2025** using LangGraph, LangChain, and GPT-4.

---

## 🎯 The Problem We Solve

Traditional customer service is **reactive** - companies wait for customers to complain, then scramble to fix issues. By then, damage is already done and customers are often lost.

**ProCX flips the script:**
- 🔮 **Predicts** churn risk before customers complain
- 🛡️ **Prevents** churn with early, personalized interventions
- 📊 **Protects** revenue by saving at-risk customers proactively

---

## 🌟 Key Features

### 1. 🔮 Proactive Monitoring
- **Real-time health scoring** of all 1,000 customers using 10 factors
- **Automated scanning** to identify at-risk customers
- **Pre-emptive intervention** generation before complaints occur
- **Dashboard visualization** of customer health distribution

### 2. 🌐 Multi-Language Intelligence
- **5 languages supported:** English, Hindi, Tamil, Telugu, Bengali
- **Auto-detection** from customer database
- **GPT-4 powered** culturally appropriate responses
- **Localized** for Indian market

### 3. 🧠 Intelligent Pattern Matching
- **Dual-layer approach:**
  - **Layer 1:** Similar customer profiles (demographics, behavior, value)
  - **Layer 2:** Similar historical issues (problem types, resolutions)
- **Learning from history:** Recommends solutions that actually worked
- **Resolution effectiveness:** Analyzes CSAT scores to identify best practices

### 4. 💳 Payment Intelligence
- **Payment failure tracking** across all transactions
- **Churn signals** from payment reliability (75% failure rate = high risk)
- **Cross-referenced** with orders for complete financial view

### 5. 📊 Comprehensive Data Integration
- **10 data sources:** customers, orders, support_tickets, churn_labels, nps_survey, payments, shipments, refunds, products, customer_events
- **Real-time analytics** on customer cohorts
- **NPS-aware** tone adjustment
- **Support history** tracking and analysis

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.10+
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

**For Judges/Demo (Recommended):**
```bash
python main.py --mode proactive
```

**For Testing Scenarios:**
```bash
python main.py --mode demo
```

**For Interactive Exploration:**
```bash
python main.py --mode interactive
```

---

## 🎬 Demo Modes Explained

### 🔮 Proactive Mode (⭐ Our Differentiator)

```bash
python main.py --mode proactive
```

**What it shows:**
- Scans all 1,000 customers in real-time
- Identifies at-risk customers using 10-factor health score
- Generates automated retention interventions
- Displays customer health dashboard
- Shows **prevention vs reaction** approach

**Why it wins:**
- This is what makes ProCX unique
- Demonstrates AI-powered prediction
- Shows business value (save customers before they leave)

### 🎬 Demo Mode (Scenario Showcase)

```bash
python main.py --mode demo
```

**What it shows:**
- 5 pre-built customer scenarios
- Multi-agent workflow in action
- Data-driven decision making
- Multi-language responses
- End-to-end customer interaction

### 🎮 Interactive Mode (Hands-On)

```bash
python main.py --mode interactive
```

**What it shows:**
- Menu-driven interface
- Custom event generation
- Real-time customer analytics
- Session summaries

---

## 🏗️ Architecture

### Multi-Agent System (LangGraph)

```
Customer Event
     ↓
┌─────────────────────────────────────────────────────┐
│              LANGGRAPH WORKFLOW                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐      ┌──────────────┐            │
│  │   Context    │ ───→ │   Pattern    │            │
│  │    Agent     │      │    Agent     │            │
│  └──────────────┘      └──────────────┘            │
│         ↓                      ↓                     │
│  Sentiment, Urgency     Churn Prediction            │
│  Risk Assessment        Historical Patterns         │
│                                                      │
│         ↓                      ↓                     │
│  ┌──────────────┐      ┌──────────────┐            │
│  │   Decision   │ ───→ │   Empathy    │            │
│  │    Agent     │      │    Agent     │            │
│  └──────────────┘      └──────────────┘            │
│         ↓                      ↓                     │
│  Action Plan            Personalized Response       │
│  Escalation Logic       (Multi-Language)            │
│                                                      │
└─────────────────────────────────────────────────────┘
     ↓
Customer Response + Action Plan + Memory Storage
```

### Agent Responsibilities

| Agent | Purpose | Key Outputs |
|-------|---------|-------------|
| **Context Agent** | Analyzes customer events, sentiment, urgency | Sentiment, Urgency (1-5), Risk Score, Summary |
| **Pattern Agent** | Predicts churn using historical patterns | Churn Risk (%), Similar Patterns, Insights |
| **Decision Agent** | Determines best action and escalation | Action Plan, Priority, Escalation Flag |
| **Empathy Agent** | Generates personalized responses | Multi-Language Message, Tone, Empathy Score |

---

## 📁 Project Structure

```
ProCX/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore rules
│
├── agents/                     # Multi-agent implementations
│   ├── context_agent.py       # Sentiment & urgency analysis
│   ├── pattern_agent.py       # Churn prediction & patterns
│   ├── decision_agent.py      # Action planning & escalation
│   └── empathy_agent.py       # Multi-language response generation
│
├── workflows/                  # LangGraph workflows
│   └── cx_workflow.py         # Main agent orchestration
│
├── models/                     # Data models
│   └── customer.py            # Customer & event models
│
├── config/                     # Configuration
│   ├── settings.py            # App settings & API keys
│   └── prompts.py             # Agent system prompts
│
├── utils/                      # Utilities
│   ├── data_analytics.py      # Multi-sheet data analysis
│   ├── proactive_monitor.py   # Health scoring & monitoring
│   ├── memory_handler.py      # Interaction memory
│   └── event_simulator.py     # Demo event generation
│
├── data/                       # Data directory
│   ├── AgentMAX_CX_dataset.xlsx  # 10-sheet customer dataset
│   └── memory/                # Customer interaction history
│
└── hackathon_requirements/     # Problem statement & requirements
```

---

## 🎯 How It Works

### 10-Factor Health Scoring Algorithm

ProCX calculates customer health using:

1. **Order Frequency Score** (20%) - How often they purchase
2. **Recency Score** (15%) - Time since last order
3. **Lifetime Value Score** (15%) - Total customer value
4. **Support Ticket Score** (10%) - Support interaction frequency
5. **CSAT Score** (10%) - Customer satisfaction ratings
6. **NPS Score** (10%) - Net Promoter Score
7. **Payment Reliability** (10%) - Payment success rate
8. **Churn Label** (5%) - ML prediction from dataset
9. **Segment Bonus** (3%) - VIP/Loyal customer boost
10. **Activity Signals** (2%) - Recent engagement

**Final Health Score** = Weighted sum of all factors  
**Churn Risk** = 100% - Health Score

### Churn Prediction Model

**Hybrid Approach:**
- **60% Data-Driven:** Using 10 factors above
- **40% AI Inference:** GPT-4 analyzing patterns and context

This combination provides both **explainable** (data-based) and **intelligent** (AI-based) predictions.

---

## 📊 Dataset

**Source:** `data/AgentMAX_CX_dataset.xlsx` (10 sheets)

| Sheet | Records | Purpose |
|-------|---------|---------|
| **customers** | 1,000 | Base profiles, segments, LTV, loyalty tiers |
| **orders** | 5,000 | Purchase history, frequency, recency |
| **support_tickets** | 2,000 | Issue descriptions, resolutions, CSAT |
| **churn_labels** | 1,000 | Ground truth churn data with ML predictions |
| **nps_survey** | 800 | Net Promoter Scores |
| **payments** | 4,750 | Transaction history, payment failures |
| **shipments** | 1,346 | Delivery tracking |
| **refunds** | 400 | Return requests |
| **products** | 300 | Product catalog |
| **customer_events** | 10,000 | Behavioral signals |

---

## 🏆 Competitive Advantages

### 1. **Proactive vs Reactive**
- Traditional: Wait for complaint → React
- ProCX: Predict churn → Prevent → Protect revenue

### 2. **Multi-Language Intelligence**
- Authentic localization in 5 Indian languages
- GPT-4 powered cultural awareness
- Auto-detection from customer preferences

### 3. **Comprehensive Data Integration**
- Uses ALL 10 data sources (not just customer profiles)
- Payment intelligence for early churn signals
- NPS-aware tone adjustment

### 4. **Intelligent Learning**
- Dual-layer pattern matching
- Learns from what actually worked (CSAT analysis)
- Recommends proven solutions

### 5. **Real-Time Health Monitoring**
- Dashboard visualization
- 10-factor scoring algorithm
- Priority-based intervention queue

### 6. **Production-Ready**
- Memory persistence (JSONL)
- Error handling and fallbacks
- Scalable LangGraph architecture

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
LLM_MODEL=gpt-4o                    # Default model
LLM_TEMPERATURE=0.7                  # Creativity (0-1)
LLM_MAX_TOKENS=2000                  # Response length

# LangSmith (Optional - for debugging)
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ProCX
```

### Model Selection

**Default:** `gpt-4o` (Recommended)
- Latest GPT-4 model
- Fastest response times
- Best quality

**Alternative:** `gpt-4o-mini`
- Faster
- Cheaper
- Good for testing

Edit in `config/settings.py`:
```python
LLM_MODEL = "gpt-4o-mini"  # or "gpt-4o"
```

---

## 🧪 Example Outputs

### Proactive Intervention

```
⚠️  Found 13 at-risk customers requiring intervention!

🎯 PROACTIVE INTERVENTION #1/5
👤 Customer: Sakshi Bhat (C100703)
   Segment: Loyal | Tier: Bronze
   Lifetime Value: $2,466.74

📊 Health Analysis:
   Health Score: 42.6% 🔴
   Churn Risk: 69.9% 🟠
   Risk Level: MEDIUM

🎯 Recommended Action: retention_offer_standard
💬 Personalized Message: [Generated in customer's preferred language]
```

### Multi-Language Response Example

**Customer:** Sakshi Patel (Language: Bengali)

**Response:**
> প্রিয় সক্ষী প্যাটেল, আপনার অসন্তোষের জন্য আমি আন্তরিকভাবে দুঃখিত। 
> আপনার গুরুত্বপূর্ণ ব্রোঞ্জ এবং VIP অবস্থানকে আমরা গভীরভাবে মূল্যায়ন করি...

*(Translation: Dear Sakshi Patel, I sincerely apologize for your dissatisfaction. 
We deeply value your important Bronze and VIP status...)*

---

## 📈 Performance Metrics

- **Processing Time:** 12-36 seconds per customer (GPT-4 quality)
- **Churn Prediction:** 60% data-driven + 40% AI inference
- **Empathy Scores:** Consistently 85-95%
- **Language Accuracy:** 100% (database-driven)
- **Dataset Coverage:** 1,000 customers, 5,000 orders, 2,000 tickets

---

## 🚧 Troubleshooting

### Common Issues

**1. "No module named 'langchain_openai'"**
```bash
pip install langchain-openai
```

**2. "OpenAI API key not found"**
- Check `.env` file exists
- Verify `OPENAI_API_KEY=sk-...` is set
- Restart application after adding key

**3. "Cannot read Excel file"**
```bash
pip install openpyxl
```

**4. Pandas SettingWithCopyWarning**
- These are warnings, not errors
- Code functions correctly
- Can be suppressed if desired

---

## 🛣️ Roadmap

### Completed ✅
- [x] Multi-agent LangGraph workflow
- [x] 10-factor health scoring
- [x] Multi-language support (5 languages)
- [x] Payment intelligence
- [x] Intelligent pattern matching
- [x] Proactive monitoring dashboard
- [x] Memory persistence

### Future Enhancements 🚀
- [ ] Real-time event streaming
- [ ] A/B testing framework
- [ ] Custom ML churn models
- [ ] API endpoints for integration
- [ ] Web dashboard UI
- [ ] Email/SMS intervention delivery
- [ ] Advanced analytics & reporting

---

## 🤝 Contributing

This is a hackathon project. For questions or collaboration:
- **Author:** Vijay Jha
- **GitHub:** [@vijay-jha-dc](https://github.com/vijay-jha-dc)
- **Event:** AgentMAX Hackathon 2025

---

## 📄 License

MIT License - Built for AgentMAX Hackathon 2025

---

## 🙏 Acknowledgments

- **LangChain & LangGraph** - Multi-agent orchestration framework
- **OpenAI** - GPT-4 language model
- **AgentMAX Hackathon** - For the challenge and dataset

---

## 🎯 For Judges

### Why ProCX Wins:

1. **✨ Innovation:** Proactive vs reactive - we don't wait for problems
2. **🌐 Market Fit:** Multi-language for Indian customer base
3. **📊 Completeness:** Uses all 10 data sheets, not just customer profiles
4. **🧠 Intelligence:** Dual-layer pattern matching learns from history
5. **🏗️ Architecture:** Production-ready LangGraph multi-agent system
6. **💡 Business Value:** Measurable ROI through churn prevention

### Quick Demo Script:

```bash
# 1. Show the differentiator (2 minutes)
python main.py --mode proactive

# 2. Show the workflow (1 minute)
python main.py --mode demo --demo-count 1

# 3. Highlight features:
# - "Look at the multi-language response!"
# - "See how we use payment data to predict churn?"
# - "Notice the 10-factor health score?"
# - "We're preventing problems, not just reacting to them"
```

---

**Built with ❤️ for AgentMAX Hackathon 2025**

🚀 **ProCX - Because prevention is better than cure!**
