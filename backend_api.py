"""
ProCX Backend API - Connects frontend to agents
Real-time WebSocket server for live dashboard updates
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))

from utils import ProactiveMonitor
from workflows import create_cx_workflow, run_workflow
from models import AgentState, CustomerEvent, EventType, Customer
from config import settings
import pandas as pd

app = Flask(__name__, static_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
active_connections = 0
processing_queue = []
recent_interventions = []
recent_events = []
customer_cache = {}

# Initialize ProactiveMonitor
monitor = ProactiveMonitor()

@app.route('/')
def index():
    """Serve the frontend dashboard"""
    return send_from_directory('.', 'frontend_demo.html')

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    customers_df = monitor.customers_df
    
    # Calculate health distribution
    health_scores = []
    for idx, row in customers_df.iterrows():
        health = monitor._calculate_customer_health(row)
        health_scores.append(health['health_score'])
    
    healthy = sum(1 for h in health_scores if h >= 0.7)
    at_risk = sum(1 for h in health_scores if 0.4 <= h < 0.7)
    critical = sum(1 for h in health_scores if h < 0.4)
    
    return jsonify({
        'totalCustomers': len(customers_df),
        'healthyCustomers': healthy,
        'atRiskCustomers': at_risk,
        'criticalCustomers': critical,
        'avgHealthScore': int(sum(health_scores) / len(health_scores) * 100),
        'interventionsToday': len(recent_interventions),
        'activeAgents': 4,
        'systemStatus': 'online'
    })

@app.route('/api/customers/at-risk')
def get_at_risk_customers():
    """Get customers requiring immediate attention"""
    alerts = monitor.detect_churn_risks(
        min_churn_risk=0.6,
        min_lifetime_value=1000.0
    )
    
    at_risk_list = []
    for alert in alerts[:20]:  # Top 20
        customer = alert['customer']
        at_risk_list.append({
            'id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'email': customer.email,
            'segment': customer.segment,
            'loyaltyTier': customer.loyalty_tier,
            'healthScore': int(alert['health_score'] * 100),
            'churnRisk': int(alert['churn_risk'] * 100),
            'lifetimeValue': customer.lifetime_value,
            'language': customer.language or 'English',
            'city': customer.country or 'Unknown',
            'status': alert['risk_level'].lower(),
            'reasons': alert['reasons'][:3]
        })
    
    return jsonify(at_risk_list)

@app.route('/api/customers/<customer_id>')
def get_customer_details(customer_id):
    """Get detailed customer information"""
    customers_df = monitor.customers_df
    customer_row = customers_df[customers_df['customer_id'] == customer_id]
    
    if customer_row.empty:
        return jsonify({'error': 'Customer not found'}), 404
    
    row = customer_row.iloc[0]
    customer = Customer.from_dataframe(row)
    health = monitor._calculate_customer_health(row)
    
    return jsonify({
        'id': customer.customer_id,
        'name': f"{customer.first_name} {customer.last_name}",
        'email': customer.email,
        'segment': customer.segment,
        'loyaltyTier': customer.loyalty_tier,
        'healthScore': int(health['health_score'] * 100),
        'churnRisk': int(health['churn_risk'] * 100),
        'lifetimeValue': customer.lifetime_value,
        'avgOrderValue': customer.avg_order_value or 0,
        'totalOrders': getattr(customer, 'total_orders', 0),
        'language': customer.language or 'English',
        'country': customer.country or 'Unknown',
        'lastActive': customer.last_active_date or 'Unknown',
        'reasons': health['reasons']
    })

@app.route('/api/scan', methods=['POST'])
def trigger_proactive_scan():
    """Trigger a proactive scan and process customers through agents"""
    data = request.json or {}
    max_customers = data.get('maxCustomers', 5)
    min_risk = data.get('minRisk', 0.7)
    
    # Run scan in background thread
    thread = threading.Thread(
        target=run_proactive_scan_background,
        args=(max_customers, min_risk)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': f'Proactive scan initiated for {max_customers} customers'
    })

def run_proactive_scan_background(max_customers, min_risk):
    """Background task to run proactive scan and emit real-time updates"""
    global recent_interventions, recent_events
    
    # Emit scan started
    socketio.emit('scan_started', {
        'timestamp': datetime.now().isoformat(),
        'maxCustomers': max_customers,
        'minRisk': min_risk
    })
    
    # Detect at-risk customers
    alerts = monitor.detect_churn_risks(
        min_churn_risk=min_risk,
        min_lifetime_value=1000.0
    )
    
    socketio.emit('scan_progress', {
        'message': f'Found {len(alerts)} at-risk customers',
        'count': len(alerts)
    })
    
    # Process top N customers through agent workflow
    workflow = create_cx_workflow()
    processed = 0
    
    for alert in alerts[:max_customers]:
        customer = alert['customer']
        
        # Emit processing start
        socketio.emit('customer_processing', {
            'customerId': customer.customer_id,
            'customerName': f"{customer.first_name} {customer.last_name}",
            'churnRisk': alert['churn_risk'],
            'healthScore': alert['health_score']
        })
        
        # Create proactive event
        event = _create_proactive_event(customer, alert)
        
        # Run through agent workflow
        try:
            initial_state = AgentState(
                event=event,
                messages=[],
                analysis={},
                next_action=None
            )
            
            # Emit each agent step
            result = run_workflow_with_updates(workflow, initial_state, customer)
            
            # Check if escalated
            if result.get('next_action') == 'escalate_to_human':
                # Emit escalation event
                socketio.emit('escalation', {
                    'customerId': customer.customer_id,
                    'customerName': f"{customer.first_name} {customer.last_name}",
                    'reason': result.get('escalation_reason', 'High priority case'),
                    'timestamp': datetime.now().isoformat(),
                    'priority': 'critical' if alert['churn_risk'] > 0.8 else 'high'
                })
                
                recent_events.append({
                    'type': 'escalation',
                    'customerId': customer.customer_id,
                    'customerName': f"{customer.first_name} {customer.last_name}",
                    'title': 'Escalated to Human Agent',
                    'description': result.get('escalation_reason', 'High priority case'),
                    'timestamp': datetime.now().isoformat(),
                    'icon': 'fa-user-shield',
                    'class': 'event-support'
                })
            
            # Emit intervention generated
            intervention = {
                'id': f"INT_{customer.customer_id}_{int(time.time())}",
                'customerId': customer.customer_id,
                'customerName': f"{customer.first_name} {customer.last_name}",
                'language': customer.language or 'English',
                'message': result.get('response', 'Intervention generated'),
                'priority': 'critical' if alert['churn_risk'] > 0.8 else 'high',
                'churnRisk': int(alert['churn_risk'] * 100),
                'healthScore': int(alert['health_score'] * 100),
                'timestamp': datetime.now().isoformat(),
                'escalated': result.get('next_action') == 'escalate_to_human'
            }
            
            recent_interventions.append(intervention)
            socketio.emit('intervention_generated', intervention)
            
            processed += 1
            time.sleep(1)  # Delay for visual effect
            
        except Exception as e:
            socketio.emit('error', {
                'customerId': customer.customer_id,
                'error': str(e)
            })
    
    # Emit scan complete
    socketio.emit('scan_complete', {
        'timestamp': datetime.now().isoformat(),
        'processed': processed,
        'total': len(alerts)
    })

def run_workflow_with_updates(workflow, initial_state, customer):
    """Run workflow and emit updates for each agent step"""
    agents = ['context', 'pattern', 'decision', 'empathy']
    
    for agent in agents:
        socketio.emit('agent_processing', {
            'agent': agent,
            'customerId': customer.customer_id,
            'customerName': f"{customer.first_name} {customer.last_name}"
        })
        time.sleep(0.5)  # Visual delay
    
    # Actually run workflow
    result = run_workflow(workflow, initial_state.event)
    return result

def _create_proactive_event(customer, alert):
    """Create proactive event from customer and alert"""
    from datetime import datetime
    import time
    
    event_id = f"PROACTIVE_{customer.customer_id}_{int(time.time())}"
    
    # Get specific issue
    reasons = alert['reasons']
    main_issue = reasons[0] if reasons else "At risk of churn"
    
    description = f"""Proactive Outreach: Customer at risk of churn

