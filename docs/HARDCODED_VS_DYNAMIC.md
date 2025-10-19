# 📊 What's Hardcoded vs Dynamic - Visual Breakdown

## The Example Description

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

---

## 🔴 Currently: MOSTLY HARDCODED

### What You Actually Have Now (main.py line 216):

```python
description = f"Proactive retention: Churn risk {alert['churn_risk']:.1%}"
```

**Example Output:**

```
Proactive retention: Churn risk 68.5%
```

### Breakdown:

- 🔴 **Hardcoded:** "Proactive retention: Churn risk" (static text)
- 🟢 **Dynamic:** `68.5%` (calculated from health score)

**That's it!** Only 1 dynamic value.

---

## 🟢 What You COULD Have (Rich Implementation)

### Using Available Database Methods:

```python
description = f"""
{customer.segment} customer (LTV: ${customer.lifetime_value:,.2f}) showing distress signals:
- Health Score: {health_score:.0f}/100 ({health_status})
- {payment_stats['failed_payments_30d']} failed payments in last 30 days
- NPS score dropped from {nps_data[1]['score']} to {nps_data[0]['score']}
- Last purchase {customer.days_since_active} days ago (unusual for {customer.segment} segment)
- {ticket_stats['open_tickets']} unresolved support tickets
- Order frequency declined {order_stats['frequency_decline_pct']:.0f}% vs 3-month average
"""
```

### Breakdown:

| Text                               | Type         | Source                                             |
| ---------------------------------- | ------------ | -------------------------------------------------- |
| "customer (LTV: $"                 | 🔴 Hardcoded | Static template                                    |
| `VIP`                              | 🟢 Dynamic   | `customer.segment` from DB                         |
| `45,230.50`                        | 🟢 Dynamic   | `customer.lifetime_value` from DB                  |
| ") showing distress signals:"      | 🔴 Hardcoded | Static template                                    |
| "- Health Score: "                 | 🔴 Hardcoded | Static label                                       |
| `58`                               | 🟢 Dynamic   | Calculated from 10 factors                         |
| "/100 ("                           | 🔴 Hardcoded | Static template                                    |
| `Critical`                         | 🟢 Dynamic   | Conditional: "Critical" if < 40, "Warning" if < 60 |
| ")"                                | 🔴 Hardcoded | Static template                                    |
| "- "                               | 🔴 Hardcoded | Static template                                    |
| `3`                                | 🟢 Dynamic   | `get_customer_payment_reliability()`               |
| " failed payments in last 30 days" | 🔴 Hardcoded | Static label                                       |
| "- NPS score dropped from "        | 🔴 Hardcoded | Static label                                       |
| `9`                                | 🟢 Dynamic   | `get_customer_nps()` - previous score              |
| " to "                             | 🔴 Hardcoded | Static template                                    |
| `4`                                | 🟢 Dynamic   | `get_customer_nps()` - current score               |
| "- Last purchase "                 | 🔴 Hardcoded | Static label                                       |
| `45`                               | 🟢 Dynamic   | `customer.days_since_active` calculated            |
| " days ago (unusual for "          | 🔴 Hardcoded | Static template                                    |
| `VIP`                              | 🟢 Dynamic   | `customer.segment`                                 |
| " segment)"                        | 🔴 Hardcoded | Static template                                    |
| "- "                               | 🔴 Hardcoded | Static template                                    |
| `2`                                | 🟢 Dynamic   | `get_customer_support_history()`                   |
| " unresolved support tickets"      | 🔴 Hardcoded | Static label                                       |
| "- Order frequency declined "      | 🔴 Hardcoded | Static label                                       |
| `60`                               | 🟢 Dynamic   | `get_customer_order_stats()`                       |
| "% vs 3-month average"             | 🔴 Hardcoded | Static label                                       |

**Summary:**

- 🔴 **Hardcoded:** ~40% (labels, punctuation, templates)
- 🟢 **Dynamic:** ~60% (all actual data from database)

**This is GOOD!** The hardcoded parts are just formatting. All real data is dynamic.

---

