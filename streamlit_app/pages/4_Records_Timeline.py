"""
Records Timeline Page - Persistent healthcare system

Two-pane layout:
- Left: List/timeline with search and filters
- Right: Selected record detail
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from components.healthcare_components import (
    render_app_shell,
    render_sidebar_nav,
    render_page_header,
    render_metric_card,
    format_timestamp
)

# Page config
render_app_shell()

# Sidebar
render_sidebar_nav("Records Timeline")

# Page header
render_page_header(
    "Records Timeline",
    "Chronological view of all care activities, analyses, and system interactions"
)

# Collect all timeline events
timeline_events = []

# Add AI Q&A history
if "ai_qa_history" in st.session_state:
    for item in st.session_state.ai_qa_history:
        timeline_events.append({
            "timestamp": item.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "type": "AI Question",
            "title": item.get("query", "")[:60] + "...",
            "content": item.get("answer", {}).get("answer", "")[:150] + "...",
            "confidence": item.get("answer", {}).get("confidence", 0),
            "icon": "💬",
            "data": item
        })

# Add daily updates
if "daily_updates" in st.session_state:
    for item in st.session_state.daily_updates:
        timeline_events.append({
            "timestamp": item.get("timestamp", item.get("date", "")),
            "type": "Daily Check-in",
            "title": f"{item.get('condition_trend', 'Unknown')} | Risk: {item.get('risk_level', 'unknown').title()}",
            "content": item.get("summary", ""),
            "risk_level": item.get("risk_level", "low"),
            "icon": "📊",
            "data": item
        })

# Add report analyses
if "report_analysis" in st.session_state and st.session_state.report_analysis:
    timeline_events.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Report Analysis",
        "title": "Medical Report Analyzed",
        "content": st.session_state.report_analysis.get("summary", "")[:150] + "...",
        "confidence": st.session_state.report_analysis.get("confidence", 0),
        "icon": "📄",
        "data": st.session_state.report_analysis
    })

# Sort by timestamp (most recent first)
timeline_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

# Initialize selected record
if "selected_record" not in st.session_state:
    st.session_state.selected_record = None

# Summary metrics
if timeline_events:
    col_m1, col_m2, col_m3, col_m4 = st.columns(4, gap="large")
    
    with col_m1:
        render_metric_card("Total Activities", str(len(timeline_events)), "All time")
    
    with col_m2:
        ai_questions = len([e for e in timeline_events if e["type"] == "AI Question"])
        render_metric_card("AI Questions", str(ai_questions), "Total")
    
    with col_m3:
        daily_checkins = len([e for e in timeline_events if e["type"] == "Daily Check-in"])
        render_metric_card("Daily Check-ins", str(daily_checkins), "Total")
    
    with col_m4:
        high_risk = len([e for e in timeline_events if e.get("risk_level") == "high"])
        render_metric_card("High Risk Alerts", str(high_risk), "Total")
    
    st.markdown("<br><br>", unsafe_allow_html=True)

# Two-pane layout
col_list, col_detail = st.columns([1, 1.5], gap="large")

with col_list:
    # Section 1: Search + Filters
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Activity Timeline
    </div>
    """, unsafe_allow_html=True)
    
    # Search bar
    search_query = st.text_input("Search records", placeholder="Search by keyword...", label_visibility="collapsed")
    
    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_type = st.selectbox("Type", ["All", "AI Question", "Daily Check-in", "Report Analysis"])
    with col_f2:
        filter_risk = st.selectbox("Risk", ["All", "High", "Medium", "Low"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section 2: Records List / Timeline
    if timeline_events:
        filtered_events = timeline_events
        
        # Apply filters
        if filter_type != "All":
            filtered_events = [e for e in filtered_events if e["type"] == filter_type]
        
        if filter_risk != "All":
            filtered_events = [e for e in filtered_events if e.get("risk_level", "").lower() == filter_risk.lower()]
        
        # Apply search
        if search_query:
            filtered_events = [e for e in filtered_events if search_query.lower() in e["title"].lower() or search_query.lower() in e["content"].lower()]
        
        st.markdown(f"**{len(filtered_events)} records found**")
        st.markdown("<br>", unsafe_allow_html=True)
        
        for idx, event in enumerate(filtered_events):
            # Format timestamp
            try:
                ts = datetime.strptime(event["timestamp"], "%Y-%m-%d %H:%M:%S")
                date_str = ts.strftime("%b %d, %Y")
            except:
                date_str = event["timestamp"]
            
            # Confidence badge if applicable
            conf_badge = ""
            if "confidence" in event:
                conf = event["confidence"]
                conf_class = "high" if conf > 0.8 else "medium" if conf > 0.6 else "low"
                conf_badge = f'<span class="confidence-badge confidence-{conf_class}" style="font-size: 0.75rem;">{conf:.0%}</span>'
            
            # Risk badge if applicable
            risk_badge = ""
            if "risk_level" in event:
                risk_level = event["risk_level"]
                risk_class = "high" if risk_level == "high" else "medium" if risk_level == "medium" else "low"
                risk_badge = f'<span class="confidence-badge confidence-{risk_class}" style="font-size: 0.75rem;">{risk_level.title()}</span>'
            
            # Record card
            is_selected = st.session_state.selected_record == idx
            border_color = "var(--teal-primary)" if is_selected else "var(--border-light)"
            
            st.markdown(f"""
            <div style="border: 2px solid {border_color}; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; cursor: pointer; background: var(--card-white);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <div style="font-weight: 600; color: var(--text-primary);">{event['icon']} {event['type']}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">{date_str}</div>
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    {event['title']}
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    {conf_badge}
                    {risk_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details", key=f"view_{idx}", use_container_width=True):
                st.session_state.selected_record = idx
                st.rerun()
    else:
        st.info("No records available yet")

# Section 3: Record Detail View
with col_detail:
    st.markdown("""
    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
        Record Details
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.selected_record is not None and st.session_state.selected_record < len(timeline_events):
        event = timeline_events[st.session_state.selected_record]
        
        st.markdown(f"""
        <div class="answer-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="font-size: 1.1rem; font-weight: 700;">{event['icon']} {event['type']}</div>
                <div style="font-size: 0.875rem; color: var(--text-muted);">{format_timestamp(event['timestamp'])}</div>
            </div>
            
            <div style="font-size: 1rem; font-weight: 600; margin-bottom: 1rem;">
                {event['title']}
            </div>
            
            <div style="color: var(--text-secondary); line-height: 1.7; margin-bottom: 1rem;">
                {event['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show full data based on type
        data = event.get("data", {})
        
        if event["type"] == "AI Question":
            if data.get("answer", {}).get("key_insights"):
                st.markdown("**Key Insights:**")
                for insight in data["answer"]["key_insights"]:
                    st.markdown(f"- {insight}")
        
        elif event["type"] == "Daily Check-in":
            st.markdown("**Check-in Details:**")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"**Pain Level:** {data.get('pain_level', 'N/A')}/10")
                st.markdown(f"**Sleep:** {data.get('sleep_quality', 'N/A')}")
            with col_d2:
                st.markdown(f"**Appetite:** {data.get('appetite', 'N/A')}")
                st.markdown(f"**Hydration:** {data.get('hydration', 'N/A')}")
        
        elif event["type"] == "Report Analysis":
            if data.get("extracted_values"):
                st.markdown("**Extracted Values:**")
                st.markdown(f"Total: {len(data['extracted_values'])}")
    
    else:
        st.markdown("""
        <div class="answer-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.3;">📋</div>
            <div style="color: var(--text-secondary);">
                Select a record from the timeline to view details
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
    if st.button("Export Timeline", use_container_width=True):
        st.info("Timeline export feature coming soon")

with col_f3:
    if st.button("Generate Report", use_container_width=True):
        st.info("Report generation feature coming soon")
