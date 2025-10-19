# 🎨 Visual Guide: Multi-Sheet Data Mapping & Step 7

## 🗺️ How We Map Data Across Multiple Sheets

### The Foreign Key: `customer_id`

```
                    CUSTOMER C100109
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  CUSTOMERS    │  │    ORDERS     │  │   TICKETS     │
│   (1,000)     │  │   (5,000)     │  │   (2,000)     │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ customer_id   │  │ customer_id   │  │ customer_id   │
│ C100109       │  │ C100109       │  │ C100109       │
│ Rajesh Kumar  │  │ ORD001        │  │ TICKET-789    │
│ VIP           │  │ $2,500        │  │ Open          │
│ $45,230 LTV   │  │ 2024-12-01    │  │ High Priority │
└───────────────┘  ├───────────────┤  ├───────────────┤
                   │ C100109       │  │ C100109       │
                   │ ORD003        │  │ TICKET-823    │
                   │ $3,400        │  │ Resolved      │
                   │ 2024-12-15    │  │ Medium        │
                   ├───────────────┤  └───────────────┘
                   │ C100109       │
                   │ ORD005        │
                   │ $1,100        │
                   │ 2025-01-05    │
                   └───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ↓                  ↓                  ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   PAYMENTS    │  │  NPS_SURVEY   │  │ CHURN_LABELS  │
│   (4,750)     │  │     (800)     │  │   (1,000)     │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ customer_id   │  │ customer_id   │  │ customer_id   │
│ C100109       │  │ C100109       │  │ C100109       │
│ SUCCESS       │  │ Score: 4      │  │ is_churn: 0   │
│ $2,500        │  │ Date: 2025    │  │ risk: 0.68    │
├───────────────┤  │ Feedback: Bad │  └───────────────┘
│ C100109       │  └───────────────┘
│ FAILED        │
│ $3,400        │
└───────────────┘
```

---

## 🔄 Complete Data Flow: Raw Data → Final Message

