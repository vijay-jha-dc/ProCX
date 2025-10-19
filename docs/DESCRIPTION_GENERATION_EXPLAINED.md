# 🔍 Description Generation - Hardcoded vs Dynamic

## Your Question

In the example:

```python
description = f"""
High-value customer (LTV: ${customer.lifetime_value:,.2f}) showing distress signals:
- Health Score: {health_score:.0f}/100 (Critical)
- 3 failed payments in last 30 days
- NPS score dropped from 9 to 4
- Last purchase 45 days ago (unusual for VIP segment)
- 2 unresolved support tickets
- Order frequency declined 60% vs 3-month average
"""
```

**What part of this is hardcoded?**

---

## ❌ Current State: MOSTLY HARDCODED (Not Implemented Yet!)

**The truth:** This detailed description example in `MODES_DEEP_DIVE.md` is **aspirational** - it shows what COULD be generated, but is NOT currently implemented in the code.

### What's Actually Happening Now

**In `main.py`, line 216:**

```python
def _create_proactive_event(self, customer, alert):
    return CustomerEvent(
        event_id=event_id,
        customer=customer,
        event_type=EventType.INQUIRY,
        timestamp=datetime.now(),
        description=f"Proactive retention: Churn risk {alert['churn_risk']:.1%}",  # ← THIS IS IT!
        metadata={
            'is_proactive': True,
            'health_score': alert['health_score'],
            'churn_risk': alert['churn_risk'],
            'risk_level': alert['risk_level'],
            'reasons': alert['reasons']
        }
    )
```

### Current Description Format

```
"Proactive retention: Churn risk 68.5%"
```

**That's it!** Very simple, mostly hardcoded text.

---

## ✅ What SHOULD Be Generated (Recommended Implementation)

To make the description truly **data-driven**, here's what should be dynamic vs static:

### Example Rich Description Breakdown

```python
# STATIC (Template text):
"High-value customer (LTV: $___) showing distress signals:"

# DYNAMIC (From database):
- ${customer.lifetime_value:,.2f}  ← customers.lifetime_value

"- Health Score: ___/100 (___)"
# DYNAMIC:
- {health_score:.0f}  ← Calculated from 10 factors
- "Critical" if < 40, "Warning" if < 60, "Good" if >= 60

"- ___ failed payments in last 30 days"
# DYNAMIC:
- Count from payments sheet WHERE customer_id = X AND status = 'failed' AND date > NOW() - 30

"- NPS score dropped from ___ to ___"
# DYNAMIC:
- Previous score: nps_survey.nps_score WHERE customer_id = X ORDER BY date DESC LIMIT 1 OFFSET 1
- Current score: nps_survey.nps_score WHERE customer_id = X ORDER BY date DESC LIMIT 1

"- Last purchase ___ days ago (unusual for ___ segment)"
# DYNAMIC:
- Days: orders.order_date WHERE customer_id = X ORDER BY date DESC LIMIT 1
- Segment: customer.segment

"- ___ unresolved support tickets"
# DYNAMIC:
- Count: support_tickets WHERE customer_id = X AND status IN ('open', 'pending')

"- Order frequency declined ___% vs 3-month average"
# DYNAMIC:
- Calculate: (last_30_days_orders / previous_60_days_orders) - 1
```

---

## 🛠️ Recommended Implementation

### Option 1: Rich Description Generator (Best for Demo)

Add this method to `main.py`:

```python
def _generate_rich_description(self, customer: Customer, alert: Dict, analytics: DataAnalytics) -> str:
    """
    Generate rich, data-driven description for proactive intervention.

    Args:
        customer: Customer object
        alert: Health alert with scores and reasons
        analytics: DataAnalytics instance for querying

    Returns:
        Detailed description string
    """
    health_score = alert['health_score'] * 100  # Convert to 0-100
    churn_risk = alert['churn_risk'] * 100

    # Health category
    if health_score < 40:
        health_status = "CRITICAL"
    elif health_score < 60:
        health_status = "Warning"
    else:
        health_status = "Concerning"

    # Base description
    description = f"High-value {customer.segment} customer (LTV: ${customer.lifetime_value:,.2f}) showing distress signals:\n"
    description += f"- Health Score: {health_score:.0f}/100 ({health_status})\n"
    description += f"- Churn Risk: {churn_risk:.0f}%\n"

    # Add specific issues from database queries

    # 1. Payment issues (if available)
    payment_stats = analytics.get_customer_payment_reliability(customer)
    if payment_stats and payment_stats.get('failed_payments_30d', 0) > 0:
        failed_count = payment_stats['failed_payments_30d']
        description += f"- {failed_count} failed payment{'s' if failed_count > 1 else ''} in last 30 days\n"

    # 2. NPS score changes (if available)
    nps_data = analytics.get_customer_nps_history(customer)
    if nps_data and len(nps_data) >= 2:
        current_nps = nps_data[0]['score']
        previous_nps = nps_data[1]['score']
        if previous_nps - current_nps >= 3:  # Significant drop
            description += f"- NPS score dropped from {previous_nps} to {current_nps}\n"

    # 3. Activity/Purchase recency
    if customer.days_since_active:
        days = customer.days_since_active
        segment_avg = analytics.get_segment_avg_activity(customer.segment)
        if days > segment_avg * 1.5:  # 50% more inactive than segment average
            description += f"- Last purchase {days} days ago (unusual for {customer.segment} segment)\n"

    # 4. Support ticket issues
    ticket_stats = analytics.get_customer_ticket_summary(customer)
    if ticket_stats and ticket_stats.get('open_tickets', 0) > 0:
        open_count = ticket_stats['open_tickets']
        description += f"- {open_count} unresolved support ticket{'s' if open_count > 1 else ''}\n"

    # 5. Order frequency decline
    order_stats = analytics.get_customer_order_stats(customer)
    if order_stats and order_stats.get('frequency_decline_pct'):
        decline_pct = abs(order_stats['frequency_decline_pct'])
        if decline_pct > 30:  # Significant decline
            description += f"- Order frequency declined {decline_pct:.0f}% vs 3-month average\n"

    # 6. Generic risk factors (fallback)
    if len(description.split('\n')) <= 3:  # If we didn't find specific issues
        for reason in alert['reasons'][:3]:
            description += f"- {reason}\n"

    return description.strip()
```

