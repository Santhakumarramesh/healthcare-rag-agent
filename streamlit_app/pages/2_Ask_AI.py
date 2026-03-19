"""
Ask AI - Structured medical Q&A with evidence-based responses.
"""
import streamlit as st
import requests
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.layout import load_css, page_header, render_sidebar_status
from components.badges import confidence_badge, status_badge

# Page config
st.set_page_config(
    page_title="Ask AI - Healthcare AI",
    layout="wide",
    page_icon="⚕️",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Sidebar
render_sidebar_status()

# Main content
page_header("Ask AI", "Get evidence-based answers to medical questions")

# Mode toggle
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    mode = st.radio("Mode", ["Patient", "Professional"], horizontal=True, label_visibility="collapsed")
with col2:
    st.markdown('<div style="padding: 8px 0; color: #486581; font-size: 13px;">Confidence legend: <span style="color: #2F855A;">High</span> | <span style="color: #B7791F;">Moderate</span> | <span style="color: #C53030;">Low</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Query input
query = st.text_area(
    "Ask your question",
    height=100,
    placeholder="Example: What are the symptoms of diabetes? Can I take ibuprofen with aspirin?",
    key="query_input",
    value=st.session_state.get("preset_query", "")
)

# Clear preset after use
if "preset_query" in st.session_state:
    del st.session_state["preset_query"]

# Suggested prompts
st.markdown('<div style="font-size: 13px; color: #486581; margin-bottom: 8px;">Suggested prompts:</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Explain lab results", key="prompt1", use_container_width=True):
        st.session_state["query_input"] = "Explain what elevated cholesterol means"
        st.rerun()

with col2:
    if st.button("Symptom patterns", key="prompt2", use_container_width=True):
        st.session_state["query_input"] = "What could cause fatigue and dizziness?"
        st.rerun()

with col3:
    if st.button("Drug interactions", key="prompt3", use_container_width=True):
        st.session_state["query_input"] = "Can I take aspirin with ibuprofen?"
        st.rerun()

with col4:
    if st.button("Follow-up questions", key="prompt4", use_container_width=True):
        st.session_state["query_input"] = "What follow-up tests should I consider?"
        st.rerun()

# Submit button
submit = st.button("Submit Question", type="primary", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Response section
if submit and query.strip():
    API_BASE = os.getenv("API_BASE_URL", "https://healthcare-rag-api.onrender.com")
    
    with st.spinner("Analyzing your question..."):
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={"query": query, "session_id": st.session_state.get("session_id", "default")},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Confidence badge
                confidence = result.get("confidence", 0.0)
                confidence_badge(confidence)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Answer card
                st.markdown(f'''
                <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 24px; margin-bottom: 16px;">
                    <div style="font-weight: 600; font-size: 16px; color: #102A43; margin-bottom: 12px;">Answer</div>
                    <div style="color: #486581; font-size: 14px; line-height: 1.7;">
                        {result.get("answer", "No answer available")}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Key insights
                if result.get("key_insights"):
                    st.markdown('''
                    <div style="background: #E6F7F8; border: 1px solid #2CB1BC; border-radius: 16px; padding: 24px; margin-bottom: 16px;">
                        <div style="font-weight: 600; font-size: 16px; color: #0F4C81; margin-bottom: 12px;">Key Insights</div>
                    ''', unsafe_allow_html=True)
                    
                    for insight in result.get("key_insights", []):
                        st.markdown(f'<div style="color: #0F4C81; font-size: 14px; margin-bottom: 8px;">• {insight}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Two column layout for concerns and next steps
                col1, col2 = st.columns(2)
                
                with col1:
                    # Possible concerns
                    concerns = result.get("possible_considerations", [])
                    if concerns:
                        st.markdown('''
                        <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                            <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 12px;">Possible Concerns</div>
                        ''', unsafe_allow_html=True)
                        
                        for concern in concerns:
                            st.markdown(f'<div style="color: #486581; font-size: 13px; margin-bottom: 6px;">• {concern}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Next steps
                    next_steps = result.get("next_steps", [])
                    if next_steps:
                        st.markdown('''
                        <div style="background: white; border: 1px solid #D9E2EC; border-radius: 16px; padding: 20px; margin-bottom: 16px;">
                            <div style="font-weight: 600; font-size: 15px; color: #102A43; margin-bottom: 12px;">Next Steps</div>
                        ''', unsafe_allow_html=True)
                        
                        for step in next_steps:
                            st.markdown(f'<div style="color: #486581; font-size: 13px; margin-bottom: 6px;">• {step}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Sources
                sources = result.get("sources", [])
                if sources:
                    st.markdown("### Sources")
                    for idx, source in enumerate(sources[:5], 1):
                        with st.expander(f"{idx}. {source.get('title', 'Source')} (Score: {source.get('score', 'N/A')})"):
                            st.markdown(f"**Category:** {source.get('category', 'N/A')}")
                            st.markdown(f"**Preview:** {source.get('preview', 'No preview available')}")
                
                # Safety note
                st.markdown(f'''
                <div style="background: #FFF4E5; border-left: 4px solid #B7791F; border-radius: 8px; padding: 16px 20px; margin-top: 24px;">
                    <div style="font-weight: 600; color: #B7791F; margin-bottom: 6px; font-size: 14px;">Safety Note</div>
                    <div style="color: #B7791F; font-size: 13px;">
                        {result.get("safety_note", "This assistant does not replace professional medical advice.")}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
            else:
                st.error(f"API error: {response.status_code}")
                
        except requests.Timeout:
            st.error("Request timed out. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif submit:
    st.warning("Please enter a question")
