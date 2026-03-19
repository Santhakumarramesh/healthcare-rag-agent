"""
File upload components for medical reports.
"""
import streamlit as st
from typing import Optional, Tuple


def render_upload_panel(
    label: str = "Upload Medical Report",
    accepted_types: list = None,
    help_text: str = None
) -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
    """
    Render a professional file upload panel.
    
    Args:
        label: Upload label text
        accepted_types: List of accepted file extensions
        help_text: Optional help text
        
    Returns:
        Uploaded file object or None
    """
    if accepted_types is None:
        accepted_types = ["pdf", "png", "jpg", "jpeg", "txt"]
    
    if help_text is None:
        help_text = f"Supported formats: {', '.join(accepted_types).upper()}"
    
    st.markdown(f'''
    <div style="background: #F7FAFC; border: 2px dashed #D9E2EC; border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 16px;">
        <div style="font-size: 16px; font-weight: 600; color: #102A43; margin-bottom: 8px;">
            {label}
        </div>
        <div style="font-size: 13px; color: #486581;">
            {help_text}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose file",
        type=accepted_types,
        label_visibility="collapsed"
    )
    
    return uploaded_file


def render_input_mode_toggle() -> str:
    """
    Render input mode toggle (File Upload vs Paste Text).
    
    Returns:
        Selected mode as string
    """
    mode = st.radio(
        "Input Method",
        ["File Upload", "Paste Text"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    return mode


def render_file_metadata(file_obj) -> None:
    """
    Render metadata for uploaded file.
    
    Args:
        file_obj: Streamlit UploadedFile object
    """
    if file_obj is None:
        return
    
    file_size_kb = len(file_obj.getvalue()) / 1024
    
    st.markdown(f'''
    <div style="background: white; border: 1px solid #D9E2EC; border-radius: 8px; padding: 16px; margin-top: 16px;">
        <div style="font-size: 13px; color: #486581; margin-bottom: 8px;">File Details:</div>
        <div style="font-size: 13px; color: #102A43; margin-bottom: 4px;">
            <span style="font-weight: 600;">Name:</span> {file_obj.name}
        </div>
        <div style="font-size: 13px; color: #102A43; margin-bottom: 4px;">
            <span style="font-weight: 600;">Type:</span> {file_obj.type}
        </div>
        <div style="font-size: 13px; color: #102A43;">
            <span style="font-weight: 600;">Size:</span> {file_size_kb:.1f} KB
        </div>
    </div>
    ''', unsafe_allow_html=True)


def render_text_input_area(
    placeholder: str = "Paste your medical report text here...",
    height: int = 300
) -> str:
    """
    Render a text area for pasting report content.
    
    Args:
        placeholder: Placeholder text
        height: Text area height in pixels
        
    Returns:
        Entered text
    """
    text = st.text_area(
        "Report Text",
        height=height,
        placeholder=placeholder,
        label_visibility="collapsed"
    )
    
    if text:
        word_count = len(text.split())
        char_count = len(text)
        
        st.markdown(f'''
        <div style="font-size: 12px; color: #486581; margin-top: 8px;">
            {word_count} words • {char_count} characters
        </div>
        ''', unsafe_allow_html=True)
    
    return text
