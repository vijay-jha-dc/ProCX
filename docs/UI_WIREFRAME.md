# ProCX Web UI Wireframe & Flow

**Created for AgentMAX Hackathon 2025**

---

## **OVERVIEW**

**Technology Stack:**

- **Backend:** FastAPI (Python) - reuse existing ProCX agents
- **Frontend:** React/HTML+Tailwind CSS
- **Real-time:** WebSocket for live updates
- **Demo Duration:** 3-5 minutes (judges attention span)

---

## **PAGE 1: DASHBOARD (Home)**

### **Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  🏠 ProCX Dashboard              [Language: EN] [Profile]  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 CUSTOMER HEALTH OVERVIEW                   [Refresh 🔄] │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ 🔴 CRITICAL  │ 🟠 HIGH RISK │ 🟡 MEDIUM    │ 🟢 LOW   │ │
│  │     24       │      84      │     156      │    736   │ │
│  │   (2.4%)     │    (8.4%)    │   (15.6%)    │  (73.6%) │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
│                                                             │
│  🚨 TOP 10 AT-RISK CUSTOMERS                                │
│  ┌─────────────────────────────────────────────────────────┤
│  │ #1  Tanya Kumar (C100924)                    Risk: 84.2%│
│  │     VIP | Electronics | LTV: ₹1,016 | Tamil             │
│  │     [View Details] [Trigger Intervention]              │
│  ├─────────────────────────────────────────────────────────┤
│  │ #2  Riya Reddy (C100336)                     Risk: 82.9%│
│  │     Occasional | Beauty | LTV: ₹1,119 | Telugu          │
│  │     [View Details] [Trigger Intervention]              │
│  ├─────────────────────────────────────────────────────────┤
│  │ #3  Rajesh Malhotra (C100567)                Risk: 81.5%│
│  │     VIP | Electronics | LTV: ₹8,500 | Hindi  🚨 ESCALATED│
│  │     [View Details] [Assigned to: Senior Agent]         │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  [🔍 View All At-Risk Customers]  [▶ Start Batch Scan]     │
└────────────────────────────────────────────────────────────┘
```

### **Key Features:**

- Real-time health score updates
- Color-coded risk levels
- Quick action buttons
- Escalation status indicators

---

## **PAGE 2: CUSTOMER DETAIL VIEW**

### **Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                  Customer: Tanya Kumar│
├────────────────────────────────────────────────────────────┤
│                                                             │
│  👤 CUSTOMER PROFILE                                        │
│  ┌─────────────────────┬─────────────────────────────────┐ │
│  │ Name: Tanya Kumar   │ Health Score: 25.7% 🔴          │ │
│  │ ID: C100924         │ Churn Risk: 84.2% 🚨            │ │
│  │ Segment: Occasional │ Sentiment: very_negative        │ │
│  │ Tier: Bronze        │ Urgency: 5/5 ⚡⚡⚡⚡⚡           │ │
│  │ LTV: ₹1,016         │ Language: Tamil (தமிழ்)          │ │
│  │ Category: Electronics│ Last Active: 45 days ago       │ │
│  └─────────────────────┴─────────────────────────────────┘ │
│                                                             │
│  📈 RISK FACTORS (10-Factor Analysis)                       │
│  ┌─────────────────────────────────────────────────────────┤
│  │ ⚠️ Segment Score: 15% (Occasional)                      │
│  │ ⚠️ Activity Recency: 10% (45 days inactive)             │
│  │ ⚠️ Order Frequency: 20% (Declining trend)               │
│  │ ✅ LTV Percentile: 45% (Average)                        │
│  │ ⚠️ Support History: 3 tickets, Avg CSAT: 2.8/5.0       │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  🤖 AI AGENT ANALYSIS (Last Run: 2 min ago)                 │
│  ┌─────────────────────────────────────────────────────────┤
│  │ Bodha (Context): "Customer shows declining engagement   │
│  │   with negative sentiment. Recent support interaction   │
│  │   indicates frustration with delivery delays."          │
│  │                                                          │
│  │ Dhyana (Pattern): "Similar customers churned after      │
│  │   40+ days inactivity. Electronics segment sensitive."  │
│  │                                                          │
│  │ Niti (Decision): "Recommend immediate retention offer   │
│  │   via WhatsApp. No escalation needed (not VIP)."        │
│  │                                                          │
│  │ Karuna (Empathy): "Generated Tamil message with Diwali  │
│  │   greeting and personalized electronics discount."      │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  💬 PERSONALIZED MESSAGE (Tamil)                            │
│  ┌─────────────────────────────────────────────────────────┤
│  │ தீபாவளி வாழ்த்துக்கள்! இந்த விளக்கு திருநாள் உங்கள்    │
│  │ வாழ்வில் மகிழ்ச்சியை கொண்டு வரட்டும். Tanya, we      │
│  │ understand how important it is for you to have...       │
│  │                                                          │
│  │ Channel: WhatsApp ✅ | Timing: Within 2 hours           │
│  │ Empathy Score: 95% | Festival Context: Diwali 2025      │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  [📤 Send Intervention] [🚨 Escalate to Human] [💾 Save]   │
└────────────────────────────────────────────────────────────┘
```

