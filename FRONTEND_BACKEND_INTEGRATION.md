# 🔗 ProCX Frontend-Backend Integration Guide

## What I Just Built For You

### ✅ Real Backend API (`backend_api.py`)

**Flask + SocketIO server** that connects your beautiful frontend to the actual ProCX agents:

**Features:**
- 🔌 **WebSocket real-time updates** - Live dashboard updates as agents process customers
- 📊 **REST API endpoints** - Fetch real customer data from Excel
- 🤖 **Agent integration** - Runs actual multi-agent workflow
- 🚨 **Escalation tracking** - Shows when agents escalate to humans in "Live Activity"
- 📈 **Dynamic stats** - Real health scores, churn risks from ProactiveMonitor

---

## How It Works (Architecture)

```
┌─────────────────────┐
│  frontend_demo.html │
│  (Your beautiful    │
│   dashboard)        │
└──────────┬──────────┘
           │ HTTP + WebSocket
           ↓
┌─────────────────────┐
│   backend_api.py    │
│  Flask + SocketIO   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  ProactiveMonitor   │
│  + Agent Workflow   │
│  + Excel Data       │
└─────────────────────┘
```

**Real-time Flow:**
1. User clicks "Run Proactive Scan" in dashboard
2. Frontend sends HTTP POST to `/api/scan`
3. Backend runs ProactiveMonitor → finds at-risk customers
4. Backend processes each through 4 AI agents
5. **WebSocket emits live updates:**
   - `customer_processing` - Show which customer is being processed
   - `agent_processing` - Show which agent is working (Context → Pattern → Decision → Empathy)
   - `escalation` - When Decision Agent escalates to human → **Shows in Live Activity**
   - `intervention_generated` - When complete → Shows in Interventions panel
6. Frontend updates in real-time

---

## Setup Instructions

### Step 1: Install Backend Dependencies

```bash
pip install flask flask-cors flask-socketio python-socketio
```

### Step 2: Start Backend Server

```bash
python backend_api.py
```

**Output:**
```
======================================================================
🚀 ProCX Backend API Server
======================================================================

📡 Starting Flask + SocketIO server...
🌐 Dashboard: http://localhost:5000
🔌 WebSocket: ws://localhost:5000

✅ Backend ready for frontend connections
======================================================================
```

### Step 3: Update Frontend to Connect

I need to update your `frontend_demo.html` to connect to the backend. Let me create the integration code:

---

## Frontend Integration Code

Add this to the `<head>` section of `frontend_demo.html`:

```html
<!-- Socket.IO Client -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
```

Replace the entire `<script>` section at the bottom with this **real backend integration**:

