# 🚀 ProCX Quick Start Guide

**Last Updated:** October 19, 2025  
**Repository:** ProCX - Multi-Agent AI Customer Experience Platform

This guide contains all commands needed to run the ProCX project including the backend API, frontend dashboard, and alternative UIs.

---

## 📋 Prerequisites

### 1. Python Environment Setup
```bash
# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# On Windows (Git Bash):
source .venv/Scripts/activate

# On Windows (CMD):
.venv\Scripts\activate

# On Linux/Mac:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually:
pip install langchain langchain-community langchain-groq langgraph pandas openpyxl python-dotenv flask flask-cors flask-socketio python-socketio streamlit
```

### 3. Environment Configuration
```bash
# Create .env file in project root
touch .env

# Add your API keys:
# GROQ_API_KEY=your_groq_api_key_here
# LANGCHAIN_API_KEY=your_langchain_api_key_here (optional)
```

---

## 🎯 Running the Project

### **Option 1: Complete Stack (Recommended for Demo)**

Run all three components for the full experience:

#### Terminal 1 - Backend API Server
```bash
# Navigate to project root
cd c:/Users/PiyushYadav/Documents/AgentMax/ProCX

# Activate virtual environment
source .venv/Scripts/activate

# Run Flask + SocketIO backend
python backend_api.py

# Expected Output:
# ✓ ProactiveMonitor initialized
# 🚀 ProCX Backend API Server
# 📡 Starting Flask + SocketIO server...
# 🌐 Dashboard: http://localhost:5000
# 🔌 WebSocket: ws://localhost:5000
```

**Access Backend:**
- API: http://localhost:5000
- Health Check: http://localhost:5000/health
- WebSocket: ws://localhost:5000

#### Terminal 2 - HTML Frontend Dashboard
```bash
# Simply open the HTML file in your browser:
# Method 1: Double-click frontend_demo.html
# Method 2: Right-click → Open with → Your Browser
# Method 3: Use live server extension in VS Code

# Or serve it with Python:
python -m http.server 8000

# Then open: http://localhost:8000/frontend_demo.html
```

**Dashboard Features:**
- Real-time WebSocket updates
- Live Activity feed (shows escalations!)
- At-Risk Customers list
- AI Interventions panel
- Customer details modal
- Health score visualization

#### Terminal 3 - Streamlit Alternative UI (Optional)
```bash
# Navigate to UI directory
cd ui

# Run Streamlit app
streamlit run app.py --server.headless=true

# Or run from project root:
streamlit run ui/app.py --server.headless=true

# Access at: http://localhost:8501
```

---

### **Option 2: Backend Only (For API Testing)**

```bash
# Run backend API server
source .venv/Scripts/activate
python backend_api.py
```

**Test API Endpoints:**
```bash
# Get dashboard statistics
curl http://localhost:5000/api/dashboard/stats

# Get at-risk customers
curl http://localhost:5000/api/customers/at-risk

# Get specific customer
curl http://localhost:5000/api/customers/C100088

# Trigger proactive scan
curl -X POST http://localhost:5000/api/scan
```

---

### **Option 3: Proactive Scheduler (Batch Processing)**

```bash
# Run proactive scheduler for automated monitoring
source .venv/Scripts/activate
python proactive_scheduler.py

# The scheduler will:
# - Monitor 1,000 customers
# - Run health checks every 6 hours
# - Generate interventions for at-risk customers
# - Log all activities
```

---

### **Option 4: Main Application (Interactive CLI)**

```bash
# Run the main ProCX application
source .venv/Scripts/activate
python main.py

# Follow prompts to:
# 1. Enter customer ID (e.g., C100088)
# 2. View customer analysis
# 3. See AI-generated interventions
# 4. Process multiple customers
```

---

## 🧪 Testing & Validation

### Test Backend Integration
```bash
# 1. Start backend
python backend_api.py

# 2. Open frontend_demo.html in browser

# 3. Click "Run Proactive Scan" button

# 4. Watch for:
#    ✅ Connection status turns green
#    ✅ Live Activity shows real-time events
#    ✅ Escalations appear with 🚨 red highlight
#    ✅ Interventions populate with multi-language messages
#    ✅ At-Risk Customers list updates
```

### Test WebSocket Connection
```bash
# Using wscat (install: npm install -g wscat)
wscat -c ws://localhost:5000

# Or use browser console:
# Open frontend_demo.html → F12 → Console
# Look for: "✅ Connected to ProCX Backend"
```

---

## 📊 Project Structure & Entry Points