## 🎯 The Key Insight

### Hardcoded vs Dynamic - What Matters?

**✅ ACCEPTABLE Hardcoding:**

- Labels: "Health Score:", "failed payments", "NPS score"
- Templates: "showing distress signals:", "unusual for"
- Punctuation: "- ", " / ", " (%)"

**❌ BAD Hardcoding:**

- Numbers: "3 failed payments" (should query DB)
- Status: "Critical" (should calculate)
- Customer data: "VIP" (should come from customer.segment)

---

## 📋 Database Methods Already Available

You have these methods ready to use:

| Method                               | Returns          | Example                                              |
| ------------------------------------ | ---------------- | ---------------------------------------------------- |
| `customer.segment`                   | Customer segment | "VIP", "Loyal"                                       |
| `customer.lifetime_value`            | Total LTV        | 45230.50                                             |
| `customer.days_since_active`         | Days inactive    | 45                                                   |
| `get_customer_payment_reliability()` | Payment stats    | `{'failed_payments_30d': 3, 'success_rate': 0.85}`   |
| `get_customer_nps()`                 | NPS score        | `{'score': 4, 'date': '2025-01-10'}`                 |
| `get_customer_support_history()`     | Ticket stats     | `{'open_tickets': 2, 'total_tickets': 5}`            |
| `get_customer_order_stats()`         | Order analysis   | `{'frequency_decline_pct': -60, 'total_orders': 12}` |
| `compare_with_cohort()`              | Percentile rank  | `{'customer_percentile': 25}`                        |

---

## 💡 Simple Example - What You Can Do RIGHT NOW

### Current Code (line 216):

```python
description = f"Proactive retention: Churn risk {alert['churn_risk']:.1%}"
```

### Improved Version (5-minute fix):

```python
health_score = alert['health_score'] * 100
churn_risk = alert['churn_risk'] * 100

description = f"""{customer.segment} customer at high risk (LTV: ${customer.lifetime_value:,.2f})
• Health Score: {health_score:.0f}/100
• Churn Risk: {churn_risk:.0f}%
• Risk Factors: {', '.join(alert['reasons'][:3])}
• Recommended Action: {alert['recommended_action'].replace('_', ' ').title()}"""
```

### Output Comparison:

**Before:**

```
Proactive retention: Churn risk 68.5%
```

**After:**

```
VIP customer at high risk (LTV: $45,230.50)
• Health Score: 58/100
• Churn Risk: 68%
• Risk Factors: Low health score, High-value segment at risk, Below-average in cohort
• Recommended Action: Immediate Personal Outreach
```

**Impact:**

- From 1 dynamic value → 7 dynamic values
- From generic text → Specific customer context
- From technical → Business-friendly

---

## 🚀 Recommendation for Hackathon

### Priority 1: Quick Win (5 minutes)

Update `_create_proactive_event` with the improved version above.

**Why:** Big visual impact, uses data you already have, no new queries needed.

### Priority 2: Rich Description (30 minutes if you have time)

Implement full `_generate_rich_description()` method with database queries.

**Why:** Most impressive demo, proves you're using real data, judges will love it.

### Priority 3: Documentation

Update `MODES_DEEP_DIVE.md` to reflect what's actually implemented.

**Why:** Honesty matters. Don't promise what you don't have.

---

## ✅ Final Answer to Your Question

### "What part of this is hardcoded?"

**In the aspirational example:**

- 🔴 **Hardcoded:** Labels, templates, formatting (~40%)
- 🟢 **Dynamic:** All numbers and customer data (~60%)

**In your current code:**

- 🔴 **Hardcoded:** "Proactive retention: Churn risk " (~85%)
- 🟢 **Dynamic:** Just the percentage (~15%)

**Recommendation:**
Implement the "Improved Version" above to get to:

- 🔴 **Hardcoded:** Labels and formatting (~50%)
- 🟢 **Dynamic:** Customer segment, LTV, scores, reasons, actions (~50%)

**This is plenty good enough for a hackathon demo!** The key is that all business data comes from the database, only labels are hardcoded.