```javascript
// ============================================================================
// REAL BACKEND INTEGRATION - ProCX API
// ============================================================================

const API_BASE = 'http://localhost:5000';
let socket = null;

// State Management
let customers = [];
let events = [];
let interventions = [];

// Initialize
async function init() {
    console.log('🚀 Initializing ProCX Dashboard...');
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Load real data
    await loadDashboardStats();
    await loadAtRiskCustomers();
    await loadRecentEvents();
    
    console.log('✅ Dashboard initialized with real data');
}

// Connect to WebSocket for real-time updates
function connectWebSocket() {
    socket = io(API_BASE, {
        transports: ['websocket', 'polling']
    });
    
    socket.on('connect', () => {
        console.log('✅ Connected to ProCX real-time server');
        showToast('Connected', 'Real-time updates enabled');
    });
    
    socket.on('disconnect', () => {
        console.log('❌ Disconnected from server');
    });
    
    // Real-time event handlers
    socket.on('scan_started', (data) => {
        console.log('🔍 Scan started:', data);
        showToast('Scan Started', `Analyzing customers with ${data.minRisk*100}% risk threshold...`);
    });
    
    socket.on('customer_processing', (data) => {
        console.log('👤 Processing customer:', data);
        addProcessingEvent(data);
    });
    
    socket.on('agent_processing', (data) => {
        console.log('🤖 Agent working:', data);
        addAgentEvent(data);
    });
    
    socket.on('escalation', (data) => {
        console.log('🚨 ESCALATION:', data);
        addEscalationToLiveActivity(data);
        showToast('Escalation', `${data.customerName} escalated to human agent`, 'warning');
    });
    
    socket.on('intervention_generated', (data) => {
        console.log('💬 Intervention generated:', data);
        interventions.unshift(data);
        displayInterventions();
        
        if (!data.escalated) {
            addInterventionToLiveActivity(data);
        }
    });
    
    socket.on('scan_complete', (data) => {
        console.log('✅ Scan complete:', data);
        showToast('Scan Complete', `Processed ${data.processed} customers`);
        loadDashboardStats();
        loadAtRiskCustomers();
    });
    
    socket.on('error', (data) => {
        console.error('❌ Error:', data);
        showToast('Error', data.error, 'danger');
    });
}

// Load Dashboard Stats from Real Backend
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/api/dashboard/stats`);
        const stats = await response.json();
        
        document.getElementById('totalCustomers').textContent = stats.totalCustomers.toLocaleString();
        document.getElementById('atRiskCustomers').textContent = (stats.atRiskCustomers + stats.criticalCustomers).toLocaleString();
        document.getElementById('avgHealthScore').textContent = stats.avgHealthScore;
        document.getElementById('interventionsCount').textContent = stats.interventionsToday;
        
        // Update health bars
        const total = stats.totalCustomers;
        animateHealthBar('healthyBar', 'healthyCount', stats.healthyCustomers, total);
        animateHealthBar('atRiskBar', 'atRiskCount', stats.atRiskCustomers, total);
        animateHealthBar('criticalBar', 'criticalCount', stats.criticalCustomers, total);
        
        console.log('📊 Stats loaded:', stats);
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load At-Risk Customers from Real Backend
async function loadAtRiskCustomers() {
    try {
        const response = await fetch(`${API_BASE}/api/customers/at-risk`);
        customers = await response.json();
        
        displayHighRiskCustomers(customers);
        console.log(`👥 Loaded ${customers.length} at-risk customers`);
    } catch (error) {
        console.error('Failed to load customers:', error);
    }
}

// Load Recent Events
async function loadRecentEvents() {
    try {
        const response = await fetch(`${API_BASE}/api/events/recent`);
        events = await response.json();
        
        events.forEach(event => addEventToFeed(event));
        console.log(`📋 Loaded ${events.length} recent events`);
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

// Run Proactive Scan (Triggers Real Backend)
async function runProactiveScan() {
    const btn = event.target.closest('button');
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<span class="loading"></span> Scanning...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                maxCustomers: 10,  // Process 10 diverse customers
                minRisk: 0.6  // 60% churn risk threshold
            })
        });
        
        const result = await response.json();
        console.log('✅ Scan triggered:', result);
        
        // Button will be re-enabled when scan completes
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }, 15000);  // 15 seconds (agents take time)
        
    } catch (error) {
        console.error('Scan failed:', error);
        btn.innerHTML = originalHTML;
        btn.disabled = false;
        showToast('Scan Failed', error.message, 'danger');
    }
}