---

## **PAGE 3: REAL-TIME EVENT MONITOR**

### **Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  🔴 LIVE EVENT STREAM                    [Auto-refresh: ON]│
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ⚡ RECENT EVENTS (Last 10 minutes)                         │
│  ┌─────────────────────────────────────────────────────────┤
│  │ 🔴 11:03:45 AM - PAYMENT FAILURE                        │
│  │    Customer: Tanya Kumar (C100924)                      │
│  │    Reason: Card expired | Amount: ₹2,499                │
│  │    Status: ✅ INTERVENTION SENT (26 seconds)            │
│  │    [View Details]                                       │
│  ├─────────────────────────────────────────────────────────┤
│  │ 🟡 11:01:22 AM - LOW NPS SCORE                          │
│  │    Customer: Amit Sharma (C100234)                      │
│  │    Score: 3/10 (Detractor) | Reason: Delivery delay     │
│  │    Status: 🔄 PROCESSING...                             │
│  │    [View Details]                                       │
│  ├─────────────────────────────────────────────────────────┤
│  │ 🟠 10:58:11 AM - SUPPORT TICKET #5 (Same Customer)      │
│  │    Customer: Priya Nair (C100445)                       │
│  │    Issue: Product quality | CSAT: 1.5/5.0               │
│  │    Status: 🚨 ESCALATED TO HUMAN                        │
│  │    Assigned: Senior Agent (Ram Kumar)                   │
│  │    [View Details]                                       │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  📊 EVENT METRICS (Today)                                   │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ Total Events │ Automated    │ Escalated    │ Avg Time │ │
│  │      47      │      42      │       5      │  28 sec  │ │
│  │              │   (89.4%)    │   (10.6%)    │          │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
│                                                             │
│  [🔔 Configure Alerts] [📥 Export Log] [⏸️ Pause Monitoring]│
└────────────────────────────────────────────────────────────┘
```

### **Key Features:**

- WebSocket real-time updates
- Event timeline with status
- Quick filtering by event type
- Auto-scroll to latest events

---

## **PAGE 4: BATCH PROCESSING MONITOR**

### **Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ BATCH SCAN IN PROGRESS...                    [Cancel ⏹]│
├────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 SCAN PROGRESS                                           │
│  ┌─────────────────────────────────────────────────────────┤
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░  60% (3/5 customers processed)     │
│  │                                                          │
│  │ Elapsed: 1m 23s | Estimated: 42s remaining              │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  ✅ COMPLETED INTERVENTIONS                                 │
│  ┌─────────────────────────────────────────────────────────┤
│  │ ✅ Customer #1: Tanya Kumar (C100924)                   │
│  │    Risk: 84.2% | Action: Retention offer sent (Tamil)   │
│  │    Time: 26 seconds | Status: Automated ✅              │
│  │    [View Message]                                       │
│  ├─────────────────────────────────────────────────────────┤
│  │ ✅ Customer #2: Rajesh Malhotra (C100567)               │
│  │    Risk: 88.0% | Action: ESCALATED TO HUMAN 🚨          │
│  │    Time: 31 seconds | Assigned: Senior Agent            │
│  │    [View Details]                                       │
│  ├─────────────────────────────────────────────────────────┤
│  │ ✅ Customer #3: Riya Reddy (C100336)                    │
│  │    Risk: 82.9% | Action: Retention offer sent (Telugu)  │
│  │    Time: 29 seconds | Status: Automated ✅              │
│  │    [View Message]                                       │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  🔄 CURRENTLY PROCESSING                                    │
│  ┌─────────────────────────────────────────────────────────┤
│  │ ⏳ Customer #4: Amit Sharma (C100234)                   │
│  │    Agent Pipeline:                                      │
│  │    ✅ Bodha (Context) → ✅ Dhyana (Pattern) →           │
│  │    🔄 Niti (Decision) → ⏸️ Karuna (Empathy)            │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  [📊 View Summary Report] [💾 Export Results]               │
└────────────────────────────────────────────────────────────┘
```

