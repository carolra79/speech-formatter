import streamlit as st
import hashlib

def check_auth():
    """Simple authentication for local testing"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Authentication Required")
        
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        
        if st.button("Login"):
            # Simple hardcoded auth for local testing
            if username == "admin" and password == "password":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.stop()
    
    return True