```
ProCX/
│
├── backend_api.py              # 🔥 Flask + SocketIO Backend (Port 5000)
├── frontend_demo.html          # 🔥 Main Dashboard UI
├── main.py                     # CLI Application
├── proactive_scheduler.py      # Batch Scheduler
│
├── ui/
│   └── app.py                  # Streamlit Alternative UI (Port 8501)
│
├── agents/                     # AI Agent Modules
│   ├── context_agent.py
│   ├── pattern_agent.py
│   ├── decision_agent.py
│   └── empathy_agent.py
│
├── utils/
│   ├── proactive_monitor.py    # Health Scoring Engine
│   ├── proactive_runner.py     # Agent Orchestrator
│   ├── data_analytics.py       # Data Processing
│   └── memory_handler.py       # Conversation Memory
│
└── workflows/
    └── cx_workflow.py          # LangGraph Workflow
```

---

## 🎬 Demo Flow (For Hackathon/Presentation)

### Step 1: Start Backend
```bash
# Terminal 1
source .venv/Scripts/activate
python backend_api.py
```

### Step 2: Open Dashboard
```bash
# Open frontend_demo.html in Chrome/Edge
# Check connection status (green dot)
```

### Step 3: Run Proactive Scan
```bash
# In browser:
# 1. Click "Run Proactive Scan" button
# 2. Watch Live Activity section
# 3. Observe agent processing in real-time
# 4. See escalations appear with 🚨 indicator
# 5. Review AI interventions in multiple languages
```

### Step 4: Explore Features
```bash
# - Click on any at-risk customer → View full profile
# - Review interventions panel → Multi-language messages
# - Check health distribution → Visual analytics
# - Monitor Live Activity → Real-time agent updates
```

---

## 🔧 Troubleshooting

### Backend Won't Start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed (Windows)
taskkill /PID <process_id> /F

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend Won't Connect
```bash
# 1. Verify backend is running
curl http://localhost:5000/health

# 2. Check browser console (F12)
# Look for WebSocket errors

# 3. Try different browser (Chrome recommended)

# 4. Clear browser cache
# Ctrl + Shift + Delete
```

### Missing Dependencies
```bash
# Reinstall all packages
pip install --force-reinstall -r requirements.txt

# Or install specific missing package
pip install flask-socketio
```

### Data Files Not Found
```bash
# Ensure Excel data files exist:
# data/MOCK_DATA.xlsx (or similar Excel files)
# data/memory/*.jsonl

# If missing, contact team for data files
```

---

## 📱 Ports & URLs

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Backend API** | 5000 | http://localhost:5000 | REST API + WebSocket |
| **HTML Dashboard** | N/A | file:///.../frontend_demo.html | Main UI |
| **Streamlit UI** | 8501 | http://localhost:8501 | Alternative UI |
| **Python HTTP Server** | 8000 | http://localhost:8000 | Static file server |

---

## 🎯 Key Features to Demo

### 1. **Real-Time Escalations** ⭐
- When Decision Agent escalates customer to human
- Appears in Live Activity with 🚨 red highlight
- Shows reason, priority, and customer details

### 2. **Multi-Language Support** 🌍
- Interventions in English, Hindi, Tamil, Telugu, Bengali
- Language-specific customer segments
- Culturally appropriate messaging

### 3. **Diverse Customer Segments** 👥
- VIP customers (high value)
- Loyal customers (frequent orders)
- Regular customers (moderate activity)
- Occasional customers (low engagement)

### 4. **AI Agent Workflow** 🤖
- Context Agent: Analyzes customer history
- Pattern Agent: Identifies behavioral patterns
- Decision Agent: Makes escalation decisions
- Empathy Agent: Generates personalized messages

### 5. **Proactive Health Scoring** 📊
- 10-factor health algorithm
- Churn risk prediction
- Automated monitoring
- Intervention recommendations

---

## 📚 Additional Documentation

For more details, see:
- `README.md` - Project overview
- `SCHEDULER_GUIDE.md` - Scheduler configuration
- `FRONTEND_BACKEND_INTEGRATION.md` - Technical integration details
- `DASHBOARD_QUESTIONS_ANSWERED.md` - FAQ
- `docs/` - Comprehensive documentation

---

## 🆘 Support

**Issues?** Check:
1. All dependencies installed (`pip list`)
2. Virtual environment activated
3. Backend running on port 5000
4. Browser console for errors (F12)
5. Terminal output for error messages

**Still stuck?** Review logs and error messages in terminal output.

---

## ✅ Quick Command Reference

```bash
# Complete Setup (First Time)
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt

# Run Backend
python backend_api.py

# Run Frontend
# Open frontend_demo.html in browser

# Run Streamlit
streamlit run ui/app.py

# Run Scheduler
python proactive_scheduler.py

# Run CLI
python main.py

# Test API
curl http://localhost:5000/api/dashboard/stats
curl -X POST http://localhost:5000/api/scan
```

---

**🎉 You're all set! Run the commands above and experience ProCX in action!**
