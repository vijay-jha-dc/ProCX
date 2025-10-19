# 🕒 ProactiveScheduler - Complete Guide

## What is the Scheduler?

The **ProactiveScheduler** is what makes ProCX truly proactive:
- Runs continuously in the background
- Scans customers every 5 minutes (configurable)
- Detects churn risks automatically
- Triggers agent interventions without human input

**This is THE differentiator:** Most CX systems are reactive. ProCX is predictive.

---

## How to Run the Scheduler

### Option 1: One-Time Scan (Demo for Judges)
```bash
python proactive_scheduler.py --mode once
```

**When to use:** 
- During hackathon demo presentation
- To show judges how proactive detection works
- Quick testing

**What happens:**
- Runs ONE scan immediately
- Shows at-risk customers
- Generates interventions
- Exits after completion

---

### Option 2: Continuous Mode (Production Simulation)
```bash
python proactive_scheduler.py --mode continuous --interval 5
```

**When to use:**
- To prove system runs autonomously
- Simulating production behavior
- Background monitoring

**What happens:**
- Scans every 5 minutes (configurable)
- Runs indefinitely until you stop it (Ctrl+C)
- Logs all scans and interventions
- Shows cumulative statistics

**Arguments:**
- `--interval 5` - Scan every 5 minutes (change to 1, 10, 15, etc.)
- `--risk-threshold 0.6` - Only intervene if churn risk >= 60%
- `--max-interventions 10` - Limit interventions per scan

---

## When to Start the Scheduler?

### 🎯 For Hackathon Demo (Recommended Approach):

**BEFORE Judges Arrive:**
1. Start scheduler 30 minutes before your presentation:
   ```bash
   python proactive_scheduler.py --mode continuous --interval 5
   ```
2. Let it run in background and accumulate scans
3. This shows "real-time monitoring" has been running

**DURING Presentation:**
1. Show the terminal with scheduler running
2. Point out: "This has been running for 30 minutes, no human intervention"
3. Show cumulative stats: "20 scans completed, 15 interventions triggered"
4. Then run one-time scan for live demo:
   ```bash
   python proactive_scheduler.py --mode once
   ```

### 📊 Output Example:

```
🔄 ProactiveScheduler initialized
   Scan interval: Every 5 minutes
   Churn risk threshold: 60%
   Max interventions per run: 10

======================================================================
🔍 PROACTIVE SCAN #1
======================================================================
Timestamp: 2025-10-19 14:30:00
Scanning customers for churn risk >= 60%...
⚠️  Found 12 at-risk customers
   Processing top 10 priority cases

🤖 Processing Customer 1/10: C100088 (VIP, Platinum)
   Health Score: 32.5% | Churn Risk: 85.2%
   Issue: Haven't purchased in 60+ days (declining activity)
   
   [Agent workflow running...]
   ✅ Intervention generated (Hindi)
   
Scan #1 Complete - 10 interventions | 6.3s elapsed

======================================================================
📊 SCHEDULER STATISTICS
======================================================================
Total Scans: 1
Total Interventions: 10
Average Interventions/Scan: 10.0
Next scan in: 5 minutes (14:35:00)
```

---

## Scheduler Architecture

```
┌─────────────────────────────────────────────────┐
│         ProactiveScheduler                      │
│  (Runs every 5 minutes automatically)           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         ProactiveMonitor                        │
│  Scans Excel → Calculates Health Scores        │
│  10-factor algorithm → Churn risk prediction    │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         At-Risk Customers Detected              │
│  [C100088, C100138, C100485, ...]              │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         Multi-Agent Pipeline                    │
│  Context → Pattern → Decision → Empathy         │
│  (Each customer processed through 4 agents)     │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         Intervention Generated                  │
│  Personalized message + Action plan             │
│  Saved to: data/memory/{customer_id}.jsonl     │
└─────────────────────────────────────────────────┘
```

---

## Judge Talking Points

### "How is this proactive?"

**Point to running scheduler:**
> "See this terminal? This scheduler has been running for 30 minutes. Zero human intervention. It scanned our customer database 6 times, detected 35 at-risk customers, and generated personalized retention interventions."

### "How often does it scan?"

> "Every 5 minutes by default, but fully configurable. In production, you'd set it based on your business needs - hourly for some industries, daily for others. The key is it's AUTOMATED - no one needs to remember to check."

### "What triggers an intervention?"

> "Our 10-factor health scoring algorithm. We analyze:
> - Order frequency and recency
> - Spending trends
> - Support ticket patterns
> - NPS scores
> - Engagement metrics
> - Loyalty tier and segment behavior
> 
> When health score drops below 40% or churn risk exceeds 60%, we intervene."

### "Why not just send batch emails?"

> "Because our system uses 4 AI agents to personalize EACH intervention:
> - Analyzes customer's specific situation
> - Predicts what's causing churn
> - Crafts personalized strategy
> - Generates message in their preferred language
> 
> It's not spam - it's intelligent, targeted retention."

---

## Testing Commands

### Quick Test (30 seconds):
```bash
python proactive_scheduler.py --mode once --risk-threshold 0.6
```

### Background Test (5 minutes):
```bash
# Terminal 1: Start scheduler
python proactive_scheduler.py --mode continuous --interval 1

# Wait 5 minutes, then check logs
# Press Ctrl+C to stop
```

### High-Risk Only:
```bash
python proactive_scheduler.py --mode once --risk-threshold 0.8
```
(Only customers with 80%+ churn risk)

---

## Production Deployment (Future)

In production, you'd deploy this as:

### Option A: Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: procx-scheduler
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scheduler
            image: procx:latest
            command: ["python", "proactive_scheduler.py", "--mode", "once"]
```

### Option B: AWS EventBridge
```python
# Lambda function triggered every 5 minutes
def lambda_handler(event, context):
    scheduler = ProactiveScheduler()
    scheduler.scan_and_intervene()
```

### Option C: SystemD Service (Linux)
```bash
sudo systemctl enable procx-scheduler
sudo systemctl start procx-scheduler
# Runs continuously as background service
```

---

## Troubleshooting

### Scheduler not finding customers?
```bash
# Check if Excel data loads properly
python -c "from utils import ProactiveMonitor; m = ProactiveMonitor(); print(len(m.customers_df))"
```

### Too many interventions?
```bash
# Increase risk threshold
python proactive_scheduler.py --mode once --risk-threshold 0.75
```

### Scheduler running too fast?
```bash
# Increase interval
python proactive_scheduler.py --mode continuous --interval 15
```

---

## Key Files

- `proactive_scheduler.py` - Main scheduler logic
- `utils/proactive_monitor.py` - Health scoring and risk detection
- `workflows/cx_workflow.py` - Multi-agent pipeline
- `data/memory/*.jsonl` - Intervention logs

---

## Summary: When & Why

| Scenario | Command | Why |
|----------|---------|-----|
| **Demo to judges** | `--mode once` | Show live proactive detection |
| **Prove automation** | `--mode continuous` (30 min before) | Show it runs without humans |
| **Testing** | `--mode once --risk-threshold 0.8` | Quick validation |
| **Production** | Deploy as CronJob/Lambda | Real continuous monitoring |

The scheduler is your proof that ProCX doesn't just react - it PREDICTS and PREVENTS customer churn automatically.
