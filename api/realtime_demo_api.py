from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import threading
import time
import subprocess
from pathlib import Path
from datetime import datetime
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__, static_folder='..')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store real-time events
realtime_events = []
current_scenario = None
demo_running = False

@app.route('/')
def index():
    return send_from_directory('..', 'realtime_showcase.html')

@app.route('/api/realtime/status')
def get_status():
    return jsonify({
        'running': demo_running,
        'events': realtime_events,
        'currentScenario': current_scenario
    })

@app.route('/api/realtime/start')
def start_demo():
    global demo_running
    if not demo_running:
        demo_running = True
        thread = threading.Thread(target=run_realtime_demo)
        thread.daemon = True
        thread.start()
        return jsonify({'status': 'started'})
    return jsonify({'status': 'already running'})

def parse_demo_output(line):
    """Parse output from demo_realtime.py and extract key information"""
    
    # Payment failure detection
    if "VIP customer payment FAILS" in line:
        return {
            'type': 'payment_failure',
            'timestamp': datetime.now().isoformat(),
            'event': 'Payment Failure Detected',
            'severity': 'high'
        }
    
    # Customer info
    customer_match = re.search(r'Customer: (.+?) \| (.+?) \| LTV: \$(.+)', line)
    if customer_match:
        return {
            'type': 'customer_info',
            'timestamp': datetime.now().isoformat(),
            'customerName': customer_match.group(1),
            'segment': customer_match.group(2),
            'ltv': customer_match.group(3)
        }
    
    # Agent processing
    if "Agent" in line and ":" in line:
        return {
            'type': 'agent_processing',
            'timestamp': datetime.now().isoformat(),
            'message': line.strip()
        }
    
    # Intervention ready
    if "Intervention READY" in line:
        return {
            'type': 'intervention_ready',
            'timestamp': datetime.now().isoformat(),
            'event': 'Intervention Ready'
        }
    
    # Processing time
    time_match = re.search(r'Processing time: ([\d.]+) seconds', line)
    if time_match:
        return {
            'type': 'processing_time',
            'timestamp': datetime.now().isoformat(),
            'duration': float(time_match.group(1))
        }
    
    # Message preview
    if line.strip().startswith('வணக்கம்') or 'Dear' in line:
        return {
            'type': 'message_preview',
            'timestamp': datetime.now().isoformat(),
            'message': line.strip()
        }
    
    return None

def run_realtime_demo():
    """Run the demo_realtime.py script and capture output"""
    global demo_running, realtime_events, current_scenario
    
    try:
        # Clear previous events
        realtime_events = []
        
        # Emit start event
        socketio.emit('demo_started', {
            'timestamp': datetime.now().isoformat(),
            'message': 'Starting real-time demo...'
        })
        
        # Run the demo script
        demo_path = Path(__file__).parent.parent / 'demo_realtime.py'
        
        process = subprocess.Popen(
            ['python', str(demo_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output line by line
        for line in process.stdout:
            if line.strip():
                print(f"[DEMO] {line.strip()}")
                
                # Parse the line
                parsed = parse_demo_output(line)
                if parsed:
                    realtime_events.append(parsed)
                    
                    # Emit to frontend via WebSocket
                    socketio.emit('demo_event', parsed)
                    
                    # Update current scenario
                    if parsed['type'] == 'payment_failure':
                        current_scenario = 'payment_failure'
                        socketio.emit('scenario_change', {
                            'scenario': 'payment_failure',
                            'title': 'Payment Failure Detection',
                            'description': 'VIP customer payment failed - AI agents triggered'
                        })
        
        process.wait()
        
        # Emit completion event
        socketio.emit('demo_completed', {
            'timestamp': datetime.now().isoformat(),
            'totalEvents': len(realtime_events)
        })
        
    except Exception as e:
        print(f"Error running demo: {e}")
        socketio.emit('demo_error', {
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        })
    finally:
        demo_running = False

@socketio.on('connect')
def handle_connect():
    print('Client connected to real-time demo')
    emit('connection_established', {
        'timestamp': datetime.now().isoformat(),
        'eventsCount': len(realtime_events)
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from real-time demo')

if __name__ == '__main__':
    print("🚀 ProCX Real-Time Demo Server Starting...")
    print("📡 Running demo_realtime.py in background...")
    
    # Auto-start demo on server start
    threading.Thread(target=run_realtime_demo, daemon=True).start()
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