### **Key Features:**

- Live progress bar
- Agent pipeline visualization
- Escalation highlighting
- Multi-language message preview

---

## **PAGE 5: ESCALATION MANAGEMENT**

### **Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  🚨 ESCALATION QUEUE                      [Assign All] [⚙️] │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  🔴 ACTIVE ESCALATIONS (5)                                  │
│  ┌─────────────────────────────────────────────────────────┤
│  │ #ESC001 - Rajesh Malhotra (C100567)    Priority: CRITICAL│
│  │ ┌───────────────────────────────────────────────────────┤
│  │ │ VIP | ₹8,500 LTV | Risk: 88% | Hindi                 │
│  │ │ Triggers: VIP + High Risk + Low CSAT (2.1/5.0)        │
│  │ │ Created: 10 min ago | SLA: 1h 50m remaining          │
│  │ │                                                        │
│  │ │ 🤖 AI Recommendation:                                 │
│  │ │ "Immediate phone call. Offer personalized retention   │
│  │ │  package with ₹1,500 discount. Address electronics    │
│  │ │  delivery delays mentioned in support tickets."       │
│  │ │                                                        │
│  │ │ 💬 Pre-drafted Message (Hindi):                       │
│  │ │ "दीपावली की शुभकामनाएं, राजेश! यह प्रकाश का..."     │
│  │ │                                                        │
│  │ │ Assigned to: [Select Agent ▼] [Auto-assign]          │
│  │ │ [✅ Accept] [➕ Add Notes] [📞 Call Customer]         │
│  │ └───────────────────────────────────────────────────────┘
│  ├─────────────────────────────────────────────────────────┤
│  │ #ESC002 - Priya Nair (C100445)         Priority: HIGH   │
│  │ ┌───────────────────────────────────────────────────────┤
│  │ │ Regular | ₹3,200 LTV | 5 support tickets in 30 days  │
│  │ │ Triggers: Repeated complaints + Low CSAT              │
│  │ │ Created: 23 min ago | Assigned: Ram Kumar             │
│  │ │ [View Details]                                        │
│  │ └───────────────────────────────────────────────────────┘
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  ✅ RESOLVED ESCALATIONS (Today: 12)                        │
│  [View History]                                             │
│                                                             │
│  📊 ESCALATION METRICS                                      │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ Active: 5    │ Avg Response │ Resolution   │ Success  │ │
│  │ Pending: 2   │   18 min     │   2.3 hours  │   94%    │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## **UI FLOW DIAGRAM**

```
START
  ↓
┌─────────────────┐
│  1. DASHBOARD   │ ← Main landing page
│  (Health View)  │
└────────┬────────┘
         │
    ┌────┴────┬────────────┬─────────────┐
    ↓         ↓            ↓             ↓
┌────────┐ ┌──────┐ ┌────────────┐ ┌──────────┐
│Customer│ │Batch │ │Real-time   │ │Escalation│
│Details │ │Scan  │ │Events      │ │Queue     │
│(Page 2)│ │(P4)  │ │(Page 3)    │ │(Page 5)  │
└────────┘ └──────┘ └────────────┘ └──────────┘
    ↓         ↓            ↓             ↓
    │    ┌────┴────┐       │        ┌────┴────┐
    │    │ Monitor │       │        │ Assign  │
    │    │Progress │       │        │to Agent │
    │    └─────────┘       │        └─────────┘
    │         ↓            │             ↓
    └─────────┴────────────┴─────────────┘
              ↓
       [Intervention Sent / Escalated]
```

---

## **API ENDPOINTS NEEDED**

