# ProCX Commands and Testing Guide

Complete reference for running and testing the ProCX platform with all agents and workflows.

---

## Table of Contents
1. [Main Platform Commands](#main-platform-commands)
2. [Test Suite Commands](#test-suite-commands)
3. [Individual Component Testing](#individual-component-testing)
4. [Workflow Testing](#workflow-testing)
5. [Troubleshooting](#troubleshooting)

---

## Main Platform Commands

### 1. Customer Health Dashboard

**Command:**
```bash
python main.py --dashboard
```

**Description:**  
Displays a comprehensive customer health dashboard showing all at-risk customers categorized by risk level.

**Expected Outcome:**
```
>> Initializing ProCX Platform (Proactive Mode)...
[OK] DataAnalytics: Loaded 1000 customers for analysis
[OK] ProactiveMonitor initialized
[OK] ProCX Platform ready!

[DASHBOARD] CUSTOMER HEALTH DASHBOARD
======================================================================

[CRITICAL] Critical Risk: 3 customers (>=80% churn risk)
[HIGH] High Risk: 21 customers (60-79% churn risk)
[MEDIUM] Medium Risk: 65 customers (40-59% churn risk)
[LOW] Low Risk: 19 customers (<40% churn risk)

[LIST] Top 10 At-Risk Customers:
1. [CRITICAL] Tanya Kumar (C100924)
   Segment: Occasional | LTV: $1,016.23
   Health: 25.7% | Churn Risk: 84.2%
...
```

**Workflow:**
1. Platform initializes with data analytics and proactive monitor
2. ProactiveMonitor scans all customers from dataset
3. Calculates health scores and churn risk for each customer
4. Categorizes customers by risk level
5. Displays top 10 at-risk customers with details

---

### 2. Proactive Interventions

**Command:**
```bash
python main.py --interventions
```

**Description:**  
Runs proactive interventions for at-risk customers, processing them through the full multi-agent workflow.

**Optional Parameters:**
- `--max-interventions N` - Limit number of interventions (default: 5)
- `--risk-threshold 0.X` - Minimum churn risk threshold (default: 0.6)

**Example:**
```bash
python main.py --interventions --max-interventions 3 --risk-threshold 0.7
```

**Expected Outcome:**
```
[SCAN] PROACTIVE CUSTOMER SCAN
======================================================================
Scanning for at-risk customers...
Risk threshold: 60%

[WARNING] Found 24 at-risk customers requiring intervention!

======================================================================
[TARGET] PROACTIVE INTERVENTION #1/3
======================================================================
[CUSTOMER] Tanya Kumar (C100924)
   Segment: Occasional | Tier: Bronze
   Lifetime Value: $1,016.23

[ANALYSIS] Health Analysis:
   Health Score: 25.7% [CRITICAL]
   Churn Risk: 84.2% [CRITICAL]
   Risk Level: CRITICAL

[ACTION] Recommended Action: Offer a personalized retention package
[MESSAGE] Personalized Message:
   தீபாவளி வாழ்த்துக்கள்! [Tamil festival greeting] ...

======================================================================
[OK] Completed 3 proactive interventions
======================================================================
```

**Workflow:**
1. Platform initializes and scans all customers
2. Identifies customers above risk threshold
3. Prioritizes by churn risk (highest first)
4. For each customer:
   - Creates CustomerEvent
   - Runs through 4-agent pipeline:
     - **Bodha (Context Agent)**: Analyzes customer situation
     - **Dhyana (Pattern Agent)**: Identifies behavioral patterns
     - **Niti (Decision Agent)**: Determines action strategy
     - **Karuna (Empathy Agent)**: Generates personalized response
   - Stores interaction in memory
   - Displays recommended action and personalized message
5. Generates summary report

---

## Test Suite Commands

### 3. Enhanced Features Test

**Command:**
```bash
python -X utf8 test_features.py
```

**Description:**  
Tests festival context management and escalation tracking features.

**Expected Outcome:**
```
======================================================================
🧪 PROCX ENHANCED FEATURES TEST SUITE
======================================================================

======================================================================
🎉 TESTING FESTIVAL CONTEXT MANAGER
======================================================================

1️⃣ Current Festival Context:
   ✅ Active Festival: Diwali
   📅 Date: 2025-10-20
   📝 Significance: Festival of lights, major shopping season

2️⃣ Current Seasonal Context:
   ✅ Season: festive_season
   🎨 Tone: celebratory, joyful, generous

3️⃣ Product-Festival Relevance:
   ✅ Festival Relevant: True
   ⭐ Relevance Score: 1.0
   🎊 Festival: Diwali

✅ Festival Context Tests Complete!

======================================================================
🚨 TESTING ESCALATION TRACKER
======================================================================

1️⃣ Initial Statistics:
   📊 Active Escalations: 0
   📚 Total Historical: 1

2️⃣ Creating Test Escalation:
   ✅ Created: ESC_TEST_C999999_[timestamp]

3️⃣ Testing Skip Logic:
   Should Skip: True
   ✅ Reason: Active escalation - being handled by human

✅ Escalation Tracker Tests Complete!

======================================================================
✅ ALL TESTS PASSED!
======================================================================
```

**Workflow:**
1. **Festival Context Tests:**
   - Detects current festival (Diwali, Holi, Christmas, etc.)
   - Retrieves seasonal context and messaging tone
   - Checks product-festival relevance
   - Generates festival greetings in multiple languages

2. **Escalation Tracker Tests:**
   - Creates test escalation
   - Tests skip logic (prevents duplicate AI interventions)
   - Resolves escalation
   - Validates status transitions

3. **Integration Tests:**
   - Tests combined festival + escalation scenarios
   - Validates critical purchase detection

---

### 4. Scenario Testing (Full Workflow)

**Command:**
```bash
python -X utf8 test_scenarios.py
```

**Description:**  
Runs comprehensive end-to-end tests with diverse customer scenarios from the real dataset.

**Expected Outcome:**
```
🔬 ProCX Proactive Mode - Diverse Scenario Testing

🚀 PROACTIVE MODE TEST SCENARIO RUNNER
======================================================================
Dataset: data/AgentMAX_CX_dataset.xlsx
Total Customers: 1000

📋 Generated 5 test scenarios:
1. VIP_WITH_COMPLAINT: VIP customer with recent support ticket
2. NEW_CUSTOMER_ISSUE: New customer with first order problem
3. MULTIPLE_TICKETS: Customer with multiple support tickets
4. FESTIVAL_PURCHASE: Customer with festival-related purchase
5. AT_RISK_HIGH_LTV: High lifetime value customer at risk

🚀 Starting automated test run...

======================================================================
🎯 SCENARIO: VIP_WITH_COMPLAINT
👤 Customer ID: C100100
======================================================================

📊 Customer Profile:
   Name: Vihaan Agarwal
   Segment: VIP
   Lifetime Value: ₹4,508.57
   Support Tickets: 6

💊 Health Score: 0.599
   Status: 🟡 AT-RISK - Proactive outreach recommended

🔄 Running Proactive Workflow...
✅ Workflow Complete!

📤 Proactive Action Result:
   Recommended Action: [Action from Decision Agent]
   Priority: HIGH
   Escalation: NO

💬 Personalized Response:
   [Culturally sensitive message from Empathy Agent]

======================================================================
📊 TEST SUMMARY REPORT
======================================================================
Total Scenarios: 5
✅ Successful: 5
❌ Failed: 0
⚠️  Errors: 0
```

**Workflow:**
1. Loads full customer dataset (1000 customers)
2. Generates diverse test scenarios:
   - VIP customers with complaints
   - New customers with issues
   - Customers with multiple tickets
   - Festival purchases (cultural context)
   - High-value at-risk customers
3. For each scenario:
   - Fetches customer profile from dataset
   - Calculates health score
   - Creates appropriate event type
   - Runs through full 4-agent workflow
   - Validates output and priority
4. Generates comprehensive summary report

---

## Individual Component Testing

### 5. Test Individual Agents

#### Context Agent (Bodha - बोध)
**Description:** Analyzes customer context, extracts key information, determines urgency and sentiment.

**Test Command:**
```bash
python -c "
from agents import create_context_agent
from models import Customer, CustomerEvent, EventType, AgentState
from datetime import datetime

# Create test customer
customer = Customer(
    customer_id='TEST001',
    first_name='Test',
    last_name='Customer',
    email='test@example.com',
    segment='VIP',
    lifetime_value=5000.0,
    preferred_category='Electronics',
    loyalty_tier='Gold'
)

# Create test event
event = CustomerEvent(
    event_id='TEST_EVENT_001',
    customer=customer,
    event_type=EventType.PROACTIVE_RETENTION,
    timestamp=datetime.now(),
    description='High churn risk detected'
)

# Create initial state
state = AgentState(customer=customer, event=event, messages=[])

# Run Context Agent
context_agent = create_context_agent()
result = context_agent(state)

print('Context Summary:', result.context_summary)
print('Sentiment:', result.sentiment)
print('Urgency Level:', result.urgency_level)
print('Risk Score:', result.customer_risk_score)
"
```

**Expected Outcome:**
```
Context Summary: VIP customer TEST001 showing high churn risk...
Sentiment: SentimentType.NEUTRAL
Urgency Level: 4
Risk Score: 0.75
```

---

#### Pattern Agent (Dhyana - ध्यान)
**Description:** Identifies behavioral patterns, historical insights, and predicts churn risk.

**Test Command:**
```bash
python -c "
from agents import create_pattern_agent
from models import Customer, CustomerEvent, EventType, AgentState
from datetime import datetime

# [Same customer/event setup as above]
# Add context from previous agent
state.context_summary = 'VIP customer with declining engagement'
state.customer_risk_score = 0.75

# Run Pattern Agent
pattern_agent = create_pattern_agent()
result = pattern_agent(state)

print('Historical Insights:', result.historical_insights)
print('Predicted Churn Risk:', result.predicted_churn_risk)
print('Similar Patterns:', len(result.similar_patterns))
"
```

**Expected Outcome:**
```
Historical Insights: Customer shows pattern of decreasing order frequency...
Predicted Churn Risk: 0.82
Similar Patterns: 3
```

---

#### Decision Agent (Niti - नीति)
**Description:** Makes strategic decisions on actions, escalations, and priority levels.

**Test Command:**
```bash
python -c "
from agents import create_decision_agent
from models import Customer, CustomerEvent, EventType, AgentState
from datetime import datetime

# [Setup with context and pattern data]
state.predicted_churn_risk = 0.82
state.customer_risk_score = 0.75

# Run Decision Agent
decision_agent = create_decision_agent()
result = decision_agent(state)

print('Recommended Action:', result.recommended_action)
print('Priority Level:', result.priority_level)
print('Escalation Needed:', result.escalation_needed)
"
```

**Expected Outcome:**
```
Recommended Action: Offer personalized retention package with loyalty rewards
Priority Level: high
Escalation Needed: False
```

---

#### Empathy Agent (Karuna - करुणा)
**Description:** Generates personalized, culturally sensitive responses with appropriate tone.

**Test Command:**
```bash
python -c "
from agents import create_empathy_agent
from models import Customer, CustomerEvent, EventType, AgentState
from datetime import datetime

# [Setup with all previous agent data]
state.recommended_action = 'Offer retention package'
state.priority_level = 'high'

# Run Empathy Agent
empathy_agent = create_empathy_agent()
result = empathy_agent(state)

print('Empathy Score:', result.empathy_score)
print('Tone:', result.tone)
print('Personalized Response:', result.personalized_response[:200])
"
```

**Expected Outcome:**
```
Empathy Score: 0.85
Tone: warm, understanding, appreciative
Personalized Response: Dear Test, we truly value your loyalty over the years...
```

---

### 6. Test Data Analytics

**Command:**
```bash
python -c "
from utils import DataAnalytics

analytics = DataAnalytics('data/AgentMAX_CX_dataset.xlsx')

# Get customer segment analysis
segments = analytics.get_customer_segments()
print('Customer Segments:', segments)

# Get churn prediction
churn_data = analytics.get_churn_predictions()
print(f'Customers with churn data: {len(churn_data)}')

# Get order patterns
orders = analytics.get_order_patterns('C100088')
print('Order Patterns:', orders)
"
```

**Expected Outcome:**
```
Customer Segments: {'VIP': 45, 'Loyal': 234, 'Regular': 456, 'Occasional': 265}
Customers with churn data: 1000
Order Patterns: {'total_orders': 12, 'avg_order_value': 1234.56, ...}
```

---

### 7. Test Proactive Monitor

**Command:**
```bash
python -c "
from utils import ProactiveMonitor

monitor = ProactiveMonitor('data/AgentMAX_CX_dataset.xlsx')

# Detect churn risks
at_risk = monitor.detect_churn_risks(min_churn_risk=0.6)
print(f'At-risk customers: {len(at_risk)}')
print(f'Top customer: {at_risk[0][\"customer\"].full_name}')
print(f'Churn risk: {at_risk[0][\"churn_risk\"]:.1%}')

# Get customer health score
from models import Customer
customer = Customer(
    customer_id='C100088',
    first_name='Test',
    last_name='User',
    email='test@test.com',
    segment='VIP',
    lifetime_value=5000,
    preferred_category='Electronics',
    loyalty_tier='Gold'
)
health = monitor.calculate_health_score(customer)
print(f'Health score: {health:.1%}')
"
```

**Expected Outcome:**
```
At-risk customers: 24
Top customer: Tanya Kumar
Churn risk: 84.2%
Health score: 65.3%
```

---

## Workflow Testing

### 8. Full Multi-Agent Pipeline Test

**Command:**
```bash
python -c "
from workflows import create_cx_workflow, run_workflow
from models import Customer, CustomerEvent, EventType, AgentState
from datetime import datetime

# Create test customer
customer = Customer(
    customer_id='C100088',
    first_name='Priya',
    last_name='Sharma',
    email='priya@example.com',
    segment='Loyal',
    lifetime_value=8500.0,
    preferred_category='Home Decor',
    loyalty_tier='Silver',
    country='India'
)

# Create proactive retention event
event = CustomerEvent(
    event_id='TEST_WORKFLOW_001',
    customer=customer,
    event_type=EventType.PROACTIVE_RETENTION,
    timestamp=datetime.now(),
    description='Proactive churn prevention',
    metadata={'health_score': 0.45, 'churn_risk': 0.75}
)

# Create initial state
initial_state = AgentState(
    customer=customer,
    event=event,
    messages=[]
)

# Run full workflow
workflow = create_cx_workflow()
final_state = run_workflow(workflow, initial_state)

# Display results
print('='*70)
print('FULL WORKFLOW TEST RESULT')
print('='*70)
print(f'Customer: {customer.first_name} {customer.last_name}')
print(f'Context: {final_state.context_summary}')
print(f'Sentiment: {final_state.sentiment}')
print(f'Urgency: {final_state.urgency_level}/5')
print(f'Churn Risk: {final_state.predicted_churn_risk:.1%}')
print(f'Recommended Action: {final_state.recommended_action}')
print(f'Priority: {final_state.priority_level}')
print(f'Escalation: {final_state.escalation_needed}')
print(f'\\nPersonalized Response:\\n{final_state.personalized_response[:300]}...')
print(f'\\nAgent Messages: {len(final_state.messages)}')
for msg in final_state.messages:
    print(f'  - {msg[\"agent\"]}: {msg[\"message\"][:80]}...')
"
```

**Expected Outcome:**
```
======================================================================
FULL WORKFLOW TEST RESULT
======================================================================
Customer: Priya Sharma
Context: Loyal customer showing declining engagement...
Sentiment: SentimentType.NEUTRAL
Urgency: 4/5
Churn Risk: 75.0%
Recommended Action: Offer personalized retention package
Priority: high
Escalation: False

Personalized Response:
नमस्ते Priya! We truly value your loyalty... [Hindi greeting with personalized offer]

Agent Messages: 4
  - context_agent: Analyzed customer context and identified risk factors...
  - pattern_agent: Identified declining engagement pattern...
  - decision_agent: Recommended retention package with loyalty incentive...
  - empathy_agent: Generated culturally sensitive response with Hindi greeting...
```

**Workflow Stages:**
1. **Context Agent (Bodha)**: 
   - Analyzes customer profile
   - Assesses current situation
   - Determines sentiment and urgency
   
2. **Pattern Agent (Dhyana)**:
   - Reviews historical behavior
   - Identifies trends
   - Predicts churn risk
   
3. **Decision Agent (Niti)**:
   - Evaluates intervention strategy
   - Determines priority level
   - Decides on escalation
   
4. **Empathy Agent (Karuna)**:
   - Crafts personalized message
   - Applies cultural context
   - Sets appropriate tone

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Unicode/Emoji Errors
**Error:** `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solution:**
```bash
# Always use -X utf8 flag for test files
python -X utf8 test_features.py
python -X utf8 test_scenarios.py

# Or set environment variable
export PYTHONIOENCODING=utf-8  # Linux/Mac
set PYTHONIOENCODING=utf-8     # Windows CMD
```

#### 2. Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific missing packages
pip install python-dotenv pandas openpyxl langchain-openai
```

#### 3. Dataset Not Found
**Error:** `FileNotFoundError: data/AgentMAX_CX_dataset.xlsx`

**Solution:**
```bash
# Ensure you're in the project root directory
cd /path/to/ProCX

# Verify dataset exists
ls -la data/AgentMAX_CX_dataset.xlsx
```

#### 4. OpenAI API Key Missing
**Error:** `OpenAI API key not found`

**Solution:**
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=your_key_here" > .env

# Or set environment variable
export OPENAI_API_KEY=your_key_here  # Linux/Mac
set OPENAI_API_KEY=your_key_here     # Windows CMD
```

#### 5. Memory/Performance Issues
**Issue:** Tests run slowly or timeout

**Solution:**
```bash
# Reduce max interventions
python main.py --interventions --max-interventions 2

# Increase risk threshold (fewer customers)
python main.py --interventions --risk-threshold 0.8

# Run single agent tests instead of full pipeline
```

---

## Quick Reference

### Most Common Commands
```bash
# View dashboard
python main.py --dashboard

# Run 5 interventions
python main.py --interventions

# Run 2 interventions with high risk only
python main.py --interventions --max-interventions 2 --risk-threshold 0.7

# Test enhanced features
python -X utf8 test_features.py

# Test full scenarios
python -X utf8 test_scenarios.py
```

### File Locations
- **Main Entry Point:** `main.py`
- **Test Files:** `test_features.py`, `test_scenarios.py`
- **Dataset:** `data/AgentMAX_CX_dataset.xlsx`
- **Agents:** `agents/` directory
- **Workflows:** `workflows/cx_workflow.py`
- **Utils:** `utils/` directory
- **Models:** `models/customer.py`

---

## Performance Benchmarks

| Command | Avg Duration | Customers Processed |
|---------|--------------|---------------------|
| `--dashboard` | ~5 seconds | 112 scanned |
| `--interventions` (5) | ~30 seconds | 5 processed |
| `test_features.py` | ~3 seconds | N/A (unit tests) |
| `test_scenarios.py` | ~60 seconds | 5 scenarios |
| Full workflow (1 customer) | ~6 seconds | 1 processed |

---

## Success Criteria

### Dashboard
- ✅ Loads all customers from dataset
- ✅ Categorizes by risk level (Critical/High/Medium/Low)
- ✅ Shows top 10 at-risk customers with details

### Interventions
- ✅ Identifies at-risk customers above threshold
- ✅ Runs full 4-agent pipeline for each
- ✅ Generates culturally appropriate responses
- ✅ Stores interactions in memory
- ✅ Completes within timeout

### Feature Tests
- ✅ Festival context detection works
- ✅ Escalation tracking prevents duplicates
- ✅ Integration scenarios pass

### Scenario Tests
- ✅ All 5 scenarios complete successfully
- ✅ Workflow executes all 4 agents
- ✅ Appropriate priority assigned
- ✅ Personalized responses generated

---

**Last Updated:** October 22, 2025  
**Platform Version:** ProCX v1.0 (Proactive-Only)  
**Python Version:** 3.11+
