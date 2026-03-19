"""
Records & History - View past analyses and conversations.
"""
import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status

# Page config
st.set_page_config(
    page_title="Records & History",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header("Records & History", "View past analyses and conversation history")

# Search and filters
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("Search records", placeholder="Search by keyword...", label_visibility="collapsed")

with col2:
    record_type = st.selectbox("Type", ["All", "Chat", "Report", "Emergency"], label_visibility="collapsed")

with col3:
    date_filter = st.selectbox("Date", ["All Time", "Today", "This Week", "This Month"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### Timeline")
    
    # Check if there are any records in session state
    if "history" not in st.session_state or not st.session_state.history:
        st.markdown('''
        <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 40px 24px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">📁</div>
            <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 8px;">No Records Yet</div>
            <div style="font-size: 14px; color: #486581;">Your conversation history and report analyses will appear here</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        # Display records
        for idx, record in enumerate(st.session_state.history):
            record_date = record.get("date", "Unknown date")
            record_title = record.get("title", "Untitled")
            record_summary = record.get("summary", "No summary")
            record_confidence = record.get("confidence", 0.0)
            
            conf_color = "#2F855A" if record_confidence >= 0.85 else "#B7791F" if record_confidence >= 0.65 else "#C53030"
            
            st.markdown(f'''
            <div style="background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: 16px; margin-bottom: 12px; cursor: pointer;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="font-weight: 600; font-size: 14px; color: #102A43;">{record_title}</div>
                    <div style="font-size: 11px; color: #486581;">{record_date}</div>
                </div>
                <div style="font-size: 13px; color: #486581; margin-bottom: 8px;">{record_summary[:100]}...</div>
                <div style="font-size: 12px; color: {conf_color}; font-weight: 600;">Confidence: {int(record_confidence * 100)}%</div>
            </div>
            ''', unsafe_allow_html=True)

with col2:
    st.markdown("### Record Detail")
    
    st.markdown('''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 40px 24px; text-align: center;">
        <div style="font-size: 14px; color: #486581;">Select a record from the timeline to view details</div>
    </div>
    ''', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('''
<div style="text-align: center; color: #486581; font-size: 12px; padding: 20px 0; border-top: 1px solid #D9E2EC;">
    Records are stored in your session • Clear browser data to reset
</div>
''', unsafe_allow_html=True)
