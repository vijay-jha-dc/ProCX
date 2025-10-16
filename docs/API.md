# 📘 AgentMAX CX - API Documentation

Complete API reference for developers.

---

## Table of Contents

1. [Models](#models)
2. [Agents](#agents)
3. [Workflows](#workflows)
4. [Utilities](#utilities)
5. [Configuration](#configuration)

---

## Models

### Customer

Represents a customer profile.

```python
from models import Customer

customer = Customer(
    customer_id="C100000",
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    segment="VIP",  # VIP, Loyal, Regular, Occasional
    lifetime_value=15000.00,
    preferred_category="Electronics",
    loyalty_tier="Platinum"  # Platinum, Gold, Silver, Bronze
)

# Properties
customer.full_name  # "John Doe"
customer.is_vip  # True
customer.is_high_value  # True (if LTV > 5000)
customer.to_dict()  # Convert to dictionary
```

### CustomerEvent

Represents a customer interaction event.

```python
from models import CustomerEvent, EventType
from datetime import datetime

event = CustomerEvent(
    event_id="EVT_001",
    customer=customer,
    event_type=EventType.COMPLAINT,
    timestamp=datetime.now(),
    description="Product arrived damaged",
    metadata={"order_id": "ORD123456", "priority": "high"}
)

event.to_dict()  # Convert to dictionary
```

### AgentState

State object passed between agents.

```python
from models import AgentState, SentimentType

state = AgentState(
    event=event,
    customer=customer
)

# Context analysis results
state.sentiment = SentimentType.NEGATIVE
state.urgency_level = 4
state.customer_risk_score = 0.75
state.context_summary = "VIP customer with damaged product"

# Pattern analysis results
state.predicted_churn_risk = 0.65
state.historical_insights = "Customer has history of quality issues"

# Decision results
state.recommended_action = "Issue immediate replacement"
state.escalation_needed = True
state.priority_level = "critical"

# Empathy results
state.personalized_response = "Dear Mr. Doe..."
state.tone = "empathetic and professional"
state.empathy_score = 0.9

# Utility methods
state.add_message("agent_name", "message")
state.to_dict()
```

### Enums

```python
from models import EventType, SentimentType, Segment, LoyaltyTier

# Event Types
EventType.ORDER_PLACED
EventType.ORDER_DELAYED
EventType.ORDER_CANCELLED
EventType.COMPLAINT
EventType.INQUIRY
EventType.FEEDBACK
EventType.RETURN_REQUEST

# Sentiment Types
SentimentType.VERY_POSITIVE
SentimentType.POSITIVE
SentimentType.NEUTRAL
SentimentType.NEGATIVE
SentimentType.VERY_NEGATIVE

# Customer Segments
Segment.VIP
Segment.LOYAL
Segment.REGULAR
Segment.OCCASIONAL

# Loyalty Tiers
LoyaltyTier.PLATINUM
LoyaltyTier.GOLD
LoyaltyTier.SILVER
LoyaltyTier.BRONZE
```

---

## Agents

### ContextAgent

Analyzes customer events and extracts contextual information.

```python
from agents import ContextAgent, create_context_agent
from models import AgentState

# Create agent
agent = ContextAgent(model_name="gpt-4", temperature=0.3)
# Or use factory
agent = create_context_agent()

# Use agent
state = AgentState(event=event, customer=customer)
updated_state = agent.analyze(state)
# Or call directly
updated_state = agent(state)

# Results
updated_state.sentiment  # SentimentType
updated_state.urgency_level  # 1-5
updated_state.customer_risk_score  # 0-1
updated_state.context_summary  # str
```

### PatternAgent

Identifies patterns and predicts customer behavior.

```python
from agents import PatternAgent, create_pattern_agent

# Create agent
agent = PatternAgent(model_name="gpt-4", temperature=0.5)
# Or use factory
agent = create_pattern_agent()

# Use agent
updated_state = agent.analyze_patterns(state)
# Or call directly
updated_state = agent(state)

# Results
updated_state.predicted_churn_risk  # 0-1
updated_state.historical_insights  # str
updated_state.similar_patterns  # List[Dict]
```

### DecisionAgent

Makes decisions on actions and escalations.

```python
from agents import DecisionAgent, create_decision_agent

# Create agent
agent = DecisionAgent(model_name="gpt-4", temperature=0.3)
# Or use factory
agent = create_decision_agent()

# Use agent
updated_state = agent.make_decision(state)
# Or call directly
updated_state = agent(state)

# Results
updated_state.recommended_action  # str
updated_state.escalation_needed  # bool
updated_state.priority_level  # "low" | "medium" | "high" | "critical"
```

### EmpathyAgent

Generates personalized, empathetic responses.

```python
from agents import EmpathyAgent, create_empathy_agent

# Create agent
agent = EmpathyAgent(model_name="gpt-4", temperature=0.7)
# Or use factory
agent = create_empathy_agent()

# Use agent
updated_state = agent.generate_response(state)
# Or call directly
updated_state = agent(state)

# Results
updated_state.personalized_response  # str
updated_state.tone  # str
updated_state.empathy_score  # 0-1
```

---

## Workflows

### create_cx_workflow

Creates standard sequential workflow.

```python
from workflows import create_cx_workflow, run_workflow

# Create workflow
workflow = create_cx_workflow()

# Run workflow
initial_state = AgentState(event=event, customer=customer)
final_state = run_workflow(workflow, initial_state)
```

### create_cx_workflow_with_routing

Creates advanced workflow with conditional routing.

```python
from workflows import create_cx_workflow_with_routing

# Create workflow with routing
workflow = create_cx_workflow_with_routing()

# Features:
# - Early exit for simple inquiries
# - Conditional escalation routing
# - Pattern analysis skip for low urgency
```

### run_workflow

Synchronous workflow execution.

```python
from workflows import run_workflow

final_state = run_workflow(workflow, initial_state)
```

### run_workflow_async

Asynchronous workflow execution.

```python
from workflows import run_workflow_async
import asyncio

async def process():
    final_state = await run_workflow_async(workflow, initial_state)
    return final_state

result = asyncio.run(process())
```

### stream_workflow

Stream workflow execution step-by-step.

```python
from workflows import stream_workflow

for step in stream_workflow(workflow, initial_state):
    print(f"Step: {step}")
    # Process each step as it completes
```

---

## Utilities

### EventSimulator

Generates realistic customer events for testing.

```python
from utils import EventSimulator

# Initialize
simulator = EventSimulator()
# Or with custom dataset path
simulator = EventSimulator(dataset_path="path/to/data.xlsx")

# Get random customer
customer = simulator.get_random_customer()
customer = simulator.get_random_customer(segment="VIP")

# Get specific customer
customer = simulator.get_customer_by_id("C100000")

# Generate random event
event = simulator.generate_event()
event = simulator.generate_event(customer=customer)
event = simulator.generate_event(event_type=EventType.COMPLAINT)

# Generate predefined scenario
event = simulator.generate_scenario("vip_complaint")

# Available scenarios
scenarios = simulator.get_available_scenarios()
# Returns: ["vip_complaint", "loyal_order_delay", "new_customer_inquiry",
#           "high_value_at_risk", "positive_feedback"]

# Get dataset statistics
stats = simulator.get_dataset_stats()
# Returns: {
#   "total_customers": 1000,
#   "segments": {...},
#   "loyalty_tiers": {...},
#   "categories": {...},
#   "lifetime_value_stats": {...}
# }
```

### MemoryHandler

Manages conversation history and state persistence.

```python
from utils import MemoryHandler

# Initialize
memory = MemoryHandler()
# Or with custom storage path
memory = MemoryHandler(storage_path=Path("./custom_memory"))

# Save interaction
interaction_id = memory.save_interaction(state)

# Get customer history
history = memory.get_customer_history("C100000")
history = memory.get_customer_history("C100000", max_items=10)

# Get recent interactions
recent = memory.get_recent_interactions("C100000", days=30)

# Find similar interactions
similar = memory.find_similar_interactions(
    event_type="complaint",
    customer_segment="VIP",
    limit=5
)

# Get session summary
summary = memory.get_session_summary()
# Returns: {
#   "total_interactions": 10,
#   "start_time": "...",
#   "end_time": "...",
#   "unique_customers": 8,
#   "event_types": {...}
# }

# Clear session
memory.clear_session()

# Export customer data
export_path = memory.export_customer_data("C100000")
```

---

## Configuration

### Settings

Accessed via `config.settings`:

```python
from config import settings

# API Keys
settings.OPENAI_API_KEY
settings.LANGCHAIN_API_KEY

# LLM Configuration
settings.LLM_MODEL  # "gpt-4"
settings.LLM_TEMPERATURE  # 0.7
settings.LLM_MAX_TOKENS  # 2000

# Agent Models
settings.CONTEXT_AGENT_MODEL
settings.PATTERN_AGENT_MODEL
settings.DECISION_AGENT_MODEL
settings.EMPATHY_AGENT_MODEL

# Memory Configuration
settings.MEMORY_MAX_HISTORY  # 50
settings.MEMORY_RELEVANCE_THRESHOLD  # 0.7

# Workflow Configuration
settings.MAX_ITERATIONS  # 10
settings.TIMEOUT_SECONDS  # 60

# Thresholds
settings.HIGH_VALUE_CUSTOMER_THRESHOLD  # 5000.0
settings.CHURN_RISK_THRESHOLD  # 0.7
settings.ESCALATION_URGENCY_THRESHOLD  # 4

# Paths
settings.BASE_DIR
settings.DATA_DIR
settings.LOGS_DIR
settings.DATASET_PATH
```

### Prompts

Accessed via `config.prompts`:

```python
from config.prompts import SYSTEM_PROMPTS

# Agent prompts
SYSTEM_PROMPTS["context_agent"]
SYSTEM_PROMPTS["pattern_agent"]
SYSTEM_PROMPTS["decision_agent"]
SYSTEM_PROMPTS["empathy_agent"]

# Customize prompts by modifying config/prompts.py
```

---

## Complete Example

```python
from models import AgentState, EventType
from agents import (
    create_context_agent,
    create_pattern_agent,
    create_decision_agent,
    create_empathy_agent
)
from utils import EventSimulator
from workflows import create_cx_workflow, run_workflow

# 1. Setup
simulator = EventSimulator()

# 2. Generate event
event = simulator.generate_scenario("vip_complaint")

# 3. Create workflow
workflow = create_cx_workflow()

# 4. Process
initial_state = AgentState(event=event, customer=event.customer)
final_state = run_workflow(workflow, initial_state)

# 5. Access results
print(f"Sentiment: {final_state.sentiment.value}")
print(f"Priority: {final_state.priority_level}")
print(f"Response: {final_state.personalized_response}")
```

---

## Error Handling

```python
try:
    final_state = run_workflow(workflow, initial_state)
except Exception as e:
    print(f"Error: {e}")
    # Check state.messages for agent-specific errors
    for msg in initial_state.messages:
        print(f"{msg['agent']}: {msg['message']}")
```

---

For more examples, see `example_simple.py` and `main.py`.
