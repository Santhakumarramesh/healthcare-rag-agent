"""
Healthcare-Specific Component Library

Reusable components for the AI Healthcare Copilot platform.
"""
import streamlit as st
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def render_app_shell():
    """Global app shell with sidebar and header."""
    st.set_page_config(
        page_title="AI Healthcare Copilot",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load CSS
    load_clinical_css()


def render_sidebar_nav(current_page: str):
    """Render sidebar navigation."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; border-bottom: 1px solid var(--border-light);">
        <div style="font-size: 1.5rem; font-weight: 700; color: var(--navy-deep);">
            AI Healthcare Copilot
        </div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
            Grounded medical intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation links
    pages = {
        "Home": "app_healthcare.py",
        "Analyze Report": "pages/1_Analyze_Report.py",
        "Ask AI": "pages/2_Ask_AI.py",
        "Follow-up Monitor": "pages/3_Followup_Monitor.py",
        "Records Timeline": "pages/4_Records_Timeline.py",
        "Monitoring": "pages/5_Monitoring.py",
        "Settings": "pages/6_Settings.py"
    }
    
    for page_name, page_path in pages.items():
        active = "background: var(--info-light); border-left: 3px solid var(--teal-primary);" if page_name == current_page else ""
        st.sidebar.markdown(f"""
        <div style="padding: 0.75rem 1rem; margin-bottom: 0.25rem; cursor: pointer; border-radius: 8px; {active}">
            <a href="{page_path}" style="text-decoration: none; color: var(--text-primary); font-weight: 500;">
                {page_name}
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    
    # System status
    render_sidebar_system_status()


def render_sidebar_system_status():
    """Render system status in sidebar."""
    st.sidebar.markdown("""
    <div style="border-top: 1px solid var(--border-light); padding-top: 1rem;">
        <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;">
            System Status
        </div>
    """, unsafe_allow_html=True)
    
    render_status_card("API", "Online", "success")
    render_status_card("Vector Store", "Ready", "success")
    render_status_card("Model", "GPT-4o-mini", "info")
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str):
    """Render page header."""
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div style="font-size: 2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
            {title}
        </div>
        <div style="font-size: 1rem; color: var(--text-secondary);">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)


def load_clinical_css():
    """Load Clinical Intelligence CSS."""
    from pathlib import Path
    css_path = Path(__file__).parent.parent / "styles" / "clinical_theme.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ============================================================================
# CARD COMPONENTS
# ============================================================================

