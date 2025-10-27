"""
Real-Time Demo API - Simplified WebSocket Server
Runs demo_realtime.py and streams events to the browser via WebSocket
"""
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import threading
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to import ProCX modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ProCX
from models import Customer, CustomerEvent, EventType

app = Flask(__name__, static_folder='..')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
demo_running = False


@app.route('/')
def index():
    """Serve the real-time showcase HTML"""
    return send_from_directory('..', 'realtime_showcase.html')


def emit_event(event_type, data, room=None):
    """Helper to emit events to connected clients"""
    if room:
        # Emit to specific client/room
        socketio.emit('demo_event', {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            **data
        }, room=room)
    else:
        # Broadcast to all (fallback)
        socketio.emit('demo_event', {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            **data
        })
    time.sleep(0.5)  # Dramatic pause for visualization


def run_payment_failure_demo(session_id=None):
    """
    Run the payment failure demo scenario
    This mimics demo_realtime.py but streams events in real-time
    """
    global demo_running
    
    try:
        emit_event('scenario_start', {
            'event': '🚨 Real-Time Event Detection',
            'message': 'Payment Failure - VIP Customer'
        }, room=session_id)
        
        # Step 1: Payment failure detected
        emit_event('payment_failure', {
            'event': '💳 Payment Failure Detected',
            'message': 'VIP customer payment FAILED - Card expired',
            'severity': 'high'
        }, room=session_id)
        
        # Step 2: Customer info
        emit_event('customer_info', {
            'event': '👤 Customer Identified',
            'customerName': 'Tanya Kumar',
            'segment': 'VIP',
            'ltv': '15,000',
            'language': 'Tamil',
            'message': 'Customer: Tanya Kumar | VIP | LTV: $15,000'
        }, room=session_id)
        
        # Step 3: Initialize ProCX and create actual customer
        procx = ProCX()
        
        # Generate unique customer ID for each demo run to avoid "already contacted" skip
        unique_customer_id = f"C100924_{int(time.time())}"
        
        customer = Customer(
            customer_id=unique_customer_id,
            first_name="Tanya",
            last_name="Kumar",
            email="tanya.kumar@example.com",
            segment="VIP",
            lifetime_value=15000.0,
            preferred_category="Electronics",
            loyalty_tier="Platinum",
            language="ta",
            phone="+91-9876543210",
            signup_date="2023-01-15",
            country="India",
            avg_order_value=1500.0,
            last_active_date="2025-10-25",
            opt_in_marketing=True
        )
        
        event = CustomerEvent(
            event_id=f"PAYMENT_FAIL_{customer.customer_id}_{int(time.time())}",
            customer=customer,
            event_type=EventType.PROACTIVE_RETENTION,
            timestamp=datetime.now(),
            description="Payment failed - card expired",
            metadata={
                'event_source': 'payment_gateway',
                'failure_reason': 'expired_card',
                'transaction_amount': 2499.00
            }
        )
        
        # Step 4: Agent processing
        emit_event('agent_processing', {
            'event': '🤖 Bodha (Context Agent): Analyzing Context',
            'message': 'Bodha: Analyzing customer context and event urgency',
            'agent': 'Bodha'
        }, room=session_id)
        
        emit_event('agent_processing', {
            'event': '🤖 Dhyana (Pattern Agent): Pattern Recognition',
            'message': 'Dhyana: Identifying behavioral patterns and trends',
            'agent': 'Dhyana'
        }, room=session_id)
        
        emit_event('agent_processing', {
            'event': '🤖 Niti (Decision Agent): Making Decisions',
            'message': 'Niti: Determining optimal intervention strategy',
            'agent': 'Niti'
        }, room=session_id)
        
        emit_event('agent_processing', {
            'event': '🤖 Karuna (Empathy Agent): Generating Message',
            'message': 'Karuna: Crafting empathetic Tamil message',
            'agent': 'Karuna'
        }, room=session_id)
        
        print("✅ All event emissions complete, now calling AI workflow...")
        
        # Step 5: Run actual AI workflow
        print("🔄 About to call procx.process_proactive_event()...")
        start_time = time.time()
        try:
            result = procx.process_proactive_event(event, verbose=True)
            print(f"✅ AI processing completed in {time.time() - start_time:.1f}s")
            
            if result is None:
                raise Exception("AI workflow returned None - event was skipped. This shouldn't happen with unique customer IDs.")
            
            print(f"📝 Result: {result.personalized_response[:100] if result.personalized_response else 'No message'}...")
        except Exception as ai_error:
            print(f"❌ AI processing failed: {ai_error}")
            import traceback
            traceback.print_exc()
            raise
        elapsed = time.time() - start_time
        
        # Step 6: Intervention ready (includes message and details)
        emit_event('intervention_ready', {
            'event': '🎯 Intervention Deployed',
            'message': result.personalized_response,
            'action': result.recommended_action,
            'priority': result.priority_level,
            'channel': 'WhatsApp',
            'language': 'Tamil',
            'tone': result.tone or 'empathetic',
            'duration': round(elapsed, 1),
            'interventionDetails': {
                'message': result.personalized_response,
                'action': result.recommended_action,
                'priority': result.priority_level,
                'discount': getattr(result, 'discount_applied', None),
                'channel': 'WhatsApp'
            }
        }, room=session_id)
        
        socketio.emit('demo_completed', {
            'timestamp': datetime.now().isoformat(),
            'totalTime': round(elapsed, 1)
        }, room=session_id)
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()
        socketio.emit('demo_error', {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, room=session_id)
    finally:
        demo_running = False


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('✅ Client connected to real-time demo')
    emit('connection_established', {
        'timestamp': datetime.now().isoformat(),
        'message': 'Connected to ProCX Real-Time Demo Server'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('👋 Client disconnected from real-time demo')


@socketio.on('start_demo')
def handle_start_demo():
    """Handle demo start request from client"""
    global demo_running
    
    if demo_running:
        emit('demo_error', {
            'timestamp': datetime.now().isoformat(),
            'error': 'Demo is already running'
        })
        return
    
    demo_running = True
    print('🎬 Starting payment failure demo...')
    
    # Get the session ID of the requesting client from Flask request context
    session_id = request.sid
    print(f'📍 Session ID: {session_id}')
    
    # Run demo in background thread, pass session_id to send events only to this client
    thread = threading.Thread(target=run_payment_failure_demo, args=(session_id,), daemon=True)
    thread.start()
    
    emit('demo_started', {
        'timestamp': datetime.now().isoformat(),
        'message': 'Demo started successfully'
    })


if __name__ == '__main__':    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
