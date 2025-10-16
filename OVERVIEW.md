# 🎯 AgentMAX CX Platform - Complete Overview

**An Empathic AI-Driven Customer Experience Platform**  
Built for AgentMAX Hackathon by Team ProCX

---

## 🚀 What Is This?

AgentMAX CX is a **production-ready multi-agent AI system** that revolutionizes customer experience management through:

- **4 specialized AI agents** working in harmony
- **LangGraph orchestration** for complex workflows  
- **Real-time sentiment & pattern analysis**
- **Empathetic, personalized responses**
- **Intelligent escalation & decision-making**

---

## ⚡ Quick Demo

```bash
# Setup (one time)
cd AgentMAX
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Run demo
python main.py --mode demo
```

**That's it!** You'll see 5 scenarios demonstrating the platform's capabilities.

---

## 🏗️ Architecture Overview

### The Multi-Agent Pipeline

```
Customer Event (e.g., "VIP customer complaint")
    ↓
┌───────────────────────────────────────────────────┐
│  CONTEXT AGENT                                    │
│  • Analyzes sentiment (very negative)             │
│  • Measures urgency (4/5 - high)                  │
│  • Assesses risk (0.8 - customer at risk)         │
│  Output: Context summary with key insights        │
└───────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────┐
│  PATTERN AGENT                                    │
│  • Identifies historical patterns                 │
│  • Predicts churn risk (0.75 - high risk)         │
│  • Finds similar past cases                       │
│  Output: Behavioral insights & predictions        │
└───────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────┐
│  DECISION AGENT                                   │
│  • Plans action (immediate replacement + gift)    │
│  • Determines priority (CRITICAL for VIP)         │
│  • Decides escalation (YES - human needed)        │
│  Output: Action plan with escalation flag         │
└───────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────┐
│  EMPATHY AGENT                                    │
│  • Crafts personalized response                   │
│  • Adapts tone (apologetic + premium)             │
│  • Scores empathy (0.9 - highly empathetic)       │
│  Output: Ready-to-send customer message           │
└───────────────────────────────────────────────────┘
    ↓
Final Result: Personalized response + Complete action plan
```

---

## 📊 Real-World Example

### Input

```
Customer: Sarah Johnson (VIP, Platinum Tier)
Event: Complaint - "Order delayed 5 days, needed for anniversary!"
Lifetime Value: $12,450
```

### Output

```
🔍 Analysis:
   Sentiment: VERY NEGATIVE
   Urgency: 5/5 (Critical)
   Churn Risk: 85%
   Priority: CRITICAL
   Escalation: YES

💬 Personalized Response:
   "Dear Ms. Johnson,

   We are deeply sorry for the delay with your anniversary order.
   As a valued Platinum member, you deserve better.
   
   We're immediately:
   • Expediting your order with next-day delivery
   • Including a complimentary gift
   • Applying a $50 credit to your account
   • Assigning a VIP specialist to your case
   
   Your specialist will call within the hour.
   
   Thank you for your patience and continued trust.
   
   Warmest regards,
   Customer Experience Team"
```

---

## 🎯 Problem It Solves

### Before AgentMAX CX ❌

- Generic "Dear Customer" responses
- No urgency differentiation
- Missed escalation opportunities
- Inconsistent VIP treatment
- No churn prediction
- Manual prioritization

### After AgentMAX CX ✅

- Personalized by segment & tier
- Automatic urgency detection
- Smart escalation logic
- VIP-specific handling
- Predictive churn analysis
- Intelligent auto-prioritization

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Agent Framework** | LangGraph (latest) |
| **LLM Orchestration** | LangChain 0.3+ |
| **Language Models** | OpenAI GPT-4 |
| **Data Processing** | Pandas, NumPy |
| **State Management** | Custom Memory Handler |
| **Language** | Python 3.10+ |
| **Architecture** | Multi-Agent System |

---

## 📁 Key Files

### For Running

- **`main.py`** - Main application (start here!)
- **`example_simple.py`** - Quick example script
- **`quickstart.sh`** - Automated setup script

### For Development

- **`agents/`** - 4 specialized agents
- **`workflows/`** - LangGraph orchestration
- **`models/`** - Data schemas
- **`config/`** - Settings & prompts
- **`utils/`** - Helper utilities

### For Learning

- **`README.md`** - Complete documentation
- **`SETUP.md`** - Setup guide
- **`API.md`** - API reference
- **`PROJECT_SUMMARY.md`** - This overview

---

## 🎮 Usage Modes

### 1. Demo Mode (Best for presentations)

```bash
python main.py --mode demo
```

Runs 5 predefined scenarios:
1. VIP complaint
2. Loyal customer order delay
3. New customer inquiry
4. High-value at-risk
5. Positive feedback

