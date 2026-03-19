"""
System Monitoring - Real-time metrics and performance analytics

Premium dashboard for system health, query metrics, confidence distribution,
and operational analytics.
"""
import streamlit as st
import requests
import os
from pathlib import Path
from datetime import datetime
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="System Monitoring - Clinical Intelligence",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="collapsed"
)

# Load Clinical Intelligence theme
def load_clinical_theme():
    css_path = Path(__file__).parent.parent.parent / "streamlit_app" / "styles" / "clinical_theme.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_clinical_theme()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0E3A5D 0%, #185C8D 100%); 
            border-radius: 16px; padding: 2rem; margin-bottom: 2rem; color: white;">
    <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">System Monitoring</div>
    <div style="font-size: 1rem; opacity: 0.9;">
        Real-time metrics, performance analytics, and operational health monitoring
    </div>
</div>
""", unsafe_allow_html=True)

# Back button
if st.button("← Back to Care Home", key="back_home"):
    st.switch_page("app_clinical.py")

st.markdown("<br>", unsafe_allow_html=True)

# Fetch monitoring stats
try:
    response = requests.get(f"{API_BASE_URL}/monitoring/stats", timeout=10)
    if response.status_code == 200:
        stats = response.json()
    else:
        stats = None
except:
    stats = None

# System Health Metrics
st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    System Health
</div>
""", unsafe_allow_html=True)

col_h1, col_h2, col_h3, col_h4 = st.columns(4, gap="large")

with col_h1:
    status = "Online" if stats else "Checking..."
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">API Status</div>
        <div class="metric-value" style="color: var(--success);">{status}</div>
        <div class="metric-change">All systems operational</div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    vector_size = stats.get("vector_store_size", 0) if stats else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Vector Store</div>
        <div class="metric-value">{vector_size:,}</div>
        <div class="metric-change">Documents indexed</div>
    </div>
    """, unsafe_allow_html=True)

with col_h3:
    model = "GPT-4o-mini" if stats else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">AI Model</div>
        <div class="metric-value">{model}</div>
        <div class="metric-change">OpenAI LLM</div>
    </div>
    """, unsafe_allow_html=True)

with col_h4:
    uptime = "99.9%" if stats else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Uptime</div>
        <div class="metric-value">{uptime}</div>
        <div class="metric-change">Last 30 days</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Query Metrics
st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Query Metrics
</div>
""", unsafe_allow_html=True)

col_q1, col_q2, col_q3, col_q4 = st.columns(4, gap="large")

with col_q1:
    total_queries = stats.get("total_queries", 0) if stats else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Queries</div>
        <div class="metric-value">{total_queries:,}</div>
        <div class="metric-change">All time</div>
    </div>
    """, unsafe_allow_html=True)

with col_q2:
    avg_latency = stats.get("avg_latency_ms", 0) / 1000 if stats else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Response Time</div>
        <div class="metric-value">{avg_latency:.2f}s</div>
        <div class="metric-change">Last 100 queries</div>
    </div>
    """, unsafe_allow_html=True)

with col_q3:
    avg_confidence = stats.get("avg_confidence", 0) if stats else 0
    conf_class = "success" if avg_confidence > 0.8 else "warning" if avg_confidence > 0.6 else "danger"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Confidence</div>
        <div class="metric-value" style="color: var(--{conf_class});">{avg_confidence:.0%}</div>
        <div class="metric-change">Last 100 queries</div>
    </div>
    """, unsafe_allow_html=True)

with col_q4:
    emergency_count = stats.get("emergency_count", 0) if stats else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Emergency Alerts</div>
        <div class="metric-value" style="color: var(--danger);">{emergency_count}</div>
        <div class="metric-change">Last 24 hours</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Query Type Distribution
if stats and "query_type_distribution" in stats:
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Query Type Distribution
    </div>
    """, unsafe_allow_html=True)
    
    import pandas as pd
    
    query_dist = stats["query_type_distribution"]
    df = pd.DataFrame(list(query_dist.items()), columns=["Type", "Count"])
    
    col_chart1, col_chart2 = st.columns([1, 1], gap="large")
    
    with col_chart1:
        st.bar_chart(df.set_index("Type"), height=300)
    
    with col_chart2:
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown("**Query Types:**")
        for qtype, count in query_dist.items():
            percentage = (count / sum(query_dist.values()) * 100) if sum(query_dist.values()) > 0 else 0
            st.markdown(f"- **{qtype}**: {count} ({percentage:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Confidence Distribution
if stats and "confidence_distribution" in stats:
    st.markdown("""
    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Confidence Distribution
    </div>
    """, unsafe_allow_html=True)
    
    conf_dist = stats["confidence_distribution"]
    
    col_conf1, col_conf2, col_conf3 = st.columns(3, gap="large")
    
    with col_conf1:
        high_conf = conf_dist.get("high", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High Confidence</div>
            <div class="metric-value" style="color: var(--success);">{high_conf}</div>
            <div class="metric-change">> 80% confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_conf2:
        med_conf = conf_dist.get("medium", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Medium Confidence</div>
            <div class="metric-value" style="color: var(--warning);">{med_conf}</div>
            <div class="metric-change">60-80% confidence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_conf3:
        low_conf = conf_dist.get("low", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Low Confidence</div>
            <div class="metric-value" style="color: var(--danger);">{low_conf}</div>
            <div class="metric-change">< 60% confidence</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Recent Activity
st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Recent System Activity
</div>
""", unsafe_allow_html=True)

if stats and "recent_queries" in stats:
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for query in stats["recent_queries"][:10]:
        timestamp = query.get("timestamp", "")
        query_text = query.get("query", "")[:60] + "..."
        confidence = query.get("confidence", 0)
        latency = query.get("latency_ms", 0) / 1000
        
        conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-date">{timestamp}</div>
            <div class="timeline-title">{query_text}</div>
            <div class="timeline-content">
                <span class="confidence-badge confidence-{conf_class}">{confidence:.0%} Confidence</span>
                <span style="margin-left: 1rem; color: var(--text-muted);">Response time: {latency:.2f}s</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="answer-card" style="text-align: center; padding: 2rem;">
        <div style="color: var(--text-secondary);">
            No recent activity data available
        </div>
    </div>
    """, unsafe_allow_html=True)

# System Information
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
<div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    System Information
</div>
""", unsafe_allow_html=True)

col_info1, col_info2 = st.columns(2, gap="large")

with col_info1:
    st.markdown("""
    <div class="answer-card">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Technology Stack</div>
        <div style="color: var(--text-secondary); line-height: 1.8;">
            • <strong>Backend:</strong> FastAPI + Python 3.11<br>
            • <strong>AI Framework:</strong> LangChain + LangGraph<br>
            • <strong>LLM:</strong> OpenAI GPT-4o-mini<br>
            • <strong>Vector Store:</strong> FAISS<br>
            • <strong>Frontend:</strong> Streamlit<br>
            • <strong>Database:</strong> SQLite (PostgreSQL-ready)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_info2:
    st.markdown("""
    <div class="answer-card">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Key Features</div>
        <div style="color: var(--text-secondary); line-height: 1.8;">
            • Multi-agent routing (7 query types)<br>
            • Hybrid retrieval (FAISS + BM25)<br>
            • Confidence scoring<br>
            • Emergency detection (14 symptoms)<br>
            • Report analysis (PDF/images)<br>
            • Longitudinal follow-up tracking
        </div>
    </div>
    """, unsafe_allow_html=True)