def render_hero_banner(title: str, subtitle: str, primary_cta: str, secondary_cta: str, 
                       primary_action=None, secondary_action=None):
    """Render hero banner."""
    st.markdown(f"""
    <div class="care-home-hero">
        <div class="care-home-title">{title}</div>
        <div class="care-home-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button(primary_cta, key="hero_primary", type="primary", use_container_width=True):
            if primary_action:
                primary_action()
    with col2:
        if st.button(secondary_cta, key="hero_secondary", use_container_width=True):
            if secondary_action:
                secondary_action()


def render_mode_card(title: str, description: str, icon: str, button_text: str, 
                     button_key: str, action=None):
    """Render care mode card."""
    st.markdown(f"""
    <div class="mode-card">
        <div class="mode-card-icon">{icon}</div>
        <div class="mode-card-title">{title}</div>
        <div class="mode-card-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(button_text, key=button_key, use_container_width=True, type="primary"):
        if action:
            action()


def render_metric_card(label: str, value: str, change: Optional[str] = None):
    """Render metric card."""
    change_html = f'<div class="metric-change">{change}</div>' if change else ''
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_card(label: str, value: str, status: str = "info"):
    """Render status card in sidebar."""
    color_map = {
        "success": "var(--success)",
        "warning": "var(--warning)",
        "danger": "var(--danger)",
        "info": "var(--text-primary)"
    }
    color = color_map.get(status, "var(--text-primary)")
    
    st.sidebar.markdown(f"""
    <div class="status-card" style="margin-bottom: 0.5rem;">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_clinical_summary_card(summary: str, confidence: float, report_type: str = ""):
    """Render clinical summary card."""
    conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
    
    st.markdown(f"""
    <div class="answer-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.25rem; font-weight: 700;">Clinical Summary</div>
            <span class="confidence-badge confidence-{conf_class}">{confidence:.0%} Confidence</span>
        </div>
        {f'<div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem;">Report Type: {report_type}</div>' if report_type else ''}
        <div class="answer-summary">{summary}</div>
    </div>
    """, unsafe_allow_html=True)


def render_trust_panel():
    """Render trust panel."""
    st.markdown("""
    <div class="trust-panel">
        <div class="trust-panel-title">Why Trust This System</div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Evidence-Based Responses</div>
                <div class="trust-item-description">
                    Every answer cites medical sources with relevance scores
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Confidence Transparency</div>
                <div class="trust-item-description">
                    Multi-factor confidence scoring displayed for every response
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Emergency Detection</div>
                <div class="trust-item-description">
                    14 critical symptoms trigger immediate risk alerts
                </div>
            </div>
        </div>
        
        <div class="trust-item">
            <div class="trust-item-icon">✓</div>
            <div class="trust-item-content">
                <div class="trust-item-title">Safety Boundaries</div>
                <div class="trust-item-description">
                    Clear disclaimers - designed to support, not replace clinicians
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# HEALTHCARE-SPECIFIC COMPONENTS
# ============================================================================

def render_confidence_badge(confidence: float, size: str = "medium"):
    """Render confidence badge."""
    conf_class = "high" if confidence > 0.8 else "medium" if confidence > 0.6 else "low"
    size_class = "text-sm" if size == "small" else "text-base" if size == "medium" else "text-lg"
    
    st.markdown(f"""
    <span class="confidence-badge confidence-{conf_class} {size_class}">
        {confidence:.0%} Confidence
    </span>
    """, unsafe_allow_html=True)


def render_risk_alert_banner(level: str, message: str):
    """Render risk alert banner."""
    icons = {"high": "⚠️", "medium": "⚡", "low": "✓"}
    icon = icons.get(level, "ℹ️")
    
    st.markdown(f"""
    <div class="risk-alert risk-alert-{level}">
        <div class="risk-alert-icon">{icon}</div>
        <div class="risk-alert-content">
            <div class="risk-alert-title">{level.title()} Risk</div>
            <div class="risk-alert-message">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_safety_notice(message: str = None):
    """Render safety notice card."""
    default_message = """
    This AI assistant provides information only and does not replace professional medical advice.
    Always consult qualified healthcare professionals for medical decisions, diagnosis, or treatment.
    In case of emergency, call emergency services or go to the nearest emergency room.
    """
    
    st.markdown(f"""
    <div class="safety-card">
        <div class="safety-title">⚠️ Safety Boundary</div>
        <div class="safety-content">{message or default_message}</div>
    </div>
    """, unsafe_allow_html=True)


def render_important_values_table(values: List[Dict[str, Any]]):
    """Render important values table."""
    if not values:
        st.info("No extracted values available")
        return
    
    st.markdown("""
    <table class="values-table">
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Value</th>
                <th>Unit</th>
                <th>Reference Range</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    for val in values:
        is_abnormal = val.get("is_abnormal", False)
        row_class = "value-abnormal" if is_abnormal else "value-normal"
        status = "⚠️ Abnormal" if is_abnormal else "✓ Normal"
        
        st.markdown(f"""
        <tr class="{row_class}">
            <td>{val.get('test_name', 'N/A')}</td>
            <td><strong>{val.get('value', 'N/A')}</strong></td>
            <td>{val.get('unit', '')}</td>
            <td>{val.get('reference_range', 'N/A')}</td>
            <td>{status}</td>
        </tr>
        """, unsafe_allow_html=True)
    
    st.markdown("</tbody></table>", unsafe_allow_html=True)


def render_source_citation_card(source: Dict[str, Any], index: int):
    """Render source citation card."""
    title = source.get("title", f"Source {index}")
    content = source.get("content", "")[:200] + "..."
    relevance = source.get("relevance_score", 0)
    category = source.get("category", "Medical")
    
    st.markdown(f"""
    <div class="evidence-source">
        <div class="evidence-header">
            <div class="evidence-title">{title}</div>
            <div class="evidence-relevance">Relevance: {relevance:.0%}</div>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem;">
            {category}
        </div>
        <div class="evidence-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_check_in_timeline(updates: List[Dict[str, Any]]):
    """Render check-in timeline."""
    if not updates:
        st.info("No check-ins available yet")
        return
    
    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    
    for update in updates[-7:]:  # Last 7 check-ins
        date = update.get("date", "")
        trend = update.get("condition_trend", "Unknown")
        risk = update.get("risk_level", "low")
        summary = update.get("summary", "")
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-date">{date}</div>
            <div class="timeline-title">{trend} | Risk: {risk.title()}</div>
            <div class="timeline-content">{summary}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# INPUT COMPONENTS
# ============================================================================

def render_query_input_bar(placeholder: str = "Enter your medical question...", 
                           key: str = "query_input"):
    """Render query input bar."""
    query = st.text_area(
        "",
        height=120,
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        ask_btn = st.button("Ask Question", type="primary", use_container_width=True, key=f"{key}_btn")
    
    return query, ask_btn


def render_upload_dropzone(key: str = "file_upload"):
    """Render upload dropzone."""
    st.markdown("""
    <div class="answer-card" style="text-align: center; padding: 2rem;">
        <div style="font-size: 2rem; margin-bottom: 1rem;">📄</div>
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
            Upload Medical Report
        </div>
        <div style="color: var(--text-secondary); margin-bottom: 1rem;">
            Supported: PDF, JPG, PNG, TXT
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png", "txt"],
        key=key,
        label_visibility="collapsed"
    )
    
    return uploaded_file


def render_prompt_suggestion_row(suggestions: List[str]):
    """Render prompt suggestion chips."""
    st.markdown('<div style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">Suggested Questions:</div>', unsafe_allow_html=True)
    
    cols = st.columns(len(suggestions))
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                return suggestion
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None


# ============================================================================
# CHART COMPONENTS
# ============================================================================

def render_trend_chart(data: List[Dict[str, Any]], x_field: str, y_field: str, title: str):
    """Render trend chart."""
    import pandas as pd
    
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(data)
    if x_field in df.columns and y_field in df.columns:
        df[x_field] = pd.to_datetime(df[x_field])
        chart_df = df[[x_field, y_field]].set_index(x_field)
        
        st.markdown(f"**{title}**")
        st.line_chart(chart_df, height=300)
    else:
        st.warning(f"Required fields not found: {x_field}, {y_field}")


def render_distribution_chart(data: Dict[str, int], title: str):
    """Render distribution bar chart."""
    import pandas as pd
    
    if not data:
        st.info(f"No data available for {title}")
        return
    
    df = pd.DataFrame(list(data.items()), columns=["Category", "Count"])
    
    st.markdown(f"**{title}**")
    st.bar_chart(df.set_index("Category"), height=300)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_timestamp(ts: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return ts


def calculate_confidence_class(confidence: float) -> str:
    """Calculate confidence class."""
    if confidence > 0.8:
        return "high"
    elif confidence > 0.6:
        return "medium"
    else:
        return "low"