### 2. Interactive Mode (Best for exploration)

```bash
python main.py --mode interactive
```

Menu-driven interface:
- Process random events
- Choose specific scenarios
- Test VIP handling
- View statistics

### 3. Test Mode (Quick verification)

```bash
python main.py --mode test
```

Runs single test to verify setup.

### 4. Programmatic (For development)

```python
from main import AgentMAXCX

platform = AgentMAXCX()
event = platform.event_simulator.generate_event()
result = platform.process_event(event)
```

---

## 📊 Dataset Details

**1000 customer records** with rich attributes:

### Segments (Customer Type)
- **VIP** (42) - Highest priority, immediate escalation
- **Loyal** (140) - Long-term customers, high empathy
- **Regular** (623) - Standard handling
- **Occasional** (195) - Onboarding focus

### Loyalty Tiers
- **Platinum** (37) - Premium benefits
- **Gold** (146) - Enhanced service
- **Silver** (303) - Standard plus
- **Bronze** (514) - Basic

### Categories
Sports, Electronics, Fashion, Books, Home & Kitchen, Beauty, Toys

### Lifetime Value
Range: $69 - $16,864  
Mean: $3,003  
High-value threshold: $5,000+

---

## 🎨 Key Features

### ✅ Context-Aware Processing

- **Sentiment Detection**: 5 levels (very positive → very negative)
- **Urgency Scoring**: 1-5 scale with auto-thresholds
- **Risk Assessment**: 0-1 churn probability
- **Context Extraction**: AI-powered summarization

### ✅ Pattern Recognition

- **Historical Analysis**: Past interaction patterns
- **Churn Prediction**: ML-based risk scoring
- **Similar Cases**: Find relevant past resolutions
- **Preventive Actions**: Proactive recommendations

### ✅ Intelligent Decisions

- **Action Planning**: Specific resolution steps
- **Auto-Escalation**: Rule-based + AI logic
- **Priority Routing**: 4 levels (low → critical)
- **Segment-Aware**: VIP, Loyal, Regular, Occasional

### ✅ Empathetic Responses

- **Personalization**: Name, tier, segment, history
- **Tone Adaptation**: Apologetic, warm, professional
- **Empathy Scoring**: Quality metrics
- **Multi-Scenario**: Complaints, inquiries, feedback

### ✅ Memory & Learning

- **Persistent History**: JSON-based storage
- **Customer Journeys**: Full interaction tracking
- **Session Management**: Real-time state
- **Export Capability**: Data portability

---

## 🔧 Configuration

### Minimum Required

```ini
# .env file
OPENAI_API_KEY=sk-your-key-here
```

### Advanced Options

```ini
# Model Selection
LLM_MODEL=gpt-4                    # or gpt-3.5-turbo
LLM_TEMPERATURE=0.7                # 0.0-1.0

# Per-Agent Models
CONTEXT_AGENT_MODEL=gpt-4
PATTERN_AGENT_MODEL=gpt-4
DECISION_AGENT_MODEL=gpt-4
EMPATHY_AGENT_MODEL=gpt-4

# Thresholds
HIGH_VALUE_CUSTOMER_THRESHOLD=5000
CHURN_RISK_THRESHOLD=0.7
ESCALATION_URGENCY_THRESHOLD=4

# LangChain Tracing (Optional)
LANGCHAIN_API_KEY=your-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=AgentMAX-CX
```

---

## 🧪 Testing Scenarios

5 built-in scenarios for demos:

1. **`vip_complaint`**
   - VIP customer with major complaint
   - Tests: Escalation, empathy, priority

2. **`loyal_order_delay`**
   - Loyal customer with delayed order
   - Tests: Loyalty handling, urgency

3. **`new_customer_inquiry`**
   - First-time buyer question
   - Tests: Onboarding, information clarity

4. **`high_value_at_risk`**
   - High LTV customer considering churn
   - Tests: Retention, pattern recognition

5. **`positive_feedback`**
   - Happy customer feedback
   - Tests: Appreciation, tone adaptation

---

## 📈 Performance Metrics

The system tracks:

- ⏱️ **Processing Time** - Workflow execution speed
- 🎯 **Confidence Scores** - Decision certainty
- 💙 **Empathy Scores** - Response quality (0-1)
- 🚨 **Escalation Rate** - % requiring human help
- 📊 **Churn Risk** - Prediction accuracy
- 🔄 **Agent Messages** - Full audit trail

---

## 🎓 For Your Team

### First Time Setup

1. Clone the repo (if not already)
2. `cd AgentMAX`
3. Run `bash quickstart.sh` (does everything!)
4. Or follow SETUP.md manually

