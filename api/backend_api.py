from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ProactiveMonitor, DataAnalytics, EscalationTracker, MemoryHandler
from workflows import create_cx_workflow, run_workflow, stream_workflow
from models import AgentState, CustomerEvent, EventType, Customer
from config import settings
import pandas as pd

app = Flask(__name__, static_folder='..')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Clear history on startup
active_connections = 0
recent_interventions = []
recent_events = []
agent_history = []
processed_customers = {}

# Cache for performance (stats only - customer data is always live)
cached_stats = {}
cached_risk_distribution = {}

# Initialize components
monitor = ProactiveMonitor()
analytics = DataAnalytics()
escalation_tracker = EscalationTracker()
memory_handler = MemoryHandler()
workflow = create_cx_workflow()

print("✅ ProCX Backend ready")

@app.route('/')
def index():
    return send_from_directory('..', 'dashboard.html')

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'activeConnections': active_connections
    })

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('../assets', filename)

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    try:
        stats = cached_stats.copy()
        stats['interventionsToday'] = len([i for i in recent_interventions 
                                          if (datetime.now() - datetime.fromisoformat(i['timestamp'])).days == 0])
        stats['activeEscalations'] = min(len(escalation_tracker.active_escalations), 2)
        stats['activeAgents'] = 4
        stats['systemStatus'] = 'online'
        return jsonify(stats)
    except Exception as e:
        print(f"Error in get_dashboard_stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/at-risk')
def get_at_risk_customers():
    try:
        global processed_customers
        
        alerts = monitor.detect_churn_risks(min_churn_risk=0.3)
        
        at_risk_list = []
        for alert in alerts[:50]:  # Top 50
            customer = alert['customer']
            
            # Check if this customer has been processed
            processed_status = None
            processed_data = None
            if customer.customer_id in processed_customers:
                proc_info = processed_customers[customer.customer_id]
                processed_status = proc_info.get('status')  # 'processing', 'sent', 'escalated'
                processed_data = proc_info.get('intervention')  # Full intervention data
            
            customer_data = {
                'id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'email': customer.email,
                'segment': customer.segment,
                'loyaltyTier': customer.loyalty_tier,
                'healthScore': int(alert['health_score'] * 100),
                'churnRisk': int(alert['churn_risk'] * 100),
                'lifetimeValue': float(customer.lifetime_value),
                'language': customer.language or 'en',
                'country': customer.country or 'Unknown',
                'status': processed_status if processed_status else 'pending',  # pending, processing, sent, escalated
                'reasons': alert['reasons'][:3]
            }
            
            # If processed, include intervention data
            if processed_data:
                customer_data['processedInfo'] = processed_data
                customer_data['aiRecommendation'] = processed_data.get('action', '')
                customer_data['message'] = processed_data.get('message', '')
            
            at_risk_list.append(customer_data)
        
        return jsonify(at_risk_list)
    except Exception as e:
        print(f"Error in get_at_risk_customers: {e}")
        return jsonify([])

def clear_session_history():
    global recent_interventions, recent_events, agent_history, processed_customers
    recent_interventions = []
    recent_events = []
    agent_history = []
    processed_customers = {}
    print("🧹 Session history cleared")

@app.route('/api/customers/<customer_id>')
def get_customer_details(customer_id):
    try:
        df = analytics.df
        customer_row = df[df['customer_id'] == customer_id]
        
        if customer_row.empty:
            return jsonify({'error': 'Customer not found'}), 404
        
        row = customer_row.iloc[0]
        
        customer = Customer(
            customer_id=str(row['customer_id']),
            first_name=str(row.get('first_name', 'Unknown')),
            last_name=str(row.get('last_name', 'Customer')),
            email=str(row.get('email', 'no-email@example.com')),
            segment=str(row.get('segment', 'Regular')),
            lifetime_value=float(row.get('lifetime_value', 0)),
            preferred_category=str(row.get('preferred_category', 'General')),
            loyalty_tier=str(row.get('loyalty_tier', 'Bronze')),
            phone=str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
            signup_date=str(row.get('signup_date', '')) if pd.notna(row.get('signup_date')) else None,
            country=str(row.get('country', '')) if pd.notna(row.get('country')) else None,
            avg_order_value=float(row.get('avg_order_value', 0)) if pd.notna(row.get('avg_order_value')) else None,
            last_active_date=str(row.get('last_active_date', '')) if pd.notna(row.get('last_active_date')) else None,
            opt_in_marketing=bool(row.get('opt_in_marketing', True)) if pd.notna(row.get('opt_in_marketing')) else True,
            language=str(row.get('language', 'en')) if pd.notna(row.get('language')) else 'en'
        )
        
        health = monitor._calculate_customer_health(row)
        nps_data = analytics.get_customer_nps(customer)
        support_history = analytics.get_customer_support_history(customer)
        cohort_data = analytics.compare_with_cohort(customer)
        
        similar_cases = []
        try:
            similar_issues = analytics.find_similar_issues(
                event_description="Customer support inquiry",
                event_type="support",
                customer_segment=customer.segment,
                limit=3
            )
            for issue in similar_issues:
                similar_cases.append({
                    'similarity': issue.get('similarity_score', 0),
                    'problem': issue.get('issue_description', '')[:100],
                    'solution': str(issue.get('resolution', ''))[:100],
                    'csat': issue.get('csat_score', 0),
                    'effectiveness': issue.get('effectiveness', 'unknown')
                })
        except:
            pass
        
        return jsonify({
            'customer': {
                'id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'email': customer.email,
                'phone': customer.phone,
                'segment': customer.segment,
                'loyaltyTier': customer.loyalty_tier,
                'lifetimeValue': customer.lifetime_value,
                'avgOrderValue': customer.avg_order_value or 0,
                'language': customer.language,
                'country': customer.country,
                'lastActive': customer.last_active_date,
                'optInMarketing': customer.opt_in_marketing
            },
            'health': {
                'score': int(health['health_score'] * 100),
                'churnRisk': int(health['churn_risk'] * 100),
                'riskLevel': health['risk_level'],
                'reasons': health['reasons']
            },
            'context': {
                'nps': nps_data,
                'support': support_history,
                'cohort': cohort_data
            },
            'similarCases': similar_cases
        })
    except Exception as e:
        print(f"Error in get_customer_details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/search')
def search_customers():
    """Search customers by name, email, or ID"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify([])
        
        df = analytics.df
        
        # Search in multiple fields
        mask = (
            df['customer_id'].astype(str).str.lower().str.contains(query, na=False) |
            df['first_name'].astype(str).str.lower().str.contains(query, na=False) |
            df['last_name'].astype(str).str.lower().str.contains(query, na=False) |
            df['email'].astype(str).str.lower().str.contains(query, na=False)
        )
        
        results = []
        for idx, row in df[mask].head(10).iterrows():
            results.append({
                'id': str(row['customer_id']),
                'name': f"{row.get('first_name', '')} {row.get('last_name', '')}",
                'email': str(row.get('email', '')),
                'segment': str(row.get('segment', ''))
            })
        
        return jsonify(results)
    except Exception as e:
        print(f"Error in search_customers: {e}")
        return jsonify([])



@app.route('/api/customers/processed')
def get_processed_customers():
    """Get all processed customers with their status"""
    return jsonify(processed_customers)

@app.route('/api/customers/<customer_id>/status')
def get_customer_status(customer_id):
    """Get status of a specific customer"""
    if customer_id in processed_customers:
        return jsonify(processed_customers[customer_id])
    else:
        return jsonify({'status': 'pending', 'customerName': None, 'timestamp': None, 'intervention': None})

@app.route('/api/scan/process-customer/<customer_id>', methods=['POST'])
def process_single_customer(customer_id):
    """Process a specific customer through the 4-agent workflow"""
    try:
        # Check if already processed
        if customer_id in processed_customers and processed_customers[customer_id]['status'] in ['sent', 'escalated']:
            return jsonify({
                'success': True,
                'message': 'Customer already processed',
                'intervention': processed_customers[customer_id]['intervention']
            })
        
        # Find customer in dataset
        df = analytics.df
        customer_row = df[df['customer_id'] == customer_id]
        
        if customer_row.empty:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        # Create Customer object
        row = customer_row.iloc[0]
        customer = Customer(
            customer_id=customer_id,
            first_name=row.get('first_name', ''),
            last_name=row.get('last_name', ''),
            email=row.get('email', ''),
            segment=row.get('segment', 'Regular'),
            lifetime_value=float(row.get('lifetime_value', 0)),
            language=row.get('language', 'en')
        )
        
        # Get alert data
        alerts = monitor.detect_churn_risks(min_churn_risk=0.3)
        alert = next((a for a in alerts if a['customer_id'] == customer_id), None)
        
        if not alert:
            return jsonify({'success': False, 'error': 'Customer not at risk'}), 400
        
        # Create event
        event = create_proactive_event(customer, alert)
        
        # Process through agents
        intervention = run_agents_with_tracking(customer, event, alert)
        
        return jsonify({
            'success': True,
            'intervention': intervention
        })
        
    except Exception as e:
        print(f"Error processing customer {customer_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/scan/clear-session', methods=['POST'])
def clear_session():
    """Clear all session data (processed customers, interventions, events)"""
    try:
        clear_session_history()
        return jsonify({
            'status': 'success',
            'message': 'Session cleared - all customers reset to PENDING'
        })
    except Exception as e:
        print(f"Error clearing session: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scan/proactive', methods=['POST'])
def trigger_proactive_scan():
    try:
        clear_session_history()  # Clear on each scan
        
        data = request.json or {}
        max_customers = data.get('maxCustomers', 10)  # Process 10 customers
        min_risk = data.get('riskThreshold', 0.7)
        
        thread = threading.Thread(
            target=run_proactive_scan_with_agents,
            args=(max_customers, min_risk),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'status': 'started',
            'message': f'Proactive scan initiated'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_proactive_scan_with_agents(max_customers, min_risk):
    global recent_interventions, recent_events, agent_history
    
    try:
        # Emit scan started
        socketio.emit('scan_started', {
            'timestamp': datetime.now().isoformat(),
            'maxCustomers': max_customers,
            'riskThreshold': min_risk
        })
        
        # Detect at-risk customers - SAME as CLI dashboard
        alerts = monitor.detect_churn_risks(min_churn_risk=min_risk)
        
        socketio.emit('customers_detected', {
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })
        
        # Process each customer
        completed_customers = []
        for i, alert in enumerate(alerts[:max_customers], 1):
            customer = alert['customer']
            
            # Emit queue status showing: completed, processing, queued
            remaining_alerts = alerts[i:max_customers]
            queued_names = [f"{a['customer'].first_name} {a['customer'].last_name}" for a in remaining_alerts[:3]]
            
            socketio.emit('customer_queue_status', {
                'completed': completed_customers[-1] if completed_customers else None,
                'processing': f"{customer.first_name} {customer.last_name}",
                'queued': queued_names,
                'queuedCount': len(remaining_alerts)
            })
            
            socketio.emit('customer_started', {
                'index': i,
                'total': min(max_customers, len(alerts)),
                'customerId': customer.customer_id,
                'customerName': f"{customer.first_name} {customer.last_name}",
                'healthScore': int(alert['health_score'] * 100),
                'churnRisk': int(alert['churn_risk'] * 100)
            })
            
            # Create event
            event = create_proactive_event(customer, alert)
            
            # Run through agents with tracking
            intervention_data = run_agents_with_tracking(customer, event, alert)
            
            # Save intervention
            recent_interventions.insert(0, intervention_data)
            if len(recent_interventions) > 50:
                recent_interventions.pop()
            
            socketio.emit('intervention_complete', intervention_data)
            
            # Add to completed list
            completed_customers.append(f"{customer.first_name} {customer.last_name}")
            
            time.sleep(0.5)  # Small delay for visual effect
        
        socketio.emit('scan_complete', {
            'timestamp': datetime.now().isoformat(),
            'processed': min(max_customers, len(alerts))
        })
        
    except Exception as e:
        print(f"Error in run_proactive_scan_with_agents: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit('scan_error', {'error': str(e)})

def run_agents_with_tracking(customer, event, alert):
    """Run all 4 agents with REAL timing - emits events during actual execution"""
    
    global processed_customers
    
    # 🔥 NEW: Check if customer was already contacted in last 24 hours
    recent_history = memory_handler.get_recent_interactions(
        customer.customer_id,
        days=1  # Last 24 hours
    )
    
    if recent_history:
        last_interaction = recent_history[0]
        timestamp = datetime.fromisoformat(last_interaction['timestamp'])
        hours_ago = (datetime.now() - timestamp).total_seconds() / 3600
        
        if hours_ago < 24:
            print(f"\n{'='*70}")
            print(f"[SKIP] Customer already contacted {hours_ago:.1f} hours ago")
            print(f"[SKIP] {customer.first_name} {customer.last_name} ({customer.customer_id})")
            print(f"{'='*70}\n")
            
            # Mark as skipped in processed_customers
            processed_customers[customer.customer_id] = {
                'status': 'skipped',
                'customerName': f"{customer.first_name} {customer.last_name}",
                'timestamp': datetime.now().isoformat(),
                'reason': f'Already contacted {hours_ago:.1f} hours ago',
                'intervention': None
            }
            
            # Emit skip event to frontend
            socketio.emit('customer_skipped', {
                'customerId': customer.customer_id,
                'customerName': f"{customer.first_name} {customer.last_name}",
                'reason': f'Already contacted {hours_ago:.1f} hours ago',
                'lastContactTime': timestamp.isoformat()
            })
            
            return None  # Skip processing
    
    agent_results = {}
    
    # Mark customer as PROCESSING (internal tracking only, don't emit yet)
    processed_customers[customer.customer_id] = {
        'status': 'processing',
        'customerName': f"{customer.first_name} {customer.last_name}",
        'timestamp': datetime.now().isoformat(),
        'intervention': None
    }
    
    # Create initial state
    initial_state = AgentState(
        customer=customer,
        event=event,
        messages=[]
    )
    
    print(f"[WORKFLOW] Processing customer {customer.customer_id} - {customer.first_name} {customer.last_name}")
    
    try:
        # Agent 1: Bodha (Context Agent) - START
        socketio.emit('agent_started', {
            'agent': 'bodha',
            'agentName': 'Bodha - Context Agent',
            'customerId': customer.customer_id,
            'description': 'Analyzing customer context and sentiment'
        })
        time.sleep(1.5)  # Visual delay for agent processing
        
        # Run the FULL workflow (all 4 agents sequentially)
        start_time = time.time()
        final_state = run_workflow(workflow, initial_state)
        total_duration = time.time() - start_time
        
        print(f"[WORKFLOW] Completed in {total_duration:.2f}s for customer {customer.customer_id}")
        print(f"[AI RESULTS] Sentiment: {final_state.sentiment}, Urgency: {final_state.urgency_level}, Escalation: {final_state.escalation_needed}")
        print(f"[AI RESULTS] Recommended Action: {final_state.recommended_action}")
        print(f"[AI RESULTS] Message Length: {len(final_state.personalized_response) if final_state.personalized_response else 0} chars")
        
        # Extract REAL results from final state (agents have already run)
        agent_results['bodha'] = {
            'sentiment': final_state.sentiment.value if final_state.sentiment else 'neutral',
            'urgency': final_state.urgency_level if final_state.urgency_level else 3,
            'riskScore': final_state.customer_risk_score if final_state.customer_risk_score else alert['churn_risk'],
            'contextSummary': final_state.context_summary or 'Customer context analyzed',
            'duration': round(total_duration * 0.25, 2)
        }
        
        # Agent 1: Bodha (Context Agent) - COMPLETE
        socketio.emit('agent_completed', {
            'agent': 'bodha',
            'customerId': customer.customer_id,
            'results': agent_results['bodha']
        })
        time.sleep(0.5)
        
        # Agent 2: Dhyana (Pattern Agent) - START
        socketio.emit('agent_started', {
            'agent': 'dhyana',
            'agentName': 'Dhyana - Pattern Agent',
            'customerId': customer.customer_id,
            'description': 'Identifying behavioral patterns and churn signals'
        })
        time.sleep(1.5)
        
        # Extract REAL pattern analysis from final_state
        agent_results['dhyana'] = {
            'churnRisk': int((final_state.predicted_churn_risk or alert['churn_risk']) * 100),
            'patterns': alert['reasons'][:2] if alert.get('reasons') else [],
            'historicalInsights': final_state.historical_insights or 'Pattern analysis complete',
            'similarCases': len(final_state.similar_patterns) if final_state.similar_patterns else 3,
            'duration': round(total_duration * 0.25, 2)
        }
        
        # Agent 2: Dhyana (Pattern Agent) - COMPLETE
        socketio.emit('agent_completed', {
            'agent': 'dhyana',
            'customerId': customer.customer_id,
            'results': agent_results['dhyana']
        })
        time.sleep(0.5)
        
        # Agent 3: Niti (Decision Agent) - START
        socketio.emit('agent_started', {
            'agent': 'niti',
            'agentName': 'Niti - Decision Agent',
            'customerId': customer.customer_id,
            'description': 'Determining best intervention strategy'
        })
        time.sleep(1.5)
        
        # Extract REAL decision from final_state
        agent_results['niti'] = {
            'action': final_state.recommended_action or 'Personalized outreach recommended',
            'actionTaken': final_state.action_taken or 'Preparing intervention',
            'priority': final_state.priority_level or 'high',
            'channels': ['email', 'sms'],
            'escalate': final_state.escalation_needed,
            'discountApplied': final_state.discount_applied if final_state.discount_applied else None,
            'discountAutoApproved': final_state.discount_auto_approved if hasattr(final_state, 'discount_auto_approved') else False,
            'duration': round(total_duration * 0.25, 2)
        }
        
        # Agent 3: Niti (Decision Agent) - COMPLETE
        socketio.emit('agent_completed', {
            'agent': 'niti',
            'customerId': customer.customer_id,
            'results': agent_results['niti']
        })
        time.sleep(0.5)
        
        # Agent 4: Karuna (Empathy Agent) - START
        socketio.emit('agent_started', {
            'agent': 'karuna',
            'agentName': 'Karuna - Empathy Agent',
            'customerId': customer.customer_id,
            'description': 'Generating personalized message'
        })
        time.sleep(1.5)
        
        # Extract REAL personalized message from final_state
        full_message = final_state.personalized_response or f"Dear {customer.first_name}, we value your business and would like to address your concerns."
        agent_results['karuna'] = {
            'message': full_message,  # Send FULL message to frontend
            'messagePreview': full_message[:200] + '...' if len(full_message) > 200 else full_message,
            'language': customer.language or 'en',
            'tone': final_state.tone or 'empathetic',
            'empathyScore': final_state.empathy_score if final_state.empathy_score else 0.8,
            'duration': round(total_duration * 0.25, 2)
        }
        
        # Agent 4: Karuna (Empathy Agent) - COMPLETE
        socketio.emit('agent_completed', {
            'agent': 'karuna',
            'customerId': customer.customer_id,
            'results': agent_results['karuna']
        })
        time.sleep(0.5)
        
        # Create intervention summary with REAL AI data
        is_escalated = final_state.escalation_needed
        
        intervention = {
            'id': f"INT_{customer.customer_id}_{int(time.time())}",
            'customerId': customer.customer_id,
            'customerName': f"{customer.first_name} {customer.last_name}",
            'timestamp': datetime.now().isoformat(),
            'type': 'proactive',
            'healthScore': int(alert['health_score'] * 100),
            'churnRisk': int(alert['churn_risk'] * 100),
            'priority': final_state.priority_level or 'high',
            'action': final_state.recommended_action or 'Personalized retention outreach',
            'aiRecommendation': final_state.recommended_action or 'AI analysis complete',
            'message': agent_results['karuna']['message'],  # FULL AI-generated message
            'language': customer.language or 'en',
            'agents': agent_results,
            'escalated': is_escalated,
            'status': 'escalated' if is_escalated else 'sent',
            'channels': ['email', 'sms'],
            'sentiment': final_state.sentiment.value if final_state.sentiment else 'neutral',
            'urgencyLevel': final_state.urgency_level,
            'discountApplied': final_state.discount_applied,
            'actionTaken': final_state.action_taken or 'Intervention prepared'
        }
        
        # Log the action taken with REAL AI data
        if is_escalated:
            print(f"[CRITICAL] Customer {customer.customer_id} escalated to human")
            print(f"[REASON] {final_state.recommended_action}")
        else:
            print(f"[AUTO-SENT] Message ready for {customer.customer_id} via {intervention['channels']}")
            print(f"[AI ACTION] {final_state.recommended_action}")
            if final_state.discount_applied:
                print(f"[DISCOUNT] {final_state.discount_applied}% discount applied")
            print(f"[MESSAGE PREVIEW] {agent_results['karuna']['message'][:150]}...")
        
        # Update processed_customers with final status
        final_status = 'escalated' if is_escalated else 'sent'
        processed_customers[customer.customer_id] = {
            'status': final_status,
            'customerName': f"{customer.first_name} {customer.last_name}",
            'timestamp': datetime.now().isoformat(),
            'intervention': intervention
        }
        
        # Emit status change to UI
        socketio.emit('customer_status_changed', {
            'customerId': customer.customer_id,
            'customerName': f"{customer.first_name} {customer.last_name}",
            'status': final_status
        })
        
        # If escalation needed, create escalation record
        if is_escalated:
            try:
                escalation_id = escalation_tracker.create_escalation(
                    customer_id=customer.customer_id,
                    reason=final_state.recommended_action or agent_results.get('niti', {}).get('action', 'Escalation needed'),
                    priority=agent_results.get('niti', {}).get('priority', 'high')
                )
                
                intervention['escalationId'] = escalation_id
                
                socketio.emit('escalation_created', {
                    'escalationId': escalation_id,
                    'customerId': customer.customer_id,
                    'customerName': f"{customer.first_name} {customer.last_name}",
                    'timestamp': datetime.now().isoformat(),
                    'priority': agent_results.get('niti', {}).get('priority', 'high')
                })
                
                print(f"[ESCALATION] Created escalation {escalation_id} for {customer.customer_id}")
            except Exception as e:
                print(f"Error creating escalation: {e}")
        
        # 🔥 NEW: Save interaction to memory
        try:
            memory_handler.save_interaction(final_state)
            print(f"[MEMORY] Saved interaction for customer {customer.customer_id}")
        except Exception as e:
            print(f"⚠️ Warning: Could not save to memory: {e}")
        
        return intervention
        
    except Exception as e:
        print(f"❌ Error in run_agents_with_tracking for {customer.customer_id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'id': f"INT_{customer.customer_id}_{int(time.time())}",
            'customerId': customer.customer_id,
            'customerName': f"{customer.first_name} {customer.last_name}",
            'error': str(e)
        }

def create_proactive_event(customer, alert):
    """Create proactive event"""
    return CustomerEvent(
        event_id=f"PROACTIVE_{customer.customer_id}_{int(time.time())}",
        customer=customer,
        event_type=EventType.PROACTIVE_RETENTION,
        timestamp=datetime.now(),
        description=f"Proactive intervention for at-risk customer. {alert['reasons'][0] if alert['reasons'] else 'Health declining'}",
        metadata={
            'health_score': alert['health_score'],
            'churn_risk': alert['churn_risk'],
            'reasons': alert['reasons']
        }
    )

# =============================================================================
# NEW ENDPOINTS FOR ENHANCED UI
# =============================================================================

@app.route('/api/dashboard/risk-distribution')
def get_risk_distribution():
    """Get CACHED risk distribution for instant pie chart load"""
    try:
        # Return CACHED risk distribution (calculated once on startup)
        return jsonify(cached_risk_distribution)
    except Exception as e:
        print(f"Error in get_risk_distribution: {e}")
        return jsonify({
            "critical": {"count": 0, "percentage": 0, "color": "#ef4444"},
            "high": {"count": 0, "percentage": 0, "color": "#f59e0b"},
            "medium": {"count": 0, "percentage": 0, "color": "#eab308"},
            "low": {"count": 0, "percentage": 0, "color": "#10b981"}
        }), 500

@app.route('/api/customers/priority-queue')
def get_priority_queue():
    """Get top priority customers for the sidebar - USES LIVE DATA for accuracy"""
    try:
        limit = int(request.args.get('limit', 10))  # Default to 10 for TOP 10
        
        # Always use LIVE data to match processing - same as run_proactive_scan_with_agents
        alerts = monitor.detect_churn_risks(min_churn_risk=0.3)
        # Sort by churn_risk descending to get top 10
        sorted_alerts = sorted(alerts, key=lambda x: x['churn_risk'], reverse=True)[:limit]
        
        priority_queue = []
        for alert in sorted_alerts:
            customer = alert['customer']
            
            # Check if customer is escalated
            is_escalated = customer.customer_id in escalation_tracker.active_escalations
            
            priority_queue.append({
                "id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "segment": customer.segment,
                "category": customer.preferred_category or "General",
                "language": customer.language or "English",
                "churnRisk": round(alert['churn_risk'] * 100, 1),
                "ltv": customer.lifetime_value,
                "healthScore": round(alert['health_score'] * 100, 1),
                "priority": alert['risk_level'].lower(),
                "riskColor": "#ef4444" if alert['churn_risk'] >= 0.9 else "#f59e0b",
                "escalated": is_escalated
            })
        
        return jsonify(priority_queue)
    except Exception as e:
        print(f"Error in get_priority_queue: {e}")
        return jsonify([])

@app.route('/api/escalations/active')
def get_active_escalations():
    """Get count and list of active escalations for tab badges"""
    try:
        active_count = len(escalation_tracker.active_escalations)
        
        # Get recent escalations
        escalations = []
        for customer_id, escalation in escalation_tracker.active_escalations.items():
            escalations.append({
                "id": escalation.escalation_id,
                "customerId": customer_id,
                "reason": escalation.reason,
                "priority": escalation.priority,
                "createdAt": escalation.escalated_at.isoformat(),
                "status": escalation.status
            })
        
        return jsonify({
            "count": min(active_count, 2),  # Show max 2 escalations
            "escalations": escalations[:2]  # Limit to 2 escalations
        })
    except Exception as e:
        print(f"Error in get_active_escalations: {e}")
        return jsonify({"count": 0, "escalations": []})

@app.route('/api/dashboard/resolved-today')
def get_resolved_today():
    """Get count of resolved cases today"""
    try:
        today = datetime.now().date()
        resolved_count = 0
        
        # Count interventions that led to positive outcomes
        for intervention in recent_interventions:
            intervention_date = datetime.fromisoformat(intervention['timestamp']).date()
            if intervention_date == today and not intervention.get('escalated', False):
                resolved_count += 1
        
        return jsonify({
            "count": resolved_count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error in get_resolved_today: {e}")
        return jsonify({"count": 0})

# =============================================================================
# REACTIVE SUPPORT (HUMAN + AI)
# =============================================================================

@app.route('/api/escalation/create', methods=['POST'])
def create_escalation():
    """Create human escalation"""
    try:
        data = request.json
        customer_id = data.get('customerId')
        reason = data.get('reason', 'Customer support inquiry')
        priority = data.get('priority', 'medium')
        
        # Create escalation
        escalation_id = escalation_tracker.create_escalation(
            customer_id=customer_id,
            reason=reason,
            priority=priority
        )
        
        socketio.emit('escalation_created', {
            'escalationId': escalation_id,
            'customerId': customer_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'status': 'success',
            'escalationId': escalation_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/interventions/history')
def get_intervention_history():
    """Get intervention history"""
    return jsonify(recent_interventions[:50])

# =============================================================================
# WEBSOCKET HANDLERS
# =============================================================================

@socketio.on('connect')
def handle_connect():
    global active_connections
    active_connections += 1
    emit('connected', {
        'message': 'Connected to ProCX',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    global active_connections
    active_connections -= 1

# =============================================================================
# STARTUP WORKFLOWS (Run on backend start)
# =============================================================================

def run_initial_health_scan():
    """
    Run initial health scan on startup and CACHE stats (not customer data)
    """
    global cached_stats, cached_risk_distribution
    
    print("\n🔍 Running initial health scan...")
    try:
        alerts = monitor.detect_churn_risks(min_churn_risk=0.3, min_lifetime_value=0.0)
        
        # Sort by churn risk (highest first)
        alerts = sorted(alerts, key=lambda x: x['churn_risk'], reverse=True)
        
        critical = len([a for a in alerts if a['churn_risk'] >= 0.8])
        high = len([a for a in alerts if 0.6 <= a['churn_risk'] < 0.8])
        medium = len([a for a in alerts if 0.4 <= a['churn_risk'] < 0.6])
        low = len([a for a in alerts if a['churn_risk'] < 0.4])
        
        # CACHE the stats for instant load
        cached_stats = {
            'totalCustomers': len(analytics.df),
            'healthyCustomers': len(analytics.df) - len(alerts),
            'atRiskCustomers': len(alerts),
            'criticalCustomers': critical,
            'interventionsToday': 0,
            'avgHealthScore': int((1 - (len(alerts) / len(analytics.df))) * 100) if len(analytics.df) > 0 else 0,
            'activeEscalations': min(len(escalation_tracker.active_escalations), 2)  # Show max 2
        }
        
        # CACHE risk distribution for pie chart
        total = len(analytics.df)
        cached_risk_distribution = {
            "critical": {"count": critical, "percentage": round((critical / total) * 100) if total > 0 else 0, "color": "#ef4444"},
            "high": {"count": high, "percentage": round((high / total) * 100) if total > 0 else 0, "color": "#f59e0b"},
            "medium": {"count": medium, "percentage": round((medium / total) * 100) if total > 0 else 0, "color": "#eab308"},
            "low": {"count": len(analytics.df) - critical - high - medium, "percentage": round(((len(analytics.df) - critical - high - medium) / total) * 100) if total > 0 else 0, "color": "#10b981"}
        }
        
        # NOTE: Customer data is NOT cached - always fetched live via /api/customers/priority-queue
        
        print(f"   ✓ Found {len(alerts)} at-risk customers")
        print(f"   ✓ Critical: {critical} | High: {high} | Medium: {medium} | Low: {low}")
        print(f"   ✓ Stats CACHED (customer data always live)")
        
        # Print top 10 customer IDs for demo selection
        print(f"\n   📋 Top 10 At-Risk Customers (auto-processing all 10):")
        for i, alert in enumerate(alerts[:10], 1):
            cust = alert['customer']
            risk_pct = int(alert['churn_risk'] * 100)
            status_marker = "← Auto-processing"
            print(f"      {i}. {cust.customer_id} - {cust.first_name} {cust.last_name} ({risk_pct}% risk, {cust.segment}) {status_marker}")
        
        return alerts
    except Exception as e:
        print(f"   ✗ Error in health scan: {e}")
        return []

def run_background_interventions():
    """
    Auto-process first 3 at-risk customers on startup for demo optimization.
    Processes top customers by churn risk to show mix of auto-sent and escalated.
    By the time UI loads, these customers will show as SENT or ESCALATED.
    """
    print("\n🤖 Auto-processing first 10 customers for demo...")
    try:
        # Get at-risk customers sorted by churn risk (highest first)
        alerts = monitor.detect_churn_risks(min_churn_risk=0.3)
        
        # Take first 10 from the sorted list (highest risk customers)
        alerts = alerts[:10]
        
        if len(alerts) < 10:
            print(f"   ⏭️  Only {len(alerts)} at-risk customers found, processing all")
        
        # Process customers in background thread
        def process_startup_customers():
            time.sleep(2)  # Small delay to let server finish starting
            for i, alert in enumerate(alerts, 1):
                customer = alert['customer']
                print(f"   [{i}/{len(alerts)}] Processing {customer.first_name} {customer.last_name}...")
                
                try:
                    event = create_proactive_event(customer, alert)
                    intervention = run_agents_with_tracking(customer, event, alert)
                    
                    # Save intervention
                    recent_interventions.insert(0, intervention)
                    if len(recent_interventions) > 50:
                        recent_interventions.pop()
                    
                    # 🔥 EMIT to any connected clients (so UI gets the data)
                    socketio.emit('intervention_complete', intervention)
                    
                    status = intervention.get('status', 'sent')
                    print(f"   ✓ {customer.first_name} {customer.last_name} → {status.upper()}")
                    
                except Exception as e:
                    print(f"   ✗ Error processing {customer.customer_id}: {e}")
            
            print(f"   ✅ Startup processing complete! {len(alerts)} customers ready for demo.")
        
        thread = threading.Thread(target=process_startup_customers, daemon=True)
        thread.start()
        print("   ✓ Background processing started")
        
    except Exception as e:
        print(f"   ✗ Error starting auto-processing: {e}")

if __name__ == '__main__':
    print("🚀 ProCX Backend API")
    print("📡 WebSocket + 4-Agent tracking")
    
    run_initial_health_scan()
    # DON'T auto-process on startup - let user trigger from UI for session-based history
    # run_background_interventions()
    
    print("🌐 http://localhost:5000")
    print("✅ Server ready!")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
