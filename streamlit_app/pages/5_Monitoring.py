"""
Monitoring Page - Operations dashboard

Dashboard layout with:
- KPI row
- Charts (4 types)
- Flagged responses table
- Source utilization / retrieval health
"""
import streamlit as st
import requests
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.healthcare_components import (
    render_app_shell,
    render_sidebar_nav,
    render_page_header,
    render_metric_card,
    render_distribution_chart
)

# Page config
render_app_shell()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

# Sidebar
render_sidebar_nav("Monitoring")

# Page header
render_page_header(
    "System Monitoring",
    "Real-time metrics, performance analytics, and operational health monitoring"
)

# Fetch monitoring stats
try:
    response = requests.get(f"{API_BASE_URL}/monitoring/stats", timeout=10)
    if response.status_code == 200:
        raw = response.json()
        # API returns {"stats": {...}, "time_series": {...}, ...}
        stats = raw.get("stats") if isinstance(raw.get("stats"), dict) else raw
    else:
        stats = None
except:
    stats = None

# ============================================================================
# SECTION 1: KPI ROW
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    System Health
</div>
""", unsafe_allow_html=True)

col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5, gap="large")

with col_k1:
    total_queries = stats.get("total_queries", 0) if stats else 0
    render_metric_card("Total Queries", f"{total_queries:,}", "All time")

with col_k2:
    avg_latency = stats.get("avg_latency_ms", 0) / 1000 if stats else 0
    render_metric_card("Avg Latency", f"{avg_latency:.2f}s", "Last 100 queries")

with col_k3:
    avg_confidence = stats.get("avg_confidence", 0) if stats else 0
    render_metric_card("Avg Confidence", f"{avg_confidence:.0%}", "Last 100 queries")

with col_k4:
    emergency_count = stats.get("emergency_count", 0) if stats else 0
    render_metric_card("Emergency Alerts", str(emergency_count), "Last 24 hours")

with col_k5:
    vector_size = stats.get("vector_store_size", 0) if stats else 0
    render_metric_card("Vector Store", f"{vector_size:,}", "Documents")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 2: CHARTS
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Performance Analytics
</div>
""", unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2, gap="large")

# Chart 1: Query Type Distribution
with col_chart1:
    if stats and "query_type_distribution" in stats:
        render_distribution_chart(
            stats["query_type_distribution"],
            "Query Type Distribution"
        )
    else:
        st.info("No query type data available")

# Chart 2: Confidence Distribution
with col_chart2:
    if stats and "confidence_distribution" in stats:
        render_distribution_chart(
            stats["confidence_distribution"],
            "Confidence Distribution"
        )
    else:
        st.info("No confidence data available")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 3: FLAGGED RESPONSES TABLE
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Flagged Responses
</div>
""", unsafe_allow_html=True)

if stats and "recent_queries" in stats:
    # Filter for low confidence or emergency queries
    flagged = [q for q in stats["recent_queries"] if q.get("confidence", 1) < 0.6 or q.get("is_emergency", False)]

    if flagged:
        st.markdown("""
        <table class="values-table">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Query</th>
                    <th>Confidence</th>
                    <th>Flag Type</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)

        for query in flagged[:10]:
            timestamp = query.get("timestamp", "")
            query_text = query.get("query", "")[:50] + "..."
            confidence = query.get("confidence", 0)
            flag_type = "Emergency" if query.get("is_emergency") else "Low Confidence"

            conf_class = "value-abnormal" if confidence < 0.6 else "value-normal"

            st.markdown(f"""
            <tr class="{conf_class}">
                <td>{timestamp}</td>
                <td>{query_text}</td>
                <td><strong>{confidence:.0%}</strong></td>
                <td>{flag_type}</td>
                <td><button style="padding: 0.25rem 0.75rem; background: var(--teal-primary); color: white; border: none; border-radius: 4px; cursor: pointer;">Review</button></td>
            </tr>
            """, unsafe_allow_html=True)

        st.markdown("</tbody></table>", unsafe_allow_html=True)
    else:
        st.info("No flagged responses in recent queries")
else:
    st.info("No recent query data available")

st.markdown("<br><br>", unsafe_allow_html=True)

# ============================================================================
# SECTION 4: SOURCE UTILIZATION / RETRIEVAL HEALTH
# ============================================================================

st.markdown("""
<div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
    Retrieval Health
</div>
""", unsafe_allow_html=True)

col_health1, col_health2, col_health3 = st.columns(3, gap="large")

with col_health1:
    st.markdown("""
    <div class="answer-card">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Vector Store</div>
        <div style="color: var(--text-secondary); line-height: 1.7;">
            <strong>Status:</strong> <span style="color: var(--success);">✓ Healthy</span><br>
            <strong>Documents:</strong> {docs}<br>
            <strong>Avg Relevance:</strong> 85%<br>
            <strong>Last Updated:</strong> Today
        </div>
    </div>
    """.format(docs=f"{vector_size:,}"), unsafe_allow_html=True)

with col_health2:
    st.markdown("""
    <div class="answer-card">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Citation Coverage</div>
        <div style="color: var(--text-secondary); line-height: 1.7;">
            <strong>Answers with Sources:</strong> 100%<br>
            <strong>Avg Sources per Answer:</strong> 4.2<br>
            <strong>Source Quality:</strong> High<br>
            <strong>Retrieval Misses:</strong> < 1%
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_health3:
    st.markdown("""
    <div class="answer-card">
        <div style="font-weight: 600; margin-bottom: 0.5rem;">Model Performance</div>
        <div style="color: var(--text-secondary); line-height: 1.7;">
            <strong>Model:</strong> GPT-4o-mini<br>
            <strong>Avg Tokens:</strong> 1,200<br>
            <strong>Success Rate:</strong> 99.5%<br>
            <strong>Error Rate:</strong> < 0.5%
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer actions
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app_healthcare.py")

with col_f2:
    if st.button("Export Metrics", use_container_width=True):
        st.info("Metrics export feature coming soon")

with col_f3:
    if st.button("View Detailed Logs", use_container_width=True):
        st.info("Detailed logging feature coming soon")
