# ProCX - Final Architecture (Agent-Driven Decisions)

## ��� Core Philosophy: AI Makes ALL Decisions

**Previous Problem:** We hardcoded rules like "churn risk >80% = give 10% discount"
**Current Solution:** GPT-4o agent analyzes situation and decides EVERYTHING

---

## How Each Scenario is Handled (100% Agent-Driven)

### Scenario 1: High Churn Risk Customer
**Agent receives:**
- Customer: Rahul Malhotra
- Churn Risk: 77.2%
- LTV: $2,526
- Sentiment: Neutral
- History: Some support tickets

**Agent decides (via GPT-4o):**
```json
{
  "recommended_action": "Offer discount and gather feedback",
  "incentive_offered": {
    "type": "discount",
    "discount_percentage": 10.0,
    "reasoning": "Moderate churn risk + good LTV warrants retention incentive"
  },
  "escalation_needed": false,
  "priority_level": "medium"
}
```

**System processes:**
- Discount ≤10% → ✅ AUTO-APPROVED
- Message: "We've applied a 10% discount to your account"
- No human intervention needed

---

### Scenario 2: VIP Customer Crisis
**Agent receives:**
- Customer: VIP, ₹8,500 LTV
- Churn Risk: 88%
- CSAT: 2.1/5.0 (very low)
- Sentiment: Very Negative

**Agent decides:**
```json
{
  "recommended_action": "Escalate + offer premium retention package",
  "incentive_offered": {
    "type": "discount",
    "discount_percentage": 15.0,
    "reasoning": "VIP with critical risk needs larger incentive"
  },
  "escalation_needed": true,
  "priority_level": "critical"
}
```

**System processes:**
- Discount >10% → ⚠️ NEEDS HUMAN APPROVAL
- VIP + high churn → ��� ESCALATE
- Human gets: Full context + recommended 15% discount
- Human decides: Approve discount or customize offer

---

### Scenario 3: Low-Risk Customer
**Agent receives:**
- Customer: Priya Sharma
- Churn Risk: 35%
- LTV: $1,200
- Sentiment: Positive
- Recent activity: Active

**Agent decides:**
```json
{
  "recommended_action": "Send appreciation message, no discount needed",
  "incentive_offered": {
    "type": "none",
    "reasoning": "Low churn risk, customer is engaged and satisfied"
  },
  "escalation_needed": false,
  "priority_level": "low"
}
```

**System processes:**
- No discount offered
- Sends positive engagement message
- Continues monitoring

---

### Scenario 4: Medium Risk with Budget Constraints
**Agent receives:**
- Customer: Regular customer
- Churn Risk: 55%
- LTV: $800
- Low profit margin category

**Agent decides:**
```json
{
  "recommended_action": "Offer non-monetary incentive",
  "incentive_offered": {
    "type": "free_shipping",
    "reasoning": "Medium risk but low LTV - free shipping more cost-effective than discount"
  },
  "escalation_needed": false,
  "priority_level": "medium"
}
```

**System processes:**
- Alternative incentive (not discount)
- Message: "We're offering you free shipping on your next order"
- No discount budget used

---

## Agent Decision Framework

### What Agent Considers:
1. **Churn Risk** (0-100%) - from Pattern Agent
2. **Customer Value** (LTV) - from customer profile
3. **Sentiment** (very_negative to very_positive) - from Context Agent
4. **Support History** (CSAT scores, ticket count) - from analytics
5. **Segment** (VIP/Loyal/Regular/Occasional) - from profile
6. **Event Type** (proactive_retention, check_in, etc.)

### What Agent Decides:
1. **Recommended Action** (what to do)
2. **Incentive Type** (discount, loyalty_points, free_shipping, none)
3. **Discount %** (if applicable: 0-15%)
4. **Escalation** (yes/no - but system rules also apply)
5. **Priority** (low/medium/high/critical)

### System Rules (The ONLY Hardcoded Logic):
```python
# Auto-Approval Threshold
if agent_recommended_discount <= 10%:
    → Auto-approve and apply
else:
    → Escalate to human

# Escalation Triggers (in addition to agent's decision)
if VIP and churn_risk > 80%:
    → Escalate
if LTV > $5000 and churn_risk > 85%:
    → Escalate
if CSAT < 2.5:
    → Escalate
```

---

## Why This is Better

### ❌ Old Approach (Hardcoded):
```python
if churn_risk >= 0.8:
    discount = 10%
elif churn_risk >= 0.6:
    discount = 7%
elif churn_risk >= 0.5:
    discount = 5%
```
**Problem:** Can't adapt to nuance, wastes discount budget

### ✅ New Approach (AI-Driven):
```python
agent_decision = gpt4o.decide({
    "customer_context": full_profile,
    "churn_risk": 0.77,
    "sentiment": "neutral",
    "history": support_data
})

# Agent might decide:
# - 10% discount (high risk but engaged)
# - Free shipping (medium risk, low margin)
# - No discount (customer just needs reassurance)
# - 15% + escalate (VIP crisis)
```
**Benefit:** Contextual, strategic, cost-effective

---

## How Demos Work Now

### Demo Files DON'T Make Decisions
They only:
1. Create customer scenario (profile + situation)
2. Pass to agent workflow
3. Display what agent decided

Example (`demo_escalation.py`):
```python
# Create VIP customer with crisis
customer = Customer(segment="VIP", ltv=8500, ...)
event = CustomerEvent(type=PROACTIVE_RETENTION, ...)

# Agent decides EVERYTHING
result = procx.process_proactive_event(event)

# Display what agent chose
print(f"Agent Decision: {result.recommended_action}")
print(f"Discount Offered: {result.discount_applied}%")
print(f"Escalation: {result.escalation_needed}")
```

---

## Future Scalability

### Adding New Incentive Types:
Just update the prompt - agent will start using them:
```json
"incentive_offered": {
  "type": "extended_warranty",  // NEW
  "reasoning": "Electronics customer values warranty over discount"
}
```

### Adding New Escalation Criteria:
Agent can recommend escalation for ANY reason:
```json
{
  "escalation_needed": true,
  "reasoning": "Customer mentioned competitor offer - needs sales team attention"
}
```

### No Code Changes Needed
- Agent learns from prompt updates
- System rules stay minimal (10% threshold)
- Everything else = AI intelligence

---

## For Hackathon Judges

**Key Message:**
"ProCX uses GPT-4o to make contextual decisions. The agent analyzes each customer's situation and decides:
- Should we offer an incentive?
- What type? (discount, free shipping, loyalty points, or none)
- How much? (0-15%)

System only enforces:
- 10% auto-approval threshold (cost control)
- Escalation for VIP/high-value crises (human oversight)

Everything else = AI intelligence, not hardcoded rules."

**Demo Flow:**
1. Show batch scan → Agent processes 3 customers
2. Customer 1: Agent offers 7% discount (auto-approved)
3. Customer 2: Agent offers free shipping (no discount)
4. Customer 3: Agent escalates VIP (15% discount needs approval)

**Shows:** AI making different decisions for different situations, not one-size-fits-all rules.

