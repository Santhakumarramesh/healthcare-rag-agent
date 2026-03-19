"""
Citation and source display components.
"""
import streamlit as st
from typing import List, Dict, Any


def render_source_card(source: Dict[str, Any], index: int) -> None:
    """
    Render a single source citation card.
    
    Args:
        source: Source dictionary with title, score, category, preview
        index: Source index number
    """
    title = source.get("title", "Source")
    score = source.get("score", 0.0)
    category = source.get("category", "N/A")
    preview = source.get("preview", "No preview available")
    
    # Score color coding
    if score >= 0.85:
        score_color = "#2F855A"
        score_bg = "#E6F4EA"
    elif score >= 0.65:
        score_color = "#B7791F"
        score_bg = "#FFF4E5"
    else:
        score_color = "#486581"
        score_bg = "#F7FAFC"
    
    with st.expander(f"{index}. {title} (Score: {score:.2f})"):
        st.markdown(f'''
        <div style="margin-bottom: 12px;">
            <span style="background: {score_bg}; color: {score_color}; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;">
                Relevance: {int(score * 100)}%
            </span>
            <span style="background: #F7FAFC; color: #486581; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; margin-left: 8px;">
                {category}
            </span>
        </div>
        <div style="color: #486581; font-size: 13px; line-height: 1.6;">
            {preview}
        </div>
        ''', unsafe_allow_html=True)


def render_sources_section(sources: List[Dict[str, Any]], max_display: int = 5) -> None:
    """
    Render all source citations in a structured format.
    
    Args:
        sources: List of source dictionaries
        max_display: Maximum number of sources to display
    """
    if not sources:
        st.markdown(
            '<div style="color: #486581; font-size: 13px; padding: 16px; text-align: center; '
            'background: #F7FAFC; border: 1px solid #D9E2EC; border-radius: 8px;">'
            'No source citations available</div>',
            unsafe_allow_html=True
        )
        return
    
    st.markdown("### Sources")
    st.markdown(
        f'<div style="color: #486581; font-size: 13px; margin-bottom: 12px;">'
        f'Showing {min(len(sources), max_display)} of {len(sources)} sources</div>',
        unsafe_allow_html=True
    )
    
    for idx, source in enumerate(sources[:max_display], 1):
        render_source_card(source, idx)


def render_grounded_sources(sources: List[Dict[str, Any]]) -> None:
    """
    Render grounded sources from structured reasoning agent.
    
    Args:
        sources: List of grounded source dictionaries
    """
    if not sources:
        return
    
    st.markdown(
        '<div style="font-size: 13px; color: #486581; margin-bottom: 8px;">'
        'Evidence-grounded sources:</div>',
        unsafe_allow_html=True
    )
    
    for idx, source in enumerate(sources, 1):
        source_name = source.get("source", "Unknown")
        score = source.get("score", 0.0)
        category = source.get("category", "unknown")
        preview = source.get("preview", "")
        
        st.markdown(f'''
        <div style="background: #E6F7F8; border-left: 3px solid #2CB1BC; padding: 12px 16px; margin-bottom: 8px; border-radius: 4px;">
            <div style="font-weight: 600; font-size: 13px; color: #0F4C81; margin-bottom: 4px;">
                {idx}. {source_name} <span style="color: #2CB1BC;">(Score: {score:.2f})</span>
            </div>
            <div style="font-size: 12px; color: #486581; margin-bottom: 4px;">
                Category: {category}
            </div>
            <div style="font-size: 12px; color: #486581; line-height: 1.5;">
                {preview}
            </div>
        </div>
        ''', unsafe_allow_html=True)
