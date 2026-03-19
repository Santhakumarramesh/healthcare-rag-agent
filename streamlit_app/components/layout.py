"""
Layout components for consistent page structure.
"""
import streamlit as st
from pathlib import Path


def load_css():
    """Load custom CSS."""
    css_path = Path(__file__).parent.parent / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar_status():
    """Render sidebar status cards."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")
    
    import requests
    import os
    
    API_BASE = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")
    
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            
            # API Status
            status = "✓ Healthy" if health.get("status") == "healthy" else "⚠ Degraded"
            color = "#2F855A" if health.get("status") == "healthy" else "#B7791F"
            st.sidebar.markdown(f'<div style="background: white; border: 1px solid #D9E2EC; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;"><span style="color: {color}; font-weight: 600; font-size: 12px;">{status}</span><br><span style="color: #486581; font-size: 11px;">API Status</span></div>', unsafe_allow_html=True)
            
            # Vector Store
            vs_status = "✓ Ready" if health.get("vector_store_ready") else "⚠ Not Ready"
            vs_color = "#2F855A" if health.get("vector_store_ready") else "#B7791F"
            st.sidebar.markdown(f'<div style="background: white; border: 1px solid #D9E2EC; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;"><span style="color: {vs_color}; font-weight: 600; font-size: 12px;">{vs_status}</span><br><span style="color: #486581; font-size: 11px;">Vector Store</span></div>', unsafe_allow_html=True)
            
            # Model
            model = health.get("model", "N/A")
            st.sidebar.markdown(f'<div style="background: white; border: 1px solid #D9E2EC; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;"><span style="color: #0F4C81; font-weight: 600; font-size: 12px;">{model}</span><br><span style="color: #486581; font-size: 11px;">Model</span></div>', unsafe_allow_html=True)
            
    except:
        st.sidebar.markdown('<div style="background: white; border: 1px solid #D9E2EC; border-radius: 8px; padding: 8px 12px;"><span style="color: #C53030; font-weight: 600; font-size: 12px;">⚠ Offline</span><br><span style="color: #486581; font-size: 11px;">API Status</span></div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render consistent page header."""
    st.markdown(f'<h1 style="color: #102A43; font-weight: 700; font-size: 28px; margin-bottom: 4px;">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p style="color: #486581; font-size: 14px; margin-bottom: 24px;">{subtitle}</p>', unsafe_allow_html=True)
