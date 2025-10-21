# ProCX Demo & Architecture Guide

## 1. High-Level Architecture (Why It Wins)

ProCX is a proactive customer experience intelligence layer that continuously scans your customer base, predicts emerging churn or dissatisfaction risks, and intervenes before support tickets appear. It replaces reactive firefighting with preemption.

Core pillars:

- Multi-Agent Decision Fabric (Bodha → Dhyana → Niti → Karuna) for layered cognition
- Real Data Analytics Integration (orders, churn labels, support tickets, NPS, payments) powering grounded insights
- Cultural & Seasonal Intelligence (FestivalContextManager) adding context-aware empathy
- Escalation Continuity (EscalationTracker) preventing duplicate handling and preserving human context
- Memory Persistence (JSONL rolling memory & escalation history) enabling longitudinal learning
- Workflow Orchestration (LangGraph StateGraph) for deterministic, inspectable agent sequencing

Outcome: Faster retention saves, higher LTV preservation, culturally resonant outreach, and reduced support volume.

## 2. Agents (Sanskrit Names & Roles)

1. Bodha (Knowledge / Awareness) – `ContextAgent`
   - Synthesizes customer profile, sentiment proxies, segment positioning, and cohort comparison.
   - Produces a compressed context summary with risk signals.
2. Dhyana (Focused Insight / Meditation) – `PatternAgent`
   - Mines historical patterns (similar customers & issues, cohort stats, health trajectory).
   - Surfaces predictive indicators & resolution effectiveness.
3. Niti (Strategy / Policy / Ethics) – `DecisionAgent`
   - Applies escalation rules (selective for proactive-only), channel mix selection, compliance enforcement.
   - Generates next-best-action with priority & whether human handoff needed.
4. Karuna (Compassion / Empathy) – `EmpathyAgent`
   - Crafts culturally aware, festival-aligned, language-aware outreach copy with tone modulation.
   - Enhances trust and emotional resonance to improve conversion/retention.

Sequential orchestration ensures each layer enriches the state before the next makes higher-order judgments.

## 3. Communication & Failure Handling

Resilience principles:

- Stateless Recovery: Each scan reconstructs state from persisted memory and analytics; no fragile in-memory chains needed.
- Agent Failure Isolation: If one agent throws an exception, workflow skips its augmentation while preserving prior state.
- Escalation Skips: DecisionAgent consults `EscalationTracker.should_skip_customer()` to avoid repeated automation when a human is active.
- Compliance Guardrails: Opt-out customers receive only service/transactional tone; marketing content suppressed.
- Fallback Messaging: If EmpathyAgent fails, a neutral, service-grade template is used to guarantee delivery.
- Idempotent Persistence: Memory writes append-only JSONL; escalation states updated with explicit timestamps to avoid race ambiguity.
- Graceful Degradation: Missing optional sheets (support_tickets, payments, NPS) only reduce richness—not break processing.

## 4. Full Data & Decision Flow

1. ProactiveMonitor selects diverse segment sample, calculates health + churn risk.
2. ProactiveRunner forms a `CustomerEvent` (retention or check-in) for each qualified alert.
3. Workflow executes:
   - Bodha: Builds context_summary (segment position, cohort variance, inferred sentiment, engagement risk).
   - Dhyana: Adds historical_insights (similar customers/issues, resolution success signals, percentile comparisons).
   - Niti: Determines priority + escalation (VIP critical churn, severe CSAT, high LTV critical risk), channel recommendations (email, phone, SMS, in-app, WhatsApp), compliance metadata.
   - Karuna: Generates empathetic, festival/language aware outreach copy referencing product relevance & timing.
4. Final state persisted; escalation (if any) logged with interaction_history potential.
5. Dashboard / CLI displays health distribution, interventions executed, and escalation summaries.

## 5. Agent Sanskrit Names (Meaning & Justification)

- Bodha: Awareness – Captures raw situational truth before action.
- Dhyana: Deep focused insight – Reflective comparative pattern extraction.
- Niti: Strategy & ethical policy – Decides under constraint (compliance, human bandwidth, churn economics).
- Karuna: Compassion – Human-grade tone bridging rational decision to emotional acceptance.

These names reinforce layered cognition: observe → contemplate → decide → connect.

## 6. Customer Situations Handled Proactively

