"""
Card components for consistent UI.
"""
import streamlit as st


def metric_card(label: str, value: str, delta: str = "", delta_color: str = "normal"):
    """Render a metric card."""
    delta_colors = {
        "normal": "#486581",
        "success": "#2F855A",
        "warning": "#B7791F",
        "danger": "#C53030"
    }
    
    delta_html = ""
    if delta:
        color = delta_colors.get(delta_color, delta_colors["normal"])
        delta_html = f'<div style="color: {color}; font-size: 13px; font-weight: 500; margin-top: 4px;">{delta}</div>'
    
    st.markdown(f'''
    <div style="
        background: white;
        border: 1px solid #D9E2EC;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    ">
        <div style="font-size: 13px; color: #486581; font-weight: 500; margin-bottom: 8px;">{label}</div>
        <div style="font-size: 32px; font-weight: 700; color: #0F4C81;">{value}</div>
        {delta_html}
    </div>
    ''', unsafe_allow_html=True)


def quick_action_card(icon: str, title: str, description: str, action_key: str):
    """Render a quick action card."""
    st.markdown(f'''
    <div style="
        background: white;
        border: 1px solid #D9E2EC;
        border-radius: 16px;
        padding: 20px;
        cursor: pointer;
        transition: all 0.2s;
        height: 100%;
    " onmouseover="this.style.borderColor='#0F4C81'; this.style.boxShadow='0 4px 12px rgba(15, 76, 129, 0.1)';" 
       onmouseout="this.style.borderColor='#D9E2EC'; this.style.boxShadow='none';">
        <div style="font-size: 24px; margin-bottom: 12px;">{icon}</div>
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 6px;">{title}</div>
        <div style="font-size: 13px; color: #486581;">{description}</div>
    </div>
    ''', unsafe_allow_html=True)


def info_card(title: str, content: str, card_type: str = "info"):
    """Render an info/warning/success card."""
    colors = {
        "info": {"bg": "#E6F7F8", "border": "#2CB1BC", "text": "#0F4C81"},
        "success": {"bg": "#E6F4EA", "border": "#2F855A", "text": "#2F855A"},
        "warning": {"bg": "#FFF4E5", "border": "#B7791F", "text": "#B7791F"},
        "danger": {"bg": "#FDECEC", "border": "#C53030", "text": "#C53030"}
    }
    
    c = colors.get(card_type, colors["info"])
    
    st.markdown(f'''
    <div style="
        background: {c["bg"]};
        border-left: 4px solid {c["border"]};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
    ">
        <div style="font-weight: 600; color: {c["text"]}; margin-bottom: 6px; font-size: 14px;">{title}</div>
        <div style="color: {c["text"]}; font-size: 13px;">{content}</div>
    </div>
    ''', unsafe_allow_html=True)


def section_card(title: str, content_html: str):
    """Render a section card with custom content."""
    st.markdown(f'''
    <div class="card">
        <div class="card-title">{title}</div>
        <div style="color: #486581; font-size: 14px; line-height: 1.6;">
            {content_html}
        </div>
    </div>
    ''', unsafe_allow_html=True)
