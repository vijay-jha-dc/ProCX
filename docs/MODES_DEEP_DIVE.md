# 🔍 ProCX Modes - Deep Dive Architecture

## Table of Contents

1. [Proactive Mode (Core Innovation)](#1-proactive-mode---core-innovation)
2. [Event-Driven Mode (Production Integration)](#2-event-driven-mode---production-integration)
3. [Demo Mode (Showcase Agent Intelligence)](#3-demo-mode---showcase-agent-intelligence)
4. [Interactive Mode (Manual Testing)](#4-interactive-mode---manual-testing)
5. [How Modes Work Together](#5-how-modes-work-together)
6. [Recommended Cleanup](#6-recommended-cleanup)

---

## 1️⃣ PROACTIVE MODE - Core Innovation

### What It Does

**Scans the ENTIRE database (1,000 customers) WITHOUT any external events and identifies at-risk customers BEFORE they complain.**

### What Database We Monitor

**Primary Sheet: `customers` (1,000 records)**

```
Columns monitored:
- customer_id, first_name, last_name, email, phone
- segment (VIP/Loyal/Regular/Occasional)
- lifetime_value (total spending)
- avg_order_value
- loyalty_tier (Platinum/Gold/Silver/Bronze)
- last_active_date (when they last interacted)
- signup_date (customer tenure)
- preferred_category
- country, city, language
- opt_in_marketing
```

**Supporting Sheets (for deep analysis):**

1. **`orders` (5,000 records)**

   - Order history, frequency, spending patterns
   - Detects: Declining purchase frequency, cart abandonment trends

2. **`churn_labels` (1,000 records)**

   - Ground truth: Who actually churned?
   - Uses ML patterns to predict future churn

3. **`support_tickets` (2,000 records)**

   - Support history, response times, ticket count
   - Detects: Frustrated customers with unresolved issues

4. **`nps_survey` (800 records)**

   - Net Promoter Scores, satisfaction feedback
   - Detects: Score drops, detractor alerts

5. **`payments` (4,750 records)**

   - Payment success/failure history
   - Detects: Declining payment reliability

6. **`customer_events` (10,000 records)**
   - Historical activity log
   - Detects: Inactivity patterns, engagement drops

### 10-Factor Health Scoring System

The proactive monitor calculates a **Health Score (0-100)** using these factors:

```python
1. Segment Strength (15% weight)
   - VIP = 15, Loyal = 12, Regular = 8, Occasional = 4
   - Fetches: customers.segment

2. Lifetime Value Percentile (12% weight)
   - Compares customer LTV to cohort average
   - Fetches: customers.lifetime_value + cohort analysis

3. Loyalty Tier (10% weight)
   - Platinum = 10, Gold = 8, Silver = 6, Bronze = 4
   - Fetches: customers.loyalty_tier

4. Relative Value in Segment (10% weight)
   - Is this VIP spending like a VIP?
   - Fetches: customers.lifetime_value vs segment average

5. Last Activity Recency (15% weight)
   - < 7 days = 15, < 30 days = 12, < 60 days = 8, > 90 days = 0
   - Fetches: customers.last_active_date

6. Order Frequency (12% weight)
   - 3+ orders/month = 12, 1+ = 9, 0.5+ = 6
   - Fetches: orders sheet → calculates frequency

7. Spending Trends (10% weight)
   - Increasing = 10, stable = 7, declining = 2
   - Fetches: orders.order_value over time

8. Support History (8% weight)
   - 0 tickets = 8, 1-2 = 6, 3-5 = 3, 6+ = 0
   - Fetches: support_tickets.ticket_count

9. NPS Score (5% weight)
   - Promoter (9-10) = 5, Passive (7-8) = 3, Detractor (0-6) = 0
   - Fetches: nps_survey.nps_score

10. Customer Tenure (3% weight)
    - Longer tenure = more stable
    - Fetches: customers.signup_date
```

### How Descriptions Are Generated

**Automatically generated from data patterns:**

```python
# Example 1: Low health score detection
description = f"""
High-value customer (LTV: ${customer.lifetime_value:,.2f}) showing distress signals:
- Health Score: {health_score:.0f}/100 (Critical)
- 3 failed payments in last 30 days
- NPS score dropped from 9 to 4
- Last purchase 45 days ago (unusual for VIP segment)
- 2 unresolved support tickets
- Order frequency declined 60% vs 3-month average
"""

# Example 2: Segment-specific alert
description = f"""
VIP customer at risk of churn:
- Segment: {customer.segment} (${segment_avg:,.2f} avg LTV)
- Current LTV: ${customer.lifetime_value:,.2f} (top 15%)
- Days since active: {customer.days_since_active} (red flag!)
- Payment reliability: {payment_score}% (declining)
- Similar VIP customers churned with this pattern
"""
```

### Workflow

```
1. Load all 1,000 customers from database
   ↓
2. For each customer:
   - Fetch order history (orders sheet)
   - Fetch support tickets (support_tickets sheet)
   - Fetch NPS scores (nps_survey sheet)
   - Fetch payment history (payments sheet)
   ↓
3. Calculate 10-factor health score (0-100)
   ↓
4. Calculate churn risk (uses churn_labels for ML patterns)
   ↓
5. Filter: churn_risk > 60% AND lifetime_value > $1,000
   ↓
6. Sort by: (churn_risk × lifetime_value) DESC
   ↓
7. Generate intervention descriptions (auto-generated)
   ↓
8. Process top 5-10 through agent pipeline
   ↓
9. Display recommendations (email/SMS/call)
```

### Command

```bash
python main.py --mode proactive
```

---

## 2️⃣ EVENT-DRIVEN MODE - Production Integration

### What It Does

**Receives real-time webhooks from external systems (Stripe, Shopify, Qualtrics) and converts technical JSON into human-readable descriptions, then ADDS this data to the live database for monitoring.**

### Your Key Insight Is CORRECT! ✅

> "webhook will give the json we convert it into description and we will add this data and the description in the live data which will be monitored by our proactive mode thus this event driven is prerequisite for the proactive mode"

**YES! This is the architecture:**

```
External System (Stripe) → Webhook → EventProcessor → Database → Proactive Monitor
                                          ↓
                                  Auto-generates description
```

### Webhook Structure We Expect

**Example 1: Payment Failed (from Stripe)**

```json
{
  "event_type": "payment.failed",
  "timestamp": "2025-01-10T14:32:00Z",
  "source": "stripe",
  "data": {
    "customer_id": "C100109",
    "amount": 2499.99,
    "currency": "USD",
    "order_id": "ORD-2025-789",
    "reason": "insufficient_funds",
    "payment_method": "card_****1234",
    "attempt": 2
  }
}
```

**Auto-generated description:**

```
"Payment of $2,499.99 failed for order ORD-2025-789 - insufficient funds.
Customer may need assistance with payment method. This is attempt #2."
```

**What gets added to database:**

```python
# This event is added to customer_events sheet:
{
    "event_id": "EVT_20250110_143200",
    "customer_id": "C100109",
    "event_type": "payment_failed",
    "description": "Payment of $2,499.99 failed...",  # Auto-generated!
    "timestamp": "2025-01-10T14:32:00Z",
    "metadata": {
        "amount": 2499.99,
        "reason": "insufficient_funds",
        "order_id": "ORD-2025-789"
    }
}

# This updates customer health score:
# - Factor 6 (Order Frequency) drops (failed order)
# - Factor 7 (Spending Trends) affected
# - Factor 8 (Support History) may increase if ticket created
# - Next proactive scan will catch this customer!
```

### How It Integrates with Proactive Mode

**Scenario Timeline:**

```
Day 1, 2:30 PM - Webhook arrives: "payment.failed"
                 ↓
              EventProcessor converts to description
                 ↓
              Event added to customer_events table
                 ↓
              Customer health score recalculated
                 ↓
              Health score drops from 75 → 58 (at-risk!)

Day 1, 3:00 PM - Proactive monitor scans database
                 ↓
              Detects customer C100109 now at-risk (score: 58)
                 ↓
              Generates proactive intervention
                 ↓
              Sends email: "We noticed your payment failed. Let us help!"
```

### 20+ Event Types Supported

```python
EVENT_TYPE_MAP = {
    # Payment events
    "payment.failed": EventType.COMPLAINT,
    "payment.method_expired": EventType.INQUIRY,

    # Order events
    "order.delayed": EventType.COMPLAINT,
    "order.cancelled": EventType.ORDER_CANCELLED,
    "shipment.delayed": EventType.ORDER_DELAYED,

    # Cart events
    "cart.abandoned": EventType.INQUIRY,

    # Customer feedback
    "nps.detractor": EventType.COMPLAINT,
    "nps.promoter": EventType.FEEDBACK,
    "review.negative": EventType.COMPLAINT,

    # Product events
    "product.out_of_stock": EventType.INQUIRY,
    "product.back_in_stock": EventType.INQUIRY,

    # Subscription events
    "subscription.cancelled": EventType.COMPLAINT,
    "subscription.payment_failed": EventType.COMPLAINT,

    # Support events
    "support.ticket.created": EventType.COMPLAINT,
    "support.ticket.escalated": EventType.COMPLAINT,

    # Engagement events
    "app.inactive": EventType.INQUIRY,
    "email.unsubscribe": EventType.COMPLAINT,

    # Return/refund events
    "refund.requested": EventType.COMPLAINT,
    "return.initiated": EventType.COMPLAINT
}
```

### Command

```bash
python main.py --mode event-driven
```

---

## 3️⃣ DEMO MODE - Showcase Agent Intelligence

### What It Does

**Processes 5 pre-built customer scenarios through the full agent pipeline to showcase agent intelligence, empathy, and multi-language support.**

### Where Do the 5 Customers Come From?

**Answer: FROM THE DATASHEET (not generated)**

The demo mode:

1. **Uses real customers** from the `customers` sheet (1,000 records)
2. **Selects by segment** (VIP, Loyal, Occasional)
3. **Uses pre-written descriptions** (hardcoded scenarios)

```python
# From event_simulator.py, lines 252-285
scenarios = {
    "vip_complaint": {
        "segment": "VIP",  # ← Filters customers sheet by segment
        "event_type": EventType.COMPLAINT,
        "custom_description": "Extremely unhappy with delayed premium order. This is the third time!"
        # ↑ This description is PRE-WRITTEN (not auto-generated)
    },
    "loyal_order_delay": {
        "segment": "Loyal",  # ← Picks a real Loyal customer from datasheet
        "event_type": EventType.ORDER_DELAYED,
        "custom_description": "Order delayed by 5 days. Need it urgently for a gift."
    },
    "new_customer_inquiry": {
        "segment": "Occasional",
        "event_type": EventType.INQUIRY,
        "custom_description": "First time buyer asking about shipping times and return policy."
    },
    "high_value_at_risk": {
        "segment": "VIP",
        "event_type": EventType.ORDER_CANCELLED,
        "custom_description": "Cancelled order due to poor experience. Considering switching to competitor."
    },
    "positive_feedback": {
        "segment": "Loyal",
        "event_type": EventType.FEEDBACK,
        "custom_description": "Absolutely loved the recent purchase! Best customer service ever."
    }
}
```

**Flow:**

```
1. Get scenario "vip_complaint"
   ↓
2. Look up random VIP customer from customers sheet
   - Example: C100109 (Rajesh Kumar, VIP, LTV: $45,230)
   ↓
3. Use pre-written description:
   "Extremely unhappy with delayed premium order. This is the third time!"
   ↓
4. Fetch customer data (orders, tickets, NPS, etc.)
   ↓
5. Process through agent pipeline
   ↓
6. Show empathy score (95%), language (Bengali), response
```

### Purpose

**To showcase:**

- ✅ Multi-language detection (auto-detects Bengali, Hindi, etc.)
- ✅ High empathy scores (85-95%)
- ✅ Context awareness (agent knows customer history)
- ✅ Smart escalation decisions
- ✅ Full agent workflow (Context → Pattern → Decision → Empathy)

### Command

```bash
python main.py --mode demo --demo-count 5
```

---

## 4️⃣ INTERACTIVE MODE - Manual Testing

### What It Does

**Provides a menu-driven interface for manual testing and exploration.**

### Menu Options

```
🎮 ProCX - Interactive Mode
📊 Dataset Loaded: 1,000 customers

Options:
1. Process random event
2. Process specific customer (by ID)
3. Run scenario (5 pre-built scenarios)
4. Show dataset statistics
5. Exit
```

### Purpose

- Manual testing during development
- Let judges explore the system
- Process specific customers by ID
- Good for Q&A sessions

### When to Use

- During development/debugging
- When judges want to "play" with the system
- Testing edge cases

### Command

```bash
python main.py --mode interactive
```

---

## 5️⃣ How Modes Work Together

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION FLOW                          │
└─────────────────────────────────────────────────────────────┘

External Systems                     ProCX Platform
─────────────────                    ──────────────

Stripe ─────┐
            │
Shopify ────┤                      ┌──────────────────┐
            ├──── Webhooks ───────→│ EventProcessor   │
Zendesk ────┤                      │ (Event-Driven)   │
            │                      └────────┬─────────┘
Qualtrics ──┘                               │
                                            │ Add to DB
                                            ↓
                                   ┌──────────────────┐
                                   │   Database       │
                                   │  ┌─────────────┐ │
                                   │  │ customers   │ │
                                   │  │ orders      │ │
                                   │  │ events      │ │
                                   │  │ tickets     │ │
                                   │  │ nps_survey  │ │
                                   │  └─────────────┘ │
                                   └────────┬─────────┘
                                            │
                              Every 5 mins / On-demand
                                            │
                                            ↓
                                   ┌──────────────────┐
                                   │ ProactiveMonitor │
                                   │  (Proactive)     │
                                   └────────┬─────────┘
                                            │
                                            ↓
                              Scan → Score → Detect → Alert
                                            │
                                            ↓
                                   ┌──────────────────┐
                                   │  Agent Pipeline  │
                                   │ Context→Pattern→ │
                                   │ Decision→Empathy │
                                   └────────┬─────────┘
                                            │
                                            ↓
                                   Email / SMS / Call
                                   to Customer
```

### Example Timeline

```
Monday 9:00 AM - Customer's payment fails (Stripe webhook)
                 → Event-Driven mode processes
                 → Adds "payment_failed" to customer_events
                 → Updates customer health score: 85 → 62

Monday 9:05 AM - Proactive monitor runs scheduled scan
                 → Detects customer now at-risk (score: 62)
                 → Generates: "We noticed payment issue, let us help"
                 → Sends email with alternative payment options

Monday 9:10 AM - Customer receives proactive email
                 → Updates payment method
                 → Issue resolved BEFORE they complained!
```

---

## 6️⃣ Recommended Cleanup

### ❌ REMOVE: Interactive Mode

**Why remove:**

- Not needed for production
- Not a strong demo feature
- Adds complexity without value
- Judges won't care about manual testing UI

**Benefits of removal:**

- Cleaner codebase
- Focus on innovation (proactive + event-driven)
- Easier to explain architecture

### ✅ KEEP: These 3 Modes

**1. Proactive Mode** (Core Innovation)

- Your main competitive advantage
- Shows prevention > reaction
- Demonstrates data science + AI

**2. Event-Driven Mode** (Production Ready)

- Shows real-world integration
- Proves you understand production architecture
- Demonstrates auto-description generation

**3. Demo Mode** (Quick Showcase)

- Fast way to show agent quality
- Demonstrates multi-language
- Shows empathy scores
- Good for time-constrained demo

### Final Architecture

```
ProCX Platform
├── Proactive Mode (Innovation) ✅
├── Event-Driven Mode (Integration) ✅
└── Demo Mode (Showcase) ✅
```

---

## 7️⃣ Summary Table

| Mode             | Data Source                      | Description Source                  | Purpose                                  | Demo Order        |
| ---------------- | -------------------------------- | ----------------------------------- | ---------------------------------------- | ----------------- |
| **Proactive**    | All 1,000 customers from DB      | Auto-generated from health analysis | Find at-risk customers BEFORE complaints | **1st** (3-4 min) |
| **Event-Driven** | External webhooks (Stripe, etc.) | Auto-generated from webhook JSON    | Process real-time events, update DB      | **2nd** (3-4 min) |
| **Demo**         | 5 customers from DB (by segment) | Pre-written scenarios               | Show agent intelligence & quality        | **3rd** (2-3 min) |
| ~~Interactive~~  | ~~Manual selection~~             | ~~User input~~                      | ~~Manual testing~~                       | ~~Remove~~        |

---

## 🎬 Recommended Demo Script

**Total Time: 10 minutes**

```bash
# 1. PROACTIVE MODE (4 minutes)
python main.py --mode proactive

"This is our innovation - we scan all customers proactively.
Watch as we detect at-risk customers WITHOUT any complaints.
See this VIP? Health score 58/100 - we caught them early!
Description auto-generated from data patterns."

Press Enter 2-3 times to show different customers
Stop after 3rd intervention

# 2. EVENT-DRIVEN MODE (3 minutes)
python main.py --mode event-driven

"Now production integration - real-time webhook from Stripe.
See the raw JSON? Watch our system convert it to description.
This gets added to database, proactive mode will catch it next scan.
Works with ANY external system - fully automated."

Press Enter for 1-2 webhook examples
Show payment.failed and cart.abandoned

# 3. DEMO MODE (3 minutes)
python main.py --mode demo --demo-count 2

"Finally, agent intelligence. Watch the multi-language detection.
See? Bengali customer, culturally appropriate response.
95% empathy score. This is GPT-4 powered, production-ready."

Show 1-2 scenarios, then stop
```

**Key Messages:**

1. Proactive > Reactive (main innovation)
2. Production-ready integration (event-driven)
3. High-quality AI agents (demo mode)

---

## 🚀 Next Steps

1. **Remove interactive mode** from codebase
2. **Test all 3 modes** work perfectly
3. **Practice demo script** (10 minutes exactly)
4. **Prepare for questions:**
   - "How does event-driven feed proactive?" → Show database flow
   - "Where do descriptions come from?" → Show auto-generation code
   - "Can this work with our systems?" → "Yes! Any webhook-capable system"

**Your innovation is clear: Prevention through proactive monitoring + Smart integration with event-driven architecture!**