- Emerging churn risk in high LTV VIP segment without recent activity.
- Multi-ticket low CSAT detractor trending toward churn, intervened before departure.
- Seasonal / festival purchase context enabling culturally timed upsell or gratitude message.
- High-value payment friction pattern triggering preemptive reassurance & alternative offer.
- New customer onboarding with weak early engagement signals (prevent silent churn).
- Product category stagnation indicating opportunity for relevant cross-sell.

## 7. Unique Features vs Typical CX Platforms

- Layered Multi-Agent Cognition instead of monolithic scoring.
- Culture & Festival Intelligence integrated natively (multi-language greetings, relevance scoring).
- Escalation Continuity prevents wasteful duplicate interventions and captures interaction history.
- Granular, explainable risk composition (health score components + churn blend with ML predictions if available).
- Compliance-aware channel synthesis (marketing opt-out propagates into decision logic).
- Deterministic yet extensible LangGraph pipeline (easy to insert experimental agents).
- Append-only JSONL memory for transparent audit and quick portability.

## 8. Integration Path (Minimal Steps)

Step 1: Data Ingestion

- Provide Excel/CSV feeds (customers, orders, churn_labels, optional support_tickets, NPS). Mount or S3-sync.

Step 2: Configuration

- Set `DATASET_PATH` & API keys in `config/settings.py`.

Step 3: API Exposure (backend_api.py)

- Expose endpoints: `/scan`, `/interventions`, `/escalations`, `/health-dashboard`.

Step 4: Webhook Hooks (Optional)

- Purchase events → trigger focused re-scan of segment.
- Support ticket creation → log into memory & adjust CSAT baseline.

Step 5: Messaging Connector

- Map channel outputs to ESP (email), Twilio (SMS/WhatsApp), in-app notification bus.

Step 6: Human Escalation Sink

- Integrate escalation JSON into CRM or ticketing (Zendesk/Jira) assigning agent & feeding back resolution notes via webhook.

## 9. Technical Stack

- Python 3.11+ (agents, orchestration, utilities)
- LangChain + LangGraph (LLM interaction & workflow graph)
- OpenAI Chat API (LLM reasoning & copy generation)
- Pandas (data wrangling across multi-sheet dataset)
- JSONL Storage (memory & escalation history persistence)
- dataclasses (Customer, EscalationRecord structure)
- CLI / minimal HTML demo (quick evaluation harness)

## 10. Demo Script (Tone & Flow)

Objective: Show proactive intelligence, empathy, and escalation precision.

Narrative Outline:

1. Opening: "Instead of waiting for a complaint, ProCX predicts who is drifting right now."
2. Run a scan (CLI): Display count of customers evaluated and top at-risk cohort.
3. Drill into a VIP near-churn customer: Show context_summary → historical_insights → decision rationale → final empathetic message (festival-aware if timing matches).
4. Show escalation skip behavior: Re-run scan; already escalated customer is bypassed with clear reason.
5. Highlight compliance: Demonstrate an opt-out customer receiving only service-toned messaging.
6. Cultural intelligence: Trigger a festival purchase example; show multi-language greeting injection.
7. Close: Quantify potential retention lift (hypothetical) and emphasize readiness for integration (only a dataset path + API key).

Tone Guidelines:

- Confident but not hypey
- Emphasize transparency and explainability
- Show human-like empathy layered on rigorous data signals

## 11. Repository Simplification Plan

After adopting this guide, all prior fragmented markdown docs become redundant. We retain:

- `README.md` (general overview)
- `DEMO_AND_ARCHITECTURE_GUIDE.md` (this authoritative deep dive)

All other `.md` files will be removed for clarity.

## Appendix: Escalation Logic (Proactive-Only)

Escalate only when: VIP churn risk > 80%, LTV > 5000 with churn risk > 85%, or extreme dissatisfaction (CSAT < 2.5). Everything else remains automated, preserving human bandwidth.

## Appendix: Failure & Retry Patterns

- Agent exception: Log and continue; state carries previous artifacts.
- Dataset partial availability: Skip dependent analytic enhancements gracefully.
- Message generation failure: Provide fallback neutral template.
- Escalation history sync failure: Retry write; if persistent, queue in memory for next pass.

---
Prepared for hackathon demonstration. Focus: proactive retention + cultural empathy + escalation efficiency.
