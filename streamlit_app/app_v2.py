"""
AI Healthcare Copilot - User-Friendly Interface
Simple, clean, and easy to use
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple, clean CSS
st.markdown("""
<style>
/* Clean, readable design */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* Main container */
.main .block-container {
    padding: 2rem;
    max-width: 1200px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8f9fa;
    padding: 1rem;
}

/* Buttons */
.stButton > button {
    width: 100%;
    background: #0066cc;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #0052a3;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,102,204,0.3);
}

/* Cards */
.card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Headers */
h1 {
    color: #1a1a1a;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

h2 {
    color: #333;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}

h3 {
    color: #555;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

/* Text */
p {
    color: #666;
    line-height: 1.6;
    font-size: 16px;
}

/* Success/Error messages */
.stSuccess {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 8px;
}

.stError {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 8px;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 16px;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #0066cc;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.1);
}

/* File uploader */
[data-testid="stFileUploader"] {
    border: 2px dashed #0066cc;
    border-radius: 12px;
    padding: 2rem;
    background: #f8f9fa;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.75rem 1.5rem;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
}

/* Expander */
.streamlit-expanderHeader {
    background: #f8f9fa;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"user-{datetime.now().strftime('%Y%m%d%H%M%S')}"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Guest"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# 🏥 Healthcare AI")
    st.markdown("---")
    
    # User info
    if st.session_state.logged_in:
        st.success(f"👤 {st.session_state.user_name}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_token = None
            st.session_state.user_name = "Guest"
            st.rerun()
    else:
        st.info("👤 Guest Mode")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📍 Navigation")
    
    page = st.radio(
        "Go to:",
        ["🏠 Home", "💬 Chat", "📄 Upload Report", "📊 My History", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # System status
    st.markdown("### 🔧 System Status")
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        if health.get("status") == "healthy":
            st.success("✅ System Online")
        else:
            st.warning("⚠️ System Issues")
    except:
        st.error("❌ System Offline")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Home":
    st.markdown("# Welcome to Healthcare AI Assistant")
    st.markdown("Get instant, evidence-based answers to your health questions")
    
    st.markdown("---")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h3>💬 Ask Questions</h3>
            <p>Get instant answers to your health questions with sources</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Chat", key="home_chat"):
            st.session_state.page = "💬 Chat"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>📄 Upload Report</h3>
            <p>Analyze your lab reports and get explanations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Upload Now", key="home_upload"):
            st.session_state.page = "📄 Upload Report"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="card">
            <h3>📊 View History</h3>
            <p>See your past conversations and reports</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View History", key="home_history"):
            st.session_state.page = "📊 My History"
            st.rerun()
    
    st.markdown("---")
    
    # Features
    st.markdown("## ✨ What Can I Do?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 Medical Q&A
        - Ask any health question
        - Get evidence-based answers
        - See source citations
        - Understand medical terms
        
        ### 📋 Report Analysis
        - Upload lab reports (PDF/Image)
        - Get instant explanations
        - Understand abnormal values
        - Receive health recommendations
        """)
    
    with col2:
        st.markdown("""
        ### 🧠 Smart Features
        - Multi-step reasoning for complex questions
        - Emergency symptom detection
        - Drug interaction warnings
        - Personalized health advice
        
        ### 🔒 Safe & Secure
        - HIPAA-compliant audit logs
        - Encrypted data storage
        - Privacy-first design
        - No data sharing
        """)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "💬 Chat":
    st.markdown("# 💬 Chat with Healthcare AI")
    st.markdown("Ask me anything about health, symptoms, medications, or medical reports")
    
    st.markdown("---")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="card" style="background: #e3f2fd;">
                <strong>You:</strong><br>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="card">
                <strong>AI Assistant:</strong><br>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(msg["sources"][:3], 1):
                        st.markdown(f"**{i}. {source.get('title', 'Source')}**")
                        st.caption(source.get('excerpt', '')[:200] + "...")
    
    # Chat input
    st.markdown("---")
    
    user_query = st.text_area(
        "Your Question:",
        placeholder="Example: What are the symptoms of diabetes?",
        height=100,
        key="chat_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Send Question", use_container_width=True):
            if user_query:
                # Add user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_query
                })
                
                # Call API
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/chat",
                            json={
                                "query": user_query,
                                "session_id": st.session_state.session_id
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Add AI response
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": data.get("response", ""),
                                "sources": data.get("sources", [])
                            })
                            
                            st.rerun()
                        else:
                            st.error("Sorry, I encountered an error. Please try again.")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a question")
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: UPLOAD REPORT
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📄 Upload Report":
    st.markdown("# 📄 Upload Medical Report")
    st.markdown("Upload your lab report or medical document for instant analysis")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Upload PDF, JPG, or PNG files (max 10MB)"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Analyze Report", use_container_width=True):
            with st.spinner("Analyzing your report..."):
                try:
                    # Upload file
                    files = {"file": uploaded_file}
                    data = {"session_id": st.session_state.session_id}
                    
                    upload_response = requests.post(
                        f"{API_BASE}/records/upload",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if upload_response.status_code == 200:
                        st.success("✅ File uploaded successfully!")
                        
                        # Analyze (increase timeout for complex reports)
                        analyze_response = requests.post(
                            f"{API_BASE}/records/analyze",
                            data={"session_id": st.session_state.session_id},
                            timeout=120  # 2 minutes for complex analysis
                        )
                        
                        if analyze_response.status_code == 200:
                            result = analyze_response.json()
                            
                            st.markdown("## 📊 Analysis Results")
                            
                            # Patient Info
                            patient_info = result.get("patient_info", {})
                            if patient_info:
                                st.markdown("### 👤 Patient Information")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Name", patient_info.get("name", "N/A"))
                                with col2:
                                    st.metric("Age", patient_info.get("age", "N/A"))
                                with col3:
                                    st.metric("Gender", patient_info.get("gender", "N/A"))
                            
                            # Lab Values
                            lab_values = result.get("lab_values", [])
                            if lab_values:
                                st.markdown("### 🧪 Lab Results")
                                for lab in lab_values:
                                    status = lab.get("status", "UNKNOWN")
                                    if status == "NORMAL":
                                        st.success(f"✅ **{lab.get('name')}**: {lab.get('value')} (Normal)")
                                    elif status in ["HIGH", "LOW"]:
                                        st.warning(f"⚠️ **{lab.get('name')}**: {lab.get('value')} ({status})")
                                    elif status == "CRITICAL":
                                        st.error(f"🚨 **{lab.get('name')}**: {lab.get('value')} (CRITICAL)")
                            
                            # Recommendations
                            recommendations = result.get("health_recommendations")
                            if recommendations:
                                with st.expander("💡 Health Recommendations"):
                                    st.markdown(recommendations)
                        else:
                            st.error("Failed to analyze report")
                    else:
                        st.error("Failed to upload file")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊 My History":
    st.markdown("# 📊 My History")
    st.markdown("View your past conversations and reports")
    
    st.markdown("---")
    
    try:
        history_response = requests.get(
            f"{API_BASE}/history/{st.session_state.session_id}",
            timeout=5
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Queries", history_data.get("total_interactions", 0))
            with col2:
                st.metric("Avg Confidence", f"{history_data.get('avg_confidence', 0)*100:.0f}%")
            with col3:
                st.metric("Status", "Active" if history_data.get("active", False) else "Inactive")
            
            st.markdown("---")
            
            # Recent conversations
            conversations = history_data.get("conversations", [])
            if conversations:
                st.markdown("### 💬 Recent Conversations")
                for conv in conversations[:10]:
                    with st.expander(f"🔹 {conv.get('query', '')[:80]}..."):
                        st.markdown(f"**Query:** {conv.get('query', '')}")
                        st.markdown(f"**Answer:** {conv.get('answer', '')[:300]}...")
                        st.caption(f"Type: {conv.get('query_type', '')} | Confidence: {conv.get('confidence', 0)*100:.0f}%")
            else:
                st.info("No conversation history yet. Start chatting to see your history here!")
        else:
            st.warning("Could not load history")
    except:
        st.error("Failed to connect to server")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "⚙️ Settings":
    st.markdown("# ⚙️ Settings")
    
    st.markdown("---")
    
    # Login section
    if not st.session_state.logged_in:
        st.markdown("## 🔐 Login")
        
        email = st.text_input("Email", placeholder="admin@healthcare.ai")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 Login", use_container_width=True):
                if email and password:
                    try:
                        response = requests.post(
                            f"{API_BASE}/auth/login",
                            json={"email": email, "password": password},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.user_token = data.get("token")
                            st.session_state.user_name = data.get("name")
                            st.success(f"Welcome, {data.get('name')}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    except:
                        st.error("Connection error")
                else:
                    st.warning("Please enter email and password")
        
        with col2:
            st.info("""
            **Demo Accounts:**
            - admin@healthcare.ai / admin123
            - doctor@healthcare.ai / doctor123
            - patient@healthcare.ai / patient123
            """)
    
    else:
        st.success(f"✅ Logged in as {st.session_state.user_name}")
        
        st.markdown("---")
        
        # User preferences
        st.markdown("## 👤 User Preferences")
        
        st.checkbox("Enable notifications", value=True)
        st.checkbox("Save conversation history", value=True)
        st.checkbox("Show confidence scores", value=True)
        
        st.markdown("---")
        
        # Session info
        st.markdown("## 📋 Session Information")
        st.code(f"Session ID: {st.session_state.session_id}")
        st.caption(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Footer
st.markdown("---")
st.caption("⚕️ Healthcare AI Assistant | Powered by Advanced AI | Not a substitute for professional medical advice")
