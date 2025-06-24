import streamlit as st
import uuid

def set_page_config():
    st.set_page_config(
        page_title="Sales Agent Chat",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def set_page_style():
    with open("assets/style.css") as f:
        style = f.read()
    st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "pending_approval" not in st.session_state:
        st.session_state.pending_approval = None
    if "config" not in st.session_state:
        st.session_state.config = {
            "configurable": {
                "customer_id": "123456789",
                "thread_id": st.session_state.thread_id,
            }
        }

def setup_sidebar():
    st.sidebar.markdown(
        """
        <div class="agent-profile">
            <div class="profile-header">
                <div class="avatar">🤖</div>
                <h1>Sales Agent</h1>
            </div>
            <div class="feature-list">
                <div class="feature-item">
                    <span class="icon">🛒</span>
                    <span>Browse available products</span>
                </div>
                <div class="feature-item">
                    <span class="icon">📦</span>
                    <span>Place orders</span>
                </div>
                <div class="feature-item">
                    <span class="icon">🚚</span>
                    <span>Track your orders</span>
                </div>
            </div>
            <div class="status-card">
                <div class="status-indicator"></div>
                <span>Ready to Assist</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Start New Chat"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()