"""
Badge components for status indicators.
"""
import streamlit as st


def confidence_badge(confidence: float) -> None:
    """Render confidence badge with color coding."""
    if confidence >= 0.85:
        bg = "#E6F4EA"
        fg = "#2F855A"
        label = "High Confidence"
    elif confidence >= 0.65:
        bg = "#FFF4E5"
        fg = "#B7791F"
        label = "Moderate Confidence"
    else:
        bg = "#FDECEC"
        fg = "#C53030"
        label = "Low Confidence"

    st.markdown(f'''
    <div style="
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: {bg};
        color: {fg};
        font-weight: 600;
        font-size: 13px;
        margin: 8px 0;
    ">
        {label}: {int(confidence * 100)}%
    </div>
    ''', unsafe_allow_html=True)


def status_badge(label: str, status: str = "success") -> None:
    """Render status badge."""
    colors = {
        "success": {"bg": "#E6F4EA", "fg": "#2F855A"},
        "warning": {"bg": "#FFF4E5", "fg": "#B7791F"},
        "danger": {"bg": "#FDECEC", "fg": "#C53030"},
        "info": {"bg": "#E6F7F8", "fg": "#0F4C81"}
    }
    
    c = colors.get(status, colors["info"])
    
    st.markdown(f'''
    <div style="
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        background: {c["bg"]};
        color: {c["fg"]};
        font-weight: 600;
        font-size: 12px;
    ">
        {label}
    </div>
    ''', unsafe_allow_html=True)


def flag_badge(flag: str) -> str:
    """Return HTML for abnormal flag badge."""
    if not flag or flag.lower() == "normal":
        return '<span style="color: #2F855A; font-weight: 600;">Normal</span>'
    elif flag.lower() == "high":
        return '<span style="background: #FDECEC; color: #C53030; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 12px;">HIGH</span>'
    elif flag.lower() == "low":
        return '<span style="background: #FFF4E5; color: #B7791F; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 12px;">LOW</span>'
    else:
        return f'<span style="color: #486581; font-weight: 500;">{flag}</span>'
