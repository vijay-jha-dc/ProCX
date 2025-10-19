"""
🔮 ProCX Dashboard - Real-Time Proactive Customer Experience Monitoring

This Streamlit app provides a stunning visual interface for:
- Live customer health monitoring
- Real-time intervention tracking
- Agent activity visualization
- Interactive analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ProactiveMonitor
from config import settings

# Page config
st.set_page_config(
    page_title="ProCX - Proactive CX Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 0.5rem 0;
    }
    .alert-high { border-color: #ef4444; background: #fef2f2; }
    .alert-medium { border-color: #f59e0b; background: #fffbeb; }
    .alert-low { border-color: #10b981; background: #f0fdf4; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'monitor' not in st.session_state:
    st.session_state.monitor = ProactiveMonitor()
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = None
if 'interventions' not in st.session_state:
    st.session_state.interventions = []

def load_data():
    """Load customer data and calculate health scores."""
    monitor = st.session_state.monitor
    
    # Get all customers
    customers_df = monitor.customers_df.copy()
    
    # Calculate health scores for sample
    health_data = []
    for idx, row in customers_df.head(100).iterrows():  # Sample 100 for performance
        health = monitor._calculate_customer_health(row)
        health_data.append({
            'customer_id': row['customer_id'],
            'name': f"{row['first_name']} {row['last_name']}",
            'segment': row['segment'],
            'loyalty_tier': row['loyalty_tier'],
            'health_score': health['health_score'] * 100,
            'churn_risk': health['churn_risk'] * 100,
            'lifetime_value': row['lifetime_value'],
            'risk_level': health['risk_level']
        })
    
    return pd.DataFrame(health_data)

def get_at_risk_customers():
    """Get customers currently at risk."""
    monitor = st.session_state.monitor
    alerts = monitor.detect_churn_risks(min_churn_risk=0.6, min_lifetime_value=1000)
    return alerts[:30]  # Top 30

# Header
st.markdown('<div class="main-header">🔮 ProCX Dashboard</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #6b7280; margin-top: -1rem;">Proactive Customer Experience Intelligence</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/667eea/ffffff?text=ProCX", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### ⚙️ Control Panel")
    
    # Scan controls
    if st.button("🔍 Run Proactive Scan", use_container_width=True):
        with st.spinner("Scanning customers..."):
            alerts = get_at_risk_customers()
            st.session_state.last_scan = datetime.now()
            st.session_state.interventions = alerts
            st.success(f"✅ Scan complete! Found {len(alerts)} at-risk customers")
    
    # Settings
    st.markdown("### 📊 Settings")
    risk_threshold = st.slider("Risk Threshold", 0, 100, 60, 5, help="Minimum churn risk % to trigger alert")
    ltv_threshold = st.number_input("Min LTV ($)", min_value=0, value=1000, step=100)
    
    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    st.markdown("---")
    st.markdown("### 📈 System Status")
    st.metric("Total Customers", "1,000")
    st.metric("Data Sources", "10 Sheets")
    st.metric("Active Agents", "4 AI Agents")
    
    # Last scan time
    if st.session_state.last_scan:
        elapsed = datetime.now() - st.session_state.last_scan
        st.info(f"Last scan: {elapsed.seconds}s ago")

# Main dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⚠️ At-Risk Customers", "🤖 Agent Activity", "📈 Analytics"])

with tab1:
    st.markdown("## 📊 Real-Time Overview")
    
    # Load data
    health_df = load_data()
    at_risk = get_at_risk_customers()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,000</div>
            <div class="metric-label">📋 Total Customers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        at_risk_count = len(at_risk)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);">
            <div class="metric-value">{at_risk_count}</div>
            <div class="metric-label">⚠️ At Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        healthy_pct = int(((100 - at_risk_count) / 100) * 100)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <div class="metric-value">{healthy_pct}%</div>
            <div class="metric-label">✅ Healthy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        interventions = len(st.session_state.interventions)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
            <div class="metric-value">{interventions}</div>
            <div class="metric-label">🎯 Interventions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Customer Health Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎨 Health Score Distribution")
        fig_health = px.histogram(
            health_df, 
            x='health_score',
            nbins=20,
            color_discrete_sequence=['#667eea'],
            labels={'health_score': 'Health Score (%)', 'count': 'Number of Customers'}
        )
        fig_health.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Churn Risk Distribution")
        fig_risk = px.histogram(
            health_df, 
            x='churn_risk',
            nbins=20,
            color_discrete_sequence=['#ef4444'],
            labels={'churn_risk': 'Churn Risk (%)', 'count': 'Number of Customers'}
        )
        fig_risk.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # Scatter plot: Health vs Risk
    st.markdown("### 📍 Customer Health Heatmap")
    fig_scatter = px.scatter(
        health_df,
        x='health_score',
        y='churn_risk',
        size='lifetime_value',
        color='risk_level',
        hover_data=['customer_id', 'name', 'segment'],
        color_discrete_map={
            'CRITICAL': '#ef4444',
            'HIGH': '#f59e0b',
            'MEDIUM': '#eab308',
            'LOW': '#10b981'
        },
        labels={
            'health_score': 'Health Score (%)',
            'churn_risk': 'Churn Risk (%)',
            'lifetime_value': 'Lifetime Value ($)'
        }
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.markdown("## ⚠️ At-Risk Customers Requiring Intervention")
    
    if not at_risk:
        st.success("🎉 No customers at critical risk! Great job!")
    else:
        # Display at-risk customers
        for i, alert in enumerate(at_risk[:15], 1):  # Top 15
            customer = alert['customer']
            
            # Risk color
            risk_pct = alert['churn_risk'] * 100
            if risk_pct >= 75:
                alert_class = "alert-high"
                risk_icon = "🔴"
            elif risk_pct >= 60:
                alert_class = "alert-medium"
                risk_icon = "🟠"
            else:
                alert_class = "alert-low"
                risk_icon = "🟡"
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{risk_icon} {customer.first_name} {customer.last_name}** ({customer.customer_id})")
                    st.caption(f"📍 {customer.segment} • {customer.loyalty_tier} • LTV: ${customer.lifetime_value:,.2f}")
                
                with col2:
                    st.metric("Health Score", f"{alert['health_score']*100:.1f}%")
                    st.metric("Churn Risk", f"{alert['churn_risk']*100:.1f}%")
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🎯 Intervene", key=f"btn_{i}"):
                        st.info("🤖 Agent pipeline would run here...")
                
                # Reasons
                with st.expander("📋 View Details"):
                    st.markdown("**Risk Factors:**")
                    for reason in alert['reasons'][:3]:
                        st.markdown(f"• {reason}")
                
                st.markdown("<hr style='margin: 0.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

with tab3:
    st.markdown("## 🤖 Multi-Agent System Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Agent Workflow")
        st.markdown("""
        ```
        ┌─────────────────┐
        │ Context Agent   │ → Sentiment & Urgency
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │ Pattern Agent   │ → Churn Prediction
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │ Decision Agent  │ → Action Strategy
        └────────┬────────┘
                 ↓
        ┌─────────────────┐
        │ Empathy Agent   │ → Personalized Message
        └─────────────────┘
        ```
        """)
    
    with col2:
        st.markdown("### 📊 Agent Performance")
        agent_data = pd.DataFrame({
            'Agent': ['Context', 'Pattern', 'Decision', 'Empathy'],
            'Executions': [147, 147, 147, 147],
            'Avg Time (s)': [0.8, 1.2, 0.9, 1.5],
            'Success Rate': [100, 98, 100, 100]
        })
        
        fig_agents = px.bar(
            agent_data,
            x='Agent',
            y='Executions',
            color='Avg Time (s)',
            color_continuous_scale='Viridis',
            text='Success Rate'
        )
        fig_agents.update_traces(texttemplate='%{text}% ✅', textposition='outside')
        fig_agents.update_layout(height=300)
        st.plotly_chart(fig_agents, use_container_width=True)
    
    # Language distribution
    st.markdown("### 🌍 Multi-Language Support")
    lang_data = pd.DataFrame({
        'Language': ['English', 'Hindi', 'Tamil', 'Telugu', 'Bengali'],
        'Messages': [45, 38, 22, 18, 24]
    })
    
    fig_lang = px.pie(
        lang_data,
        values='Messages',
        names='Language',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_lang.update_layout(height=400)
    st.plotly_chart(fig_lang, use_container_width=True)

with tab4:
    st.markdown("## 📈 Advanced Analytics")
    
    # Segment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Risk by Segment")
        segment_risk = health_df.groupby('segment')['churn_risk'].mean().reset_index()
        segment_risk['churn_risk'] = segment_risk['churn_risk'].round(1)
        
        fig_segment = px.bar(
            segment_risk,
            x='segment',
            y='churn_risk',
            color='churn_risk',
            color_continuous_scale='Reds',
            labels={'churn_risk': 'Avg Churn Risk (%)', 'segment': 'Customer Segment'}
        )
        fig_segment.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_segment, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 LTV by Loyalty Tier")
        tier_ltv = health_df.groupby('loyalty_tier')['lifetime_value'].mean().reset_index()
        tier_ltv['lifetime_value'] = tier_ltv['lifetime_value'].round(0)
        
        fig_tier = px.bar(
            tier_ltv,
            x='loyalty_tier',
            y='lifetime_value',
            color='lifetime_value',
            color_continuous_scale='Greens',
            labels={'lifetime_value': 'Avg LTV ($)', 'loyalty_tier': 'Loyalty Tier'}
        )
        fig_tier.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_tier, use_container_width=True)
    
    # Intervention timeline (simulated)
    st.markdown("### ⏰ Intervention Timeline (Last 24h)")
    timeline_data = pd.DataFrame({
        'Time': pd.date_range(end=datetime.now(), periods=12, freq='2h'),
        'Interventions': [3, 5, 2, 8, 4, 6, 9, 3, 5, 7, 4, 6]
    })
    
    fig_timeline = px.area(
        timeline_data,
        x='Time',
        y='Interventions',
        color_discrete_sequence=['#667eea']
    )
    fig_timeline.update_layout(height=300)
    st.plotly_chart(fig_timeline, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
    🔮 ProCX - Powered by LangGraph Multi-Agent AI • Built for Hackathon • Made with ❤️
</div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if auto_refresh:
    time.sleep(30)
    st.rerun()