```
STEP 1: LOAD DATA
═════════════════════════════════════════════════════════════════
Excel Files                          Pandas DataFrames
─────────────                        ─────────────────
AgentMAX_CX_dataset.xlsx
├── customers (1,000)      ────────→  self.df
├── orders (5,000)         ────────→  self.orders_df
├── support_tickets (2,000)────────→  self.support_tickets_df
├── nps_survey (800)       ────────→  self.nps_survey_df
├── payments (4,750)       ────────→  self.payments_df
└── churn_labels (1,000)   ────────→  self.churn_labels_df

[Loaded ONCE using singleton pattern]


STEP 2: FETCH CUSTOMER-SPECIFIC DATA
═════════════════════════════════════════════════════════════════
For Customer C100109:

┌─────────────────────────────────────────────────────────────┐
│  customer = self.df[customer_id == 'C100109']              │
│  ↓                                                          │
│  Customer Object:                                           │
│    - customer_id: C100109                                   │
│    - name: Rajesh Kumar                                     │
│    - segment: VIP                                           │
│    - lifetime_value: $45,230                                │
│    - loyalty_tier: Platinum                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ↓                 ↓                 ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ FETCH ORDERS    │ │ FETCH TICKETS   │ │ FETCH PAYMENTS  │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ Filter:         │ │ Filter:         │ │ Filter:         │
│ orders_df[      │ │ tickets_df[     │ │ payments_df[    │
│  customer_id==  │ │  customer_id==  │ │  customer_id==  │
│  'C100109']     │ │  'C100109']     │ │  'C100109']     │
│                 │ │                 │ │                 │
│ Result:         │ │ Result:         │ │ Result:         │
│ 3 orders        │ │ 2 tickets       │ │ 5 payments      │
│ Total: $7,000   │ │ 1 open          │ │ 1 failed        │
│ Last: 45d ago   │ │ Avg time: 48h   │ │ Success: 80%    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ↓
                    ┌─────────────┐
                    │ FETCH NPS   │
                    ├─────────────┤
                    │ nps_df[     │
                    │  customer_  │
                    │  id=='...'] │
                    │             │
                    │ Result:     │
                    │ Score: 4/10 │
                    │ Detractor   │
                    └─────────────┘


STEP 3: CALCULATE HEALTH SCORE
═════════════════════════════════════════════════════════════════
Input: Customer object + fetched data

┌─────────────────────────────────────────────────────────────┐
│  health_score = 0.0                                         │
│                                                             │
│  Factor 1: Segment = VIP           → +15 points            │
│  Factor 2: LTV Percentile = 75%    → +9 points             │
│  Factor 3: Loyalty = Platinum      → +10 points            │
│  Factor 4: Relative Value = 1.2x   → +8 points             │
│  Factor 5: Days Inactive = 45      → +4 points (low!)      │
│  Factor 6: Order Frequency = 0.8/m → +6 points             │
│  Factor 7: Spending Trend = -10%   → +5 points (decline!)  │
│  Factor 8: Support Tickets = 2     → +3 points (issues!)   │
│  Factor 9: NPS Score = 4           → +0 points (bad!)      │
│  Factor 10: Tenure = 2 years       → +3 points             │
│                                                             │
│  Total: 58 / 100                                            │
└─────────────────────────────────────────────────────────────┘


STEP 4: CALCULATE CHURN RISK
═════════════════════════════════════════════════════════════════
Input: Health score + churn_labels data

┌─────────────────────────────────────────────────────────────┐
│  Base risk from health:                                     │
│    health_score = 58 → base_risk = 42%                      │
│                                                             │
│  Adjustment from churn_labels (ML model):                   │
│    predicted_churn_score = 0.68                             │
│                                                             │
│  Find similar customers who churned:                        │
│    - 3 VIP customers with health 55-60 → 2 churned         │
│    - Churn rate in this group: 67%                          │
│                                                             │
│  Final churn_risk = (base_risk + predicted + similar) / 3   │
│                   = (42% + 68% + 67%) / 3                   │
│                   = 59% → Adjusted to 68% (model weight)    │
└─────────────────────────────────────────────────────────────┘


STEP 5: FILTER AT-RISK
═════════════════════════════════════════════════════════════════
Conditions:
  churn_risk > 60% ✓ (68%)
  lifetime_value > $2,000 ✓ ($45,230)
  segment in [VIP, Loyal] ✓ (VIP)

→ Customer C100109 is AT RISK!


STEP 6: SORT BY PRIORITY
═════════════════════════════════════════════════════════════════
Priority Score = churn_risk × lifetime_value

C100109: 0.68 × $45,230 = $30,756  ← Highest priority!
C100141: 0.71 × $12,450 = $8,840
C100302: 0.65 × $8,900  = $5,785

→ C100109 gets processed first


STEP 7: GENERATE DESCRIPTION (THIS IS THE KEY STEP!)
═════════════════════════════════════════════════════════════════
Input: Customer object + Alert dict

┌─────────────────────────────────────────────────────────────┐
│  alert = {                                                  │
│    'customer': <Customer C100109>,                          │
│    'health_score': 0.58,                                    │
│    'churn_risk': 0.68,                                      │
│    'reasons': [                                             │
│      'Low health score',                                    │
│      'High-value segment at risk',                          │
│      'Below-average in cohort'                              │
│    ],                                                       │
│    'recommended_action': 'immediate_personal_outreach'      │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
              ┌───────────────────────┐
              │ GENERATION LOGIC      │
              ├───────────────────────┤
              │ 1. Extract scores     │
              │ 2. Categorize health  │
              │ 3. Format description │
              │ 4. Create event       │
              └───────────┬───────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  GENERATED DESCRIPTION:                                     │
│                                                             │
│  VIP customer at high risk (LTV: $45,230.50)                │
│  • Health Score: 58/100 (Warning)                           │
│  • Churn Risk: 68%                                          │
│  • Risk Factors: Low health score, High-value segment at   │
│    risk, Below-average in cohort                            │
│  • Recommended Action: Immediate Personal Outreach          │
└─────────────────────────────────────────────────────────────┘

This description is:
  ✓ Technical (for AI agents)
  ✓ Data-driven (all numbers from analysis)
  ✓ Actionable (includes recommendation)


STEP 8: AGENT PIPELINE
═════════════════════════════════════════════════════════════════
Input: CustomerEvent with description

┌─────────────────────────────────────────────────────────────┐
│  CustomerEvent:                                             │
│    event_id: PROACTIVE_C100109_1234567890                   │
│    customer: <Customer C100109>                             │
│    description: "VIP customer at high risk..."              │
│    metadata: {health_score, churn_risk, reasons}            │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │ Context  │  →   │ Pattern  │  →   │ Decision │
  │  Agent   │      │  Agent   │      │  Agent   │
  ├──────────┤      ├──────────┤      ├──────────┤
  │ Analyzes │      │ Finds    │      │ Chooses  │
  │ customer │      │ similar  │      │ channel  │
  │ history  │      │ cases    │      │ & timing │
  └──────────┘      └──────────┘      └──────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ↓
                    ┌──────────┐
                    │ Empathy  │
                    │  Agent   │
                    ├──────────┤
                    │ Generates│
                    │ response │
                    │ (GPT-4)  │
                    └──────────┘


STEP 9: FINAL MESSAGE (DIFFERENT FROM STEP 7!)
═════════════════════════════════════════════════════════════════
Input: Agent decisions + customer context

┌─────────────────────────────────────────────────────────────┐
│  EMPATHY AGENT OUTPUT:                                      │
│                                                             │
│  Subject: We Miss You, Rajesh!                              │
│                                                             │
│  Dear Rajesh,                                               │
│                                                             │
│  As one of our most valued VIP members, we noticed you      │
│  haven't placed an order in the past 45 days. We hope       │
│  everything is going well!                                  │
│                                                             │
│  We genuinely appreciate your loyalty over the past 2       │
│  years and would love to continue serving you. To show      │
│  our appreciation, we'd like to offer you:                  │
│                                                             │
│  • 25% OFF your next order                                  │
│  • Free express shipping                                    │
│  • Priority customer support                                │
│  • Personal account manager                                 │
│                                                             │
│  Your feedback matters to us. If there's anything we        │
│  can improve, please let us know. We're here to help!       │
│                                                             │
│  Best regards,                                              │
│  The Customer Experience Team                               │
│                                                             │
│  [Empathy Score: 9.5/10]                                    │
│  [Channel: Email + SMS]                                     │
│  [Timing: Send within 24 hours]                             │
│  [Escalation: Assign account manager]                       │
└─────────────────────────────────────────────────────────────┘

This message is:
  ✓ Empathetic (warm, understanding tone)
  ✓ Personalized (uses name, history, offers)
  ✓ Actionable (clear offers and CTA)
```

