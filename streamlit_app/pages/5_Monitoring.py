"""
Monitoring Dashboard - System metrics and analytics.
"""
import streamlit as st
import requests
import os
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status
from components.cards import metric_card

# Page config
st.set_page_config(
    page_title="Monitoring - Healthcare AI",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header("Monitoring Dashboard", "Real-time system metrics and analytics")

API_BASE = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")

try:
    stats_response = requests.get(f"{API_BASE}/monitoring/stats", timeout=10)
    
    if stats_response.status_code == 200:
        data = stats_response.json()
        stats = data.get("stats", {})
        
        # KPI Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card("Total Queries", str(stats.get("total_queries", 0)))
        
        with col2:
            avg_latency = stats.get("avg_latency_ms", 0)
            metric_card("Avg Latency", f"{int(avg_latency)}ms" if avg_latency > 0 else "N/A")
        
        with col3:
            avg_conf = stats.get("avg_confidence", 0)
            metric_card("Avg Confidence", f"{int(avg_conf * 100)}%" if avg_conf > 0 else "N/A")
        
        with col4:
            low_conf = stats.get("confidence_distribution", {}).get("low", 0)
            metric_card("Low Confidence Alerts", str(low_conf))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Query Type Distribution")
            query_dist = stats.get("query_type_distribution", {})
            
            if query_dist:
                fig = go.Figure(data=[go.Bar(
                    x=list(query_dist.keys()),
                    y=list(query_dist.values()),
                    marker_color='#0F4C81'
                )])
                fig.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=20, b=0),
                    paper_bgcolor='white',
                    plot_bgcolor='#F7FAFC',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#D9E2EC')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No query data available yet")
        
        with col2:
            st.markdown("### Confidence Distribution")
            conf_dist = stats.get("confidence_distribution", {})
            
            if any(conf_dist.values()):
                labels = list(conf_dist.keys())
                values = list(conf_dist.values())
                colors = ['#2F855A', '#B7791F', '#C53030']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    hole=0.4
                )])
                fig.update_layout(
                    height=300,
                    margin=dict(l=0, r=0, t=20, b=0),
                    paper_bgcolor='white',
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No confidence data available yet")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Latency percentiles
        st.markdown("### Response Latency")
        percentiles = stats.get("latency_percentiles", {})
        
        if any(percentiles.values()):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                p50 = percentiles.get("p50", 0)
                st.markdown(f'''
                <div style="background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 13px; color: #486581; margin-bottom: 8px;">P50 (Median)</div>
                    <div style="font-size: 28px; font-weight: 700; color: #0F4C81;">{int(p50)}ms</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                p95 = percentiles.get("p95", 0)
                st.markdown(f'''
                <div style="background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 13px; color: #486581; margin-bottom: 8px;">P95</div>
                    <div style="font-size: 28px; font-weight: 700; color: #0F4C81;">{int(p95)}ms</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                p99 = percentiles.get("p99", 0)
                st.markdown(f'''
                <div style="background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 13px; color: #486581; margin-bottom: 8px;">P99</div>
                    <div style="font-size: 28px; font-weight: 700; color: #0F4C81;">{int(p99)}ms</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No latency data available yet")
        
        # Success rate
        st.markdown("<br>", unsafe_allow_html=True)
        success_rate = stats.get("success_rate", 1.0)
        error_count = stats.get("error_count", 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'''
            <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
                <div style="font-weight: 600; font-size: 16px; color: #102A43; margin-bottom: 16px;">Success Rate</div>
                <div style="font-size: 48px; font-weight: 700; color: #2F855A; text-align: center;">{int(success_rate * 100)}%</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px;">
                <div style="font-weight: 600; font-size: 16px; color: #102A43; margin-bottom: 16px;">Error Count</div>
                <div style="font-size: 48px; font-weight: 700; color: #C53030; text-align: center;">{error_count}</div>
            </div>
            ''', unsafe_allow_html=True)
        
    else:
        st.error("Unable to fetch monitoring data")
        
except requests.Timeout:
    st.error("Request timed out. API may be sleeping.")
except Exception as e:
    st.error(f"Error fetching monitoring data: {str(e)}")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Monitoring updates in real-time • Metrics stored for last 1000 queries
</div>
''', unsafe_allow_html=True)
