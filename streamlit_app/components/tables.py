"""
Table components for structured data display.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any


def render_extracted_values_table(values: List[Dict[str, Any]]) -> None:
    """
    Render extracted lab values with abnormal highlighting.
    
    Args:
        values: List of extracted lab values with name, value, unit, reference, flag
    """
    if not values:
        st.markdown(
            '<div style="color: #486581; font-size: 14px; padding: 20px; text-align: center; '
            'background: white; border: 1px solid #D9E2EC; border-radius: 12px;">'
            'No structured lab values detected</div>',
            unsafe_allow_html=True
        )
        return
    
    # Build custom HTML table
    table_html = '''
    <table style="width: 100%; border-collapse: collapse; font-size: 14px; background: white; border-radius: 12px; overflow: hidden; border: 1px solid #D9E2EC;">
        <thead>
            <tr style="background: #F7FAFC; border-bottom: 2px solid #D9E2EC;">
                <th style="padding: 12px; text-align: left; font-weight: 600; color: #486581; font-size: 12px; text-transform: uppercase;">Test Name</th>
                <th style="padding: 12px; text-align: left; font-weight: 600; color: #486581; font-size: 12px; text-transform: uppercase;">Value</th>
                <th style="padding: 12px; text-align: left; font-weight: 600; color: #486581; font-size: 12px; text-transform: uppercase;">Unit</th>
                <th style="padding: 12px; text-align: left; font-weight: 600; color: #486581; font-size: 12px; text-transform: uppercase;">Reference</th>
                <th style="padding: 12px; text-align: left; font-weight: 600; color: #486581; font-size: 12px; text-transform: uppercase;">Status</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for val in values:
        flag = (val.get("flag") or "").lower()
        is_abnormal = flag in {"high", "low", "abnormal", "critical"}
        
        row_bg = "#FDECEC" if is_abnormal else "white"
        flag_color = "#C53030" if is_abnormal else "#2F855A"
        flag_text = val.get("flag", "Normal") or "Normal"
        
        table_html += f'''
        <tr style="border-bottom: 1px solid #D9E2EC; background: {row_bg};">
            <td style="padding: 12px; color: #102A43; font-weight: 500;">{val.get("name", "N/A")}</td>
            <td style="padding: 12px; color: #102A43; font-weight: 600;">{val.get("value", "N/A")}</td>
            <td style="padding: 12px; color: #486581;">{val.get("unit", "")}</td>
            <td style="padding: 12px; color: #486581; font-size: 13px;">{val.get("reference", "N/A")}</td>
            <td style="padding: 12px;">
                <span style="background: {"#FDECEC" if is_abnormal else "#E6F4EA"}; 
                             color: {flag_color}; 
                             padding: 4px 10px; 
                             border-radius: 999px; 
                             font-size: 12px; 
                             font-weight: 600;">
                    {flag_text}
                </span>
            </td>
        </tr>
        '''
    
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)


def render_data_table(data: pd.DataFrame, title: str = None) -> None:
    """
    Render a generic data table with professional styling.
    
    Args:
        data: Pandas DataFrame
        title: Optional table title
    """
    if title:
        st.markdown(f"### {title}")
    
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


def render_timeline_table(records: List[Dict[str, Any]]) -> None:
    """
    Render a timeline-style table for records history.
    
    Args:
        records: List of record dictionaries
    """
    if not records:
        st.markdown(
            '<div style="color: #486581; font-size: 14px; padding: 40px; text-align: center; '
            'background: white; border: 1px solid #D9E2EC; border-radius: 12px;">'
            'No records found</div>',
            unsafe_allow_html=True
        )
        return
    
    for record in records:
        date = record.get("date", "N/A")
        title = record.get("title", "Untitled")
        summary = record.get("summary", "")
        confidence = record.get("confidence", 0.0)
        
        confidence_color = "#2F855A" if confidence >= 0.85 else "#B7791F" if confidence >= 0.65 else "#C53030"
        
        st.markdown(f'''
        <div style="background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: 20px; margin-bottom: 12px; cursor: pointer;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                <div>
                    <div style="font-weight: 600; font-size: 15px; color: #102A43;">{title}</div>
                    <div style="font-size: 12px; color: #486581; margin-top: 4px;">{date}</div>
                </div>
                <div style="background: {confidence_color}20; color: {confidence_color}; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;">
                    {int(confidence * 100)}%
                </div>
            </div>
            <div style="color: #486581; font-size: 13px; line-height: 1.5;">
                {summary[:150]}{"..." if len(summary) > 150 else ""}
            </div>
        </div>
        ''', unsafe_allow_html=True)