### Daily Usage

```bash
# Activate environment
source .venv/Scripts/activate

# Run demo
python main.py --mode demo

# Or interactive
python main.py --mode interactive
```

### Customization

- **Change prompts**: Edit `config/prompts.py`
- **Adjust thresholds**: Modify `config/settings.py`
- **Add agents**: Create new file in `agents/`
- **Extend workflows**: Update `workflows/cx_workflow.py`

---

## 🎤 Presentation Tips

### Demo Flow (5 min)

1. **Intro** (30s): "Multi-agent AI for customer experience"
2. **Architecture** (60s): Show the 4-agent diagram
3. **Live Demo** (180s): Run `python main.py --mode demo`
   - Show VIP complaint scenario
   - Highlight personalization
   - Point out escalation logic
4. **Results** (60s): Show metrics & response quality
5. **Tech Stack** (30s): LangGraph, LangChain, OpenAI

### Key Talking Points

✅ **Multi-agent specialization** - Each agent has expertise  
✅ **Real-time personalization** - Not generic responses  
✅ **Intelligent escalation** - Knows when human needed  
✅ **Production-ready** - Error handling, logging, config  
✅ **Extensible** - Easy to add agents/scenarios  

---

## 🏆 Hackathon Strengths

### Innovation
- ✅ Multi-agent architecture
- ✅ LangGraph workflow orchestration
- ✅ Empathy-first design
- ✅ Predictive churn analysis

### Technical Quality
- ✅ Clean, modular code
- ✅ Type hints & docs
- ✅ Error handling
- ✅ Configurable

### User Experience
- ✅ Interactive demos
- ✅ Clear output
- ✅ Easy setup
- ✅ Good documentation

### Completeness
- ✅ Real dataset
- ✅ Multiple scenarios
- ✅ Full workflow
- ✅ Memory system

---

## 🐛 Common Issues & Fixes

### "ModuleNotFoundError"
```bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

### "OpenAI API key not found"
```bash
# Check .env exists
cat .env

# Add key
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### "Dataset not found"
```bash
cp ../AgentMAX_CX_dataset.xlsx data/AgentMAX_CX_dataset_cleaned.xlsx
```

### Rate limit errors
```bash
# Use GPT-3.5 (faster, cheaper)
export LLM_MODEL=gpt-3.5-turbo
python main.py --mode test
```

---

## 📚 Learning Resources

### In This Repo
1. Start: `README.md` - Full documentation
2. Setup: `SETUP.md` - Installation guide
3. Code: `example_simple.py` - Simple example
4. API: `API.md` - Complete reference

### External
- LangGraph: https://langchain-ai.github.io/langgraph/
- LangChain: https://python.langchain.com/
- OpenAI: https://platform.openai.com/docs

---

## ✅ Pre-Demo Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured with API key
- [ ] Dataset in `data/` folder
- [ ] Test run successful: `python main.py --mode test`
- [ ] Demo works: `python main.py --mode demo`
- [ ] Team understands architecture
- [ ] Presentation prepared

---

## 🎯 Success Criteria

**Platform is working when:**

✅ Demo mode runs without errors  
✅ All 5 scenarios complete successfully  
✅ Responses are personalized (not generic)  
✅ Escalation triggers for VIP/urgent cases  
✅ Sentiment detection is accurate  
✅ Churn risk predictions make sense  
✅ Memory persists between runs  

---

## 🌟 What Makes This Special

1. **Not just a chatbot** - It's a coordinated multi-agent system
2. **Real personalization** - Uses customer data meaningfully
3. **Production-ready** - Not a prototype, actual usable code
4. **Empathy-first** - Designed for human connection
5. **Extensible** - Easy to add features/agents
6. **Well-documented** - Anyone can understand & use it

---

## 🚀 Next Steps After Hackathon

### Potential Enhancements
- [ ] Vector database for semantic search
- [ ] Real-time dashboard
- [ ] A/B testing framework
- [ ] Multi-language support
- [ ] Voice integration
- [ ] Advanced ML models
- [ ] Real-time monitoring
- [ ] API endpoints

---

## 📞 Quick Help

**For setup issues:** Check `SETUP.md`  
**For usage questions:** Check `API.md`  
**For quick start:** Run `bash quickstart.sh`  
**For examples:** See `example_simple.py`  
**For demo:** Run `python main.py --mode demo`

---

## 🎉 Final Words

You now have a **complete, production-ready, multi-agent AI platform** for customer experience management.

**It's ready to demo. It's ready to impress. It's ready to win. 🏆**

---

**Team ProCX**  
*Building empathetic AI, one interaction at a time.*

**Built with:** LangGraph • LangChain • OpenAI • Python • ❤️