```python
# FastAPI Backend

# 1. Dashboard
GET  /api/dashboard/health-overview
GET  /api/dashboard/top-at-risk?limit=10

# 2. Customer Details
GET  /api/customer/{customer_id}
GET  /api/customer/{customer_id}/agent-analysis
POST /api/customer/{customer_id}/trigger-intervention

# 3. Real-time Events
WS   /api/events/stream                    # WebSocket
GET  /api/events/recent?minutes=10
POST /api/events/configure-alerts

# 4. Batch Processing
POST /api/batch/start?max_customers=5
GET  /api/batch/status/{batch_id}
GET  /api/batch/results/{batch_id}

# 5. Escalations
GET  /api/escalations/active
POST /api/escalations/{escalation_id}/assign
POST /api/escalations/{escalation_id}/resolve
GET  /api/escalations/metrics
```

---

## **DEMO FLOW (3 MINUTES)**

### **Part 1: Dashboard (30 sec)**

1. Open UI → Show health overview
2. Point to "24 critical customers"
3. Scroll top 10 at-risk list
4. Highlight Tanya Kumar (84.2% risk, Tamil)

### **Part 2: Real-time Event (1 min)**

5. Click "Real-time Events" tab
6. Simulate payment failure (backend trigger)
7. Watch event appear in stream
8. Show "INTERVENTION SENT - 26 seconds"
9. Click "View Details" → Show Tamil message

### **Part 3: Batch Processing (1 min)**

10. Click "Start Batch Scan" button
11. Watch progress bar (60% → 100%)
12. See 3 customers processed
13. Highlight Customer #2: "🚨 ESCALATED"

### **Part 4: Escalation (30 sec)**

14. Click "Escalation Queue" tab
15. Show Rajesh Malhotra (#ESC001)
16. Point to 3 triggers: VIP + Risk + CSAT
17. Show Hindi pre-drafted message
18. Click "Assign to Senior Agent"

---

## **TECHNOLOGY CHOICES**

### **Option A: Simple (1 day) - RECOMMENDED FOR HACKATHON**

- **Frontend:** Single HTML + Tailwind CSS + Alpine.js (or vanilla JS)
- **Backend:** FastAPI with existing ProCX code
- **Real-time:** Server-Sent Events (simpler than WebSocket)
- **Database:** JSON files (already have)

### **Option B: Full Stack (3+ days)**

- **Frontend:** React + TypeScript
- **Backend:** FastAPI
- **Real-time:** WebSocket
- **Database:** PostgreSQL

**RECOMMENDATION: Use Option A - judges care about DEMO, not tech stack complexity!**

---

## **IMPLEMENTATION PRIORITY (For Tomorrow)**

**CRITICAL (Must Have):**

1. ✅ Page 1: Dashboard with health overview
2. ✅ Page 2: Customer detail view
3. ✅ Page 5: Escalation queue with Rajesh

**NICE TO HAVE (If Time):** 4. ⚠️ Page 3: Real-time event stream 5. ⚠️ Page 4: Batch processing monitor

**SKIP (Not Worth Time):**

- ❌ User authentication
- ❌ Advanced filtering/search
- ❌ Mobile responsive (judges use laptops)
- ❌ Charts/graphs (too much time)

---

## **FILE STRUCTURE**

```
ProCX/
├── backend/
│   ├── api.py              # FastAPI app
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── customers.py
│   │   ├── events.py
│   │   └── escalations.py
│   └── main.py             # Reuse existing ProCX class
│
├── frontend/
│   ├── index.html          # Single page app
│   ├── styles.css          # Tailwind or custom
│   └── app.js              # Vanilla JS or Alpine.js
│
└── requirements-ui.txt     # fastapi, uvicorn, jinja2
```

---

## **QUICK START GUIDE (Tomorrow)**

```bash
# 1. Create FastAPI backend (30 min)
cd backend/
python api.py

# 2. Create HTML frontend (1 hour)
cd frontend/
# Open index.html in browser

# 3. Connect frontend to backend (30 min)
# Add fetch() calls in app.js

# 4. Test demo flow (30 min)
# Run through 4-page demo

# TOTAL: 2.5 hours for basic working UI
```

---

## **QUESTIONS TO DECIDE:**

1. **How much time tomorrow?** (2 hours → Simple HTML | 6+ hours → React)
2. **Is UI mandatory for hackathon?** (CLI demo might be enough!)
3. **Priority:** Perfect CLI demo OR basic UI demo?

**MY BRUTAL RECOMMENDATION:** If you have < 4 hours tomorrow, SKIP UI. Polish your CLI demos instead. Judges score presentation + demo execution higher than UI prettiness! 🎯

---

**READY TO BUILD TOMORROW?** Let me know your time budget! ⏰