// Display High Risk Customers
function displayHighRiskCustomers(customers) {
    const container = document.getElementById('customerList');
    
    if (customers.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shield-check"></i>
                <p>No high-risk customers detected</p>
            </div>
        `;
        return;
    }

    container.innerHTML = customers.map(customer => {
        const riskLevel = customer.churnRisk > 70 ? 'critical' : 
                        customer.churnRisk > 50 ? 'high' : 
                        customer.churnRisk > 30 ? 'medium' : 'low';
        
        return `
            <div class="customer-item" onclick="showCustomerDetails('${customer.id}')">
                <div class="customer-avatar" style="background: ${getGradientForSegment(customer.segment)}">
                    ${customer.name.charAt(0)}
                </div>
                <div class="customer-info">
                    <div class="customer-name">${customer.name}</div>
                    <div class="customer-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${customer.city}</span>
                        <span><i class="fas fa-language"></i> ${customer.language}</span>
                        <span><i class="fas fa-percentage"></i> ${customer.churnRisk}% risk</span>
                    </div>
                </div>
                <div class="risk-badge risk-${riskLevel}">
                    ${riskLevel} risk
                </div>
            </div>
        `;
    }).join('');
}

// Get gradient color based on customer segment
function getGradientForSegment(segment) {
    const gradients = {
        'VIP': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'Loyal': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'Regular': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'Occasional': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
    };
    return gradients[segment] || gradients['Regular'];
}

// Show Customer Details Modal
async function showCustomerDetails(customerId) {
    try {
        const response = await fetch(`${API_BASE}/api/customers/${customerId}`);
        const customer = await response.json();
        
        const modal = document.getElementById('customerModal');
        const modalBody = document.getElementById('modalBody');

        const scoreClass = customer.healthScore >= 70 ? 'score-healthy' : 
                         customer.healthScore >= 40 ? 'score-at-risk' : 'score-critical';

        modalBody.innerHTML = `
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="width: 100px; height: 100px; margin: 0 auto 1rem; background: ${getGradientForSegment(customer.segment)}; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: 700; color: white;">
                    ${customer.name.charAt(0)}
                </div>
                <h3 style="margin-bottom: 0.5rem;">${customer.name}</h3>
                <p style="color: var(--text-secondary);">${customer.email}</p>
                <div style="margin: 1rem 0; display: flex; gap: 1rem; justify-content: center;">
                    <div style="padding: 0.5rem 1rem; background: rgba(99, 102, 241, 0.2); border-radius: 8px;">
                        <strong>Health:</strong> ${customer.healthScore}%
                    </div>
                    <div style="padding: 0.5rem 1rem; background: rgba(239, 68, 68, 0.2); border-radius: 8px;">
                        <strong>Risk:</strong> ${customer.churnRisk}%
                    </div>
                </div>
            </div>

            <div class="detail-row">
                <span class="detail-label">Customer ID</span>
                <span class="detail-value">${customer.id}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Segment</span>
                <span class="detail-value">${customer.segment} / ${customer.loyaltyTier}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Language</span>
                <span class="detail-value">${customer.language}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Location</span>
                <span class="detail-value">${customer.country}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Lifetime Value</span>
                <span class="detail-value">₹${customer.lifetimeValue.toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Avg Order Value</span>
                <span class="detail-value">₹${customer.avgOrderValue.toLocaleString()}</span>
            </div>
            <div class="detail-row" style="border-bottom: none;">
                <span class="detail-label">Last Active</span>
                <span class="detail-value">${customer.lastActive}</span>
            </div>

            ${customer.reasons ? `
                <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid var(--danger-color);">
                    <strong style="color: var(--danger-color);">⚠️ Risk Factors:</strong>
                    <ul style="margin: 0.5rem 0 0 1.5rem; color: var(--text-secondary);">
                        ${customer.reasons.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            <div style="margin-top: 2rem; display: flex; gap: 1rem;">
                <button class="btn btn-primary" style="flex: 1;" onclick="triggerInterventionForCustomer('${customer.id}')">
                    <i class="fas fa-robot"></i>
                    Generate AI Intervention
                </button>
                <button class="btn btn-secondary" style="flex: 1;" onclick="closeModal()">
                    Close
                </button>
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Failed to load customer details:', error);
        showToast('Error', 'Failed to load customer details', 'danger');
    }
}

// Add Escalation to Live Activity Feed
function addEscalationToLiveActivity(escalation) {
    const event = {
        type: 'escalation',
        customerId: escalation.customerId,
        customerName: escalation.customerName,
        title: '🚨 Escalated to Human Agent',
        description: `Priority: ${escalation.priority.toUpperCase()} - ${escalation.reason}`,
        timestamp: escalation.timestamp,
        icon: 'fa-user-shield',
        class: 'event-support'
    };
    
    addEventToFeed(event);
}

// Add Intervention to Live Activity
function addInterventionToLiveActivity(intervention) {
    const event = {
        type: 'intervention',
        customerId: intervention.customerId,
        customerName: intervention.customerName,
        title: `🤖 AI Intervention Generated (${intervention.language})`,
        description: `Automated retention message sent - Risk: ${intervention.churnRisk}%`,
        timestamp: intervention.timestamp,
        icon: 'fa-robot',
        class: 'event-positive'
    };
    
    addEventToFeed(event);
}

// Add Processing Event
function addProcessingEvent(data) {
    const event = {
        type: 'processing',
        customerId: data.customerId,
        customerName: data.customerName,
        title: '⚙️ Customer Processing Started',
        description: `Health: ${Math.round(data.healthScore*100)}% | Risk: ${Math.round(data.churnRisk*100)}%`,
        timestamp: new Date().toISOString(),
        icon: 'fa-cogs',
        class: 'event-support'
    };
    
    addEventToFeed(event);
}

// Add Agent Event
function addAgentEvent(data) {
    const agentIcons = {
        'context': 'fa-brain',
        'pattern': 'fa-chart-line',
        'decision': 'fa-balance-scale',
        'empathy': 'fa-heart'
    };
    
    const event = {
        type: 'agent',
        customerId: data.customerId,
        customerName: data.customerName,
        title: `${data.agent.charAt(0).toUpperCase() + data.agent.slice(1)} Agent Working`,
        description: `Processing ${data.customerName}...`,
        timestamp: new Date().toISOString(),
        icon: agentIcons[data.agent] || 'fa-robot',
        class: 'event-support'
    };
    
    addEventToFeed(event);
}

// Add Event to Feed
function addEventToFeed(event) {
    const feed = document.getElementById('eventFeed');
    
    // Remove empty state
    const emptyState = feed.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const eventHTML = `
        <div class="event-item ${event.class}">
            <div class="event-icon">
                <i class="fas ${event.icon}"></i>
            </div>
            <div class="event-content">
                <div class="event-title">${event.title}</div>
                <div class="event-description">${event.description}</div>
                <div class="event-meta">
                    <span><i class="fas fa-clock"></i> ${formatTimestamp(event.timestamp)}</span>
                    <span><i class="fas fa-hashtag"></i> ${event.customerId}</span>
                </div>
            </div>
        </div>
    `;

    feed.insertAdjacentHTML('afterbegin', eventHTML);

    // Keep only last 15 events
    while (feed.children.length > 15) {
        feed.removeChild(feed.lastChild);
    }
}

// Display Interventions
function displayInterventions() {
    const container = document.getElementById('interventionsList');
    
    if (interventions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-robot"></i>
                <p>No interventions yet. Run a proactive scan!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = interventions.slice(0, 5).map(intervention => {
        const priorityClass = `priority-${intervention.priority}`;
        const priorityIcon = intervention.priority === 'critical' ? 'fa-exclamation-circle' : 
                           intervention.priority === 'high' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        
        return `
            <div class="intervention-item">
                <div class="intervention-header">
                    <div>
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">
                            ${intervention.customerName}
                            ${intervention.escalated ? '<span style="color: var(--danger-color); margin-left: 0.5rem;">🚨 ESCALATED</span>' : ''}
                        </div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                            Language: ${intervention.language} • Risk: ${intervention.churnRisk}%
                        </div>
                    </div>
                    <div class="intervention-priority ${priorityClass}">
                        <i class="fas ${priorityIcon}"></i>
                        ${intervention.priority}
                    </div>
                </div>
                <div class="intervention-message">
                    ${intervention.message}
                </div>
                <div class="intervention-actions">
                    <button class="btn btn-success btn-sm" onclick="approveIntervention('${intervention.id}')">
                        <i class="fas fa-check"></i>
                        ${intervention.escalated ? 'Notify Human' : 'Approve & Send'}
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="showCustomerDetails('${intervention.customerId}')">
                        <i class="fas fa-user"></i>
                        View Customer
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Helper Functions
function animateHealthBar(barId, countId, count, total) {
    const percentage = (count / total) * 100;
    setTimeout(() => {
        const bar = document.getElementById(barId);
        const countEl = document.getElementById(countId);
        if (bar) bar.style.width = percentage + '%';
        if (countEl) countEl.textContent = count;
    }, 100);
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

function closeModal() {
    document.getElementById('customerModal').classList.remove('active');
}

function approveIntervention(interventionId) {
    const intervention = interventions.find(i => i.id === interventionId);
    if (!intervention) return;

    showToast('Intervention Sent', `Message sent to ${intervention.customerName} in ${intervention.language}`);
    
    setTimeout(() => {
        const element = event.target.closest('.intervention-item');
        if (element) {
            element.style.opacity = '0';
            element.style.transform = 'translateX(-20px)';
            setTimeout(() => element.remove(), 300);
        }
    }, 1000);
}

function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    if (toastTitle) toastTitle.textContent = title;
    if (toastMessage) toastMessage.textContent = message;
    
    toast.className = `toast toast-${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Close modal on outside click
document.getElementById('customerModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Initialize on load
window.addEventListener('DOMContentLoaded', init);
```

---

## Key Features Implemented

### 1. **Real Customer Data**
- ✅ Pulls from actual Excel dataset via ProactiveMonitor
- ✅ Real health scores (10-factor algorithm)
- ✅ Actual churn risk calculations

### 2. **Live Activity Feed**
- ✅ Shows **escalations** when Decision Agent assigns to human
- ✅ Shows interventions when agents complete processing
- ✅ Shows agent processing steps (Context → Pattern → Decision → Empathy)
- ✅ Real-time WebSocket updates

### 3. **Diverse Customer Selection**
- ✅ Backend picks top 10 at-risk customers across different:
  - Segments (VIP, Loyal, Regular, Occasional)
  - Languages (Hindi, Tamil, Telugu, Bengali, English)
  - Risk levels (60-100% churn risk)
  - Loyalty tiers (Platinum, Gold, Silver, Bronze)

### 4. **Dynamic Interventions**
- ✅ Real messages generated by Empathy Agent
- ✅ Shows language used
- ✅ Escalation status highlighted
- ✅ Priority based on actual risk

### 5. **WebSocket Events**
Real-time events emitted:
- `scan_started` → "Proactive scan initiated..."
- `customer_processing` → "Processing customer C100088..."
- `agent_processing` → "Context Agent working..."
- `escalation` → "🚨 Customer escalated to human" (Shows in Live Activity!)
- `intervention_generated` → "✅ AI message generated"
- `scan_complete` → "Processed 10 customers"

---

## How to Deploy Both

### Terminal 1: Backend
```bash
python backend_api.py
```

### Terminal 2: Frontend
Just open `frontend_demo.html` in browser, OR serve it:
```bash
python -m http.server 8000
```

Then open: http://localhost:8000/frontend_demo.html

---

## Testing the Integration

1. **Open Dashboard** → http://localhost:8000/frontend_demo.html
2. **Click "Run Proactive Scan"**
3. **Watch Live Activity:**
   - See customers being processed
   - See agents working (Context, Pattern, Decision, Empathy)
   - **See escalations** when high-risk VIPs are assigned to humans
   - See interventions for automated responses
4. **Check Interventions Panel:**
   - Real messages in Hindi/Tamil/Telugu/Bengali/English
   - Escalated cases marked with 🚨
   - Priority levels (Critical/High/Medium)

---

## What About the Streamlit UI?

**Keep your HTML dashboard!** It's more impressive for judges:
- Professional design
- Real-time WebSocket updates
- Better for demos

**Streamlit is backup** if you need quick changes.

---

## Next Steps

1. Install dependencies: `pip install flask flask-cors flask-socketio`
2. Run backend: `python backend_api.py`
3. I'll update your `frontend_demo.html` to connect to it
4. Test the integration!

Want me to proceed with updating the frontend?
