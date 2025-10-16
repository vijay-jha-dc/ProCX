# Dataset Optimization Analysis

## Summary
**Optimized:** 16 columns → 15 columns  
**Removed:** 1 column (`city`)  
**Reason:** Unnecessary granularity without business value

---

## Column-by-Column Analysis

### ✅ **KEEP - Critical Fields (10)**

| Column | Utility | Use Case |
|--------|---------|----------|
| `customer_id` | ⭐⭐⭐⭐⭐ CRITICAL | Unique identifier for tracking |
| `first_name` | ⭐⭐⭐⭐⭐ CRITICAL | Personalization in responses |
| `last_name` | ⭐⭐⭐⭐⭐ CRITICAL | Professional communication |
| `email` | ⭐⭐⭐⭐⭐ CRITICAL | Primary contact channel |
| `segment` | ⭐⭐⭐⭐⭐ CRITICAL | VIP/Loyal/Regular/Occasional classification |
| `lifetime_value` | ⭐⭐⭐⭐⭐ CRITICAL | Value-based prioritization, churn risk |
| `avg_order_value` | ⭐⭐⭐⭐⭐ CRITICAL | Spending patterns, upsell targeting |
| `last_active_date` | ⭐⭐⭐⭐⭐ CRITICAL | Inactivity detection, engagement scoring |
| `signup_date` | ⭐⭐⭐⭐⭐ CRITICAL | Customer tenure, lifecycle stage |
| `opt_in_marketing` | ⭐⭐⭐⭐⭐ CRITICAL | GDPR compliance, permission-based marketing |

### ✅ **KEEP - High Value Fields (2)**

| Column | Utility | Use Case |
|--------|---------|----------|
| `loyalty_tier` | ⭐⭐⭐⭐ HIGH | Platinum/Gold/Silver/Bronze rewards program |
| `preferred_category` | ⭐⭐⭐⭐ HIGH | Product recommendations, personalization |

### ✅ **KEEP - Medium Value Fields (3)**

| Column | Utility | Use Case |
|--------|---------|----------|
| `phone` | ⭐⭐⭐ MEDIUM | Multi-channel outreach (SMS, WhatsApp, calls) |
| `country` | ⭐⭐⭐ MEDIUM | Geographic insights, timezone-aware engagement (6 countries) |
| `language` | ⭐⭐⭐ MEDIUM | Localized messaging, multilingual support (5 languages: en, hi, ta, te, bn) |

---

### ❌ **REMOVE - Low Value Field (1)**

| Column | Why Remove |
|--------|------------|
| `city` | **Too granular:** 10 Indian cities (Jaipur, Delhi, Mumbai, etc.)<br>**No business value:** Hyper-local offers not in project scope<br>**Redundant:** Country-level data sufficient for regional patterns<br>**Adds noise:** Clutters agent context without clear use case<br>**Distribution:** Evenly spread (88-114 customers per city) - no clustering insights |

---

## Business Justification

### Why City is Unnecessary:

1. **Scope Mismatch**
   - ProCX is a customer experience platform, not a logistics/delivery system
   - No hyper-local offers or city-specific campaigns in scope

2. **Insufficient Granularity**
   - Only 10 cities covered (all in India)
   - Not enough diversity for meaningful pattern recognition
   - Even distribution across cities (no geographical clustering)

3. **Redundancy**
   - `country` field provides sufficient geographic context
   - Timezone and regional preferences can be derived from country

4. **Context Pollution**
   - Adds extra data to agent prompts without improving decision quality
   - Increases token usage for LLM calls

### What We Keep Instead:

- **Country** (6 countries: Singapore, UAE, USA, UK, Australia, India)
  - Sufficient for timezone-aware engagement
  - Regional business patterns (e.g., different shopping behaviors by country)
  - Cultural considerations in messaging

---

## Impact on Agents

### Before (16 columns):
```
Customer: John Doe, Mumbai, India
```
- City adds little context value

### After (15 columns):
```
Customer: John Doe, India
```
- Cleaner, focuses on actionable data
- Country is sufficient for regional insights

---

## Optimized Dataset

**File:** `data/AgentMAX_CX_dataset_optimized.xlsx`  
**Rows:** 1,000 customers  
**Columns:** 15 (removed `city`)

### Fields Retained:
1. customer_id
2. first_name
3. last_name
4. email
5. phone
6. signup_date
7. country
8. segment
9. lifetime_value
10. avg_order_value
11. preferred_category
12. last_active_date
13. loyalty_tier
14. opt_in_marketing
15. language

---

## Recommendation

✅ **Switch to optimized dataset** for better agent performance:
- Reduced noise in agent context
- All business-critical fields preserved
- Maintains compliance (opt_in_marketing)
- Keeps engagement metrics (last_active_date, signup_date)
- Enables personalization (language, name, country)
- Supports churn prediction (tenure, spending, activity)

**Next Step:** Update `settings.py` to use `AgentMAX_CX_dataset_optimized.xlsx`