---

## 📊 Key Differences: Step 7 vs Step 9

```
┌──────────────────────────────────────────────────────────────┐
│                    STEP 7 DESCRIPTION                        │
│              (Problem Summary for AI Agents)                 │
├──────────────────────────────────────────────────────────────┤
│  VIP customer at high risk (LTV: $45,230.50)                 │
│  • Health Score: 58/100 (Warning)                            │
│  • Churn Risk: 68%                                           │
│  • Risk Factors: Low health score, High-value segment at     │
│    risk, Below-average in cohort                             │
│  • Recommended Action: Immediate Personal Outreach           │
├──────────────────────────────────────────────────────────────┤
│  Audience: AI Agents                                         │
│  Tone: Technical/Analytical                                  │
│  Generated by: ProCX System Logic                            │
│  Purpose: Context for decision-making                        │
│  Length: 5 lines                                             │
│  Content: Scores, risks, facts                               │
└──────────────────────────────────────────────────────────────┘
                            ↓
                     [Agent Pipeline]
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    STEP 9 FINAL MESSAGE                      │
│               (Customer Outreach Response)                   │
├──────────────────────────────────────────────────────────────┤
│  Dear Rajesh,                                                │
│                                                              │
│  As one of our most valued VIP members, we noticed you       │
│  haven't placed an order in the past 45 days...              │
│                                                              │
│  We'd like to offer you:                                     │
│  • 25% OFF your next order                                   │
│  • Free express shipping                                     │
│  • Personal account manager                                  │
│                                                              │
│  Your feedback matters to us...                              │
├──────────────────────────────────────────────────────────────┤
│  Audience: Customer (Rajesh)                                 │
│  Tone: Empathetic/Warm                                       │
│  Generated by: GPT-4 Empathy Agent                           │
│  Purpose: Retention & engagement                             │
│  Length: 15+ lines                                           │
│  Content: Offers, support, solutions                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Reference: Where Things Happen

| What                              | Where                      | Input               | Output             |
| --------------------------------- | -------------------------- | ------------------- | ------------------ |
| **Load data**                     | `data_analytics.py:49`     | Excel file          | DataFrames         |
| **Filter by customer**            | `data_analytics.py:714`    | `customer_id`       | Filtered rows      |
| **Calculate health**              | `proactive_monitor.py:16`  | Customer + data     | Score 0-1          |
| **Calculate churn**               | `proactive_monitor.py:144` | Health + labels     | Risk 0-1           |
| **Detect at-risk**                | `proactive_monitor.py:220` | All customers       | Alert list         |
| **Sort priority**                 | `proactive_monitor.py:334` | Alert list          | Sorted alerts      |
| **Generate description (Step 7)** | `main.py:204`              | Customer + alert    | Description string |
| **Agent pipeline**                | `workflows/cx_workflow.py` | CustomerEvent       | Agent decisions    |
| **Generate message (Step 9)**     | `agents/empathy_agent.py`  | Context + decisions | Final message      |

---

## 💡 The Big Picture

```
Excel Data → Load → Filter → Analyze → [STEP 7: Describe] → Agents → [STEP 9: Respond]
  (Raw)    (Pandas) (by ID)  (scores)   (Technical)     (GPT-4)    (Empathetic)
```

**Step 7 = Problem definition (what's wrong)**
**Step 9 = Solution delivery (how to fix it)**

They're completely different outputs serving different purposes!