DETECTED ISSUES:
• {main_issue}
• Health Score: {alert['health_score']*100:.1f}%
• Churn Risk: {alert['churn_risk']*100:.1f}%
• Lifetime Value: ${customer.lifetime_value:,.2f}

PROACTIVE GOAL: Re-engage before they leave
"""
    
    return CustomerEvent(
        event_id=event_id,
        customer=customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description=description,
        metadata={
            'is_proactive': True,
            'health_score': alert['health_score'],
            'churn_risk': alert['churn_risk'],
            'risk_level': alert['risk_level'],
            'reasons': reasons
        }
    )

@app.route('/api/interventions/recent')
def get_recent_interventions():
    """Get recent interventions"""
    return jsonify(recent_interventions[-10:])

@app.route('/api/events/recent')
def get_recent_events():
    """Get recent events for live activity feed"""
    return jsonify(recent_events[-10:])

@socketio.on('connect')
def handle_connect():
    global active_connections
    active_connections += 1
    emit('connection_established', {
        'message': 'Connected to ProCX real-time server',
        'activeConnections': active_connections
    })

@socketio.on('disconnect')
def handle_disconnect():
    global active_connections
    active_connections -= 1

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ProCX Backend API Server")
    print("=" * 70)
    print("\n📡 Starting Flask + SocketIO server...")
    print(f"🌐 Dashboard: http://localhost:5000")
    print(f"🔌 WebSocket: ws://localhost:5000")
    print("\n✅ Backend ready for frontend connections")
    print("=" * 70)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