### Then Update `_create_proactive_event`:

```python
def _create_proactive_event(self, customer, alert):
    """Helper to create proactive event from health alert."""
    from models import CustomerEvent
    from datetime import datetime
    import time

    event_id = f"PROACTIVE_{customer.customer_id}_{int(time.time())}"

    # Generate rich description
    description = self._generate_rich_description(customer, alert, self.proactive_monitor.analytics)

    return CustomerEvent(
        event_id=event_id,
        customer=customer,
        event_type=EventType.INQUIRY,
        timestamp=datetime.now(),
        description=description,  # ← Now using rich description!
        metadata={
            'is_proactive': True,
            'health_score': alert['health_score'],
            'churn_risk': alert['churn_risk'],
            'risk_level': alert['risk_level'],
            'reasons': alert['reasons']
        }
    )
```

---

### Option 2: Simple But Effective (Quick Implementation)

If you don't have time for Option 1, at least improve the current description:

```python
def _create_proactive_event(self, customer, alert):
    """Helper to create proactive event from health alert."""
    from models import CustomerEvent
    from datetime import datetime
    import time

    event_id = f"PROACTIVE_{customer.customer_id}_{int(time.time())}"

    # Build description with available data
    health_score = alert['health_score'] * 100
    churn_risk = alert['churn_risk'] * 100

    description = f"""{customer.segment} customer at risk (LTV: ${customer.lifetime_value:,.2f})
Health Score: {health_score:.0f}/100 | Churn Risk: {churn_risk:.0f}%
Key Issues: {', '.join(alert['reasons'][:3])}
Action Required: {alert['recommended_action'].replace('_', ' ').title()}"""

    return CustomerEvent(
        event_id=event_id,
        customer=customer,
        event_type=EventType.INQUIRY,
        timestamp=datetime.now(),
        description=description,
        metadata={
            'is_proactive': True,
            'health_score': alert['health_score'],
            'churn_risk': alert['churn_risk'],
            'risk_level': alert['risk_level'],
            'reasons': alert['reasons']
        }
    )
```

**Output Example:**

```
VIP customer at risk (LTV: $45,230.50)
Health Score: 58/100 | Churn Risk: 68%
Key Issues: Low health score, High-value segment at risk, Below-average in cohort
Action Required: Immediate Personal Outreach
```

---

## 📊 Data Availability Check

Before implementing rich descriptions, verify which data you have access to:

### Currently Available in DataAnalytics:

✅ **Implemented:**

- `compare_with_cohort(customer)` - Percentile ranking
- `find_similar_customers(customer)` - Similar customer analysis
- `get_segment_statistics(segment)` - Segment averages
- `get_customer_order_stats(customer)` - Order history

❓ **Need to Check/Implement:**

- `get_customer_payment_reliability(customer)` - Failed payments count
- `get_customer_nps_history(customer)` - NPS score changes
- `get_customer_ticket_summary(customer)` - Open ticket count
- `get_segment_avg_activity(segment)` - Segment activity baseline

### Quick Check Command:

```bash
cd /c/Users/VijayJha/Documents/AgentMax-Hackathon/ProCX
grep -n "def get_customer" utils/data_analytics.py
```

---

## 🎯 Summary

### Current State:

```python
description = f"Proactive retention: Churn risk {alert['churn_risk']:.1%}"
```

- **Hardcoded:** "Proactive retention: Churn risk"
- **Dynamic:** `{alert['churn_risk']:.1%}` (calculated percentage)

### Recommended State (Option 2 - Quick):

```python
description = f"""{customer.segment} customer at risk (LTV: ${customer.lifetime_value:,.2f})
Health Score: {health_score:.0f}/100 | Churn Risk: {churn_risk:.0f}%
Key Issues: {', '.join(alert['reasons'][:3])}"""
```

- **Hardcoded:** Template text ("customer at risk", "Health Score:", etc.)
- **Dynamic:** All numbers, customer data, risk factors

### Ideal State (Option 1 - Rich):

```python
description = self._generate_rich_description(customer, alert, analytics)
```

- **Hardcoded:** Only bullet point formatting and labels
- **Dynamic:** All data pulled from database (payments, NPS, tickets, orders, activity)

---

## 🚀 Recommendation

**For hackathon demo:**

1. Implement **Option 2** (takes 5 minutes, big impact)
2. If you have time, add **Option 1** (takes 30 minutes, very impressive)

**Why this matters:**

- Judges will ask: "How do you know there are 3 failed payments?"
- Current answer: "We calculate from payment history database"
- But if description says "Churn risk 68%", they'll think it's all generic
- Rich description PROVES you're using real data

**The more dynamic data in the description, the more credible your system looks!**
