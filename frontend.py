import streamlit as st
import logging
import requests

from app.core.database import SessionLocal
from app.agents.orchestrator import create_market_agent

# Configure logging to console (for terminal debugging)
logging.basicConfig(level=logging.INFO)

API_URL = "http://localhost:8000/api/auth"

# ==========================================
# 2. Page Config
# ==========================================
st.set_page_config(
    page_title="ET Market Oracle",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# ==========================================
# 3. Session State
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the Tool-Calling Agent exactly once per session
if "agent" not in st.session_state:
    try:
        st.session_state.agent = create_market_agent()
    except Exception as e:
        st.error(f"Failed to initialize ET Market Oracle Agent: {e}")
        st.stop()

if "auth_status" not in st.session_state:
    st.session_state.auth_status = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "token" not in st.session_state:
    st.session_state.token = None

# ==========================================
# 4. Auth Gate
# ==========================================
if st.session_state.auth_status is None:
    st.title("Welcome to ET Market Oracle")
    st.markdown("Please authenticate to access the portfolio and agent, or continue as a guest.")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Guest Mode"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                try:
                    response = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.auth_status = "logged_in"
                        st.session_state.token = data.get("access_token")
                        st.session_state.user_name = data.get("name")
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error connecting to backend. Is FastAPI running on port 8000? {e}")
                    
    with tab2:
        st.subheader("Register a new account")
        with st.form("register_form"):
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email")
            reg_phone = st.text_input("Phone (Optional)")
            reg_password = st.text_input("Password", type="password")
            reg_submit = st.form_submit_button("Register")
            if reg_submit:
                payload = {
                    "name": reg_name,
                    "email": reg_email,
                    "phone": reg_phone if reg_phone else None,
                    "password": reg_password
                }
                try:
                    res = requests.post(f"{API_URL}/register", json=payload)
                    if res.status_code == 201:
                        st.success("Registration successful! You can now log in via the Login tab.")
                    else:
                        st.error(f"Registration failed: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
                    
    with tab3:
        st.subheader("Guest Mode")
        st.info("Experience the ET Market Oracle without saving portfolio data.")
        if st.button("Continue as Guest"):
            st.session_state.auth_status = "guest"
            st.session_state.user_name = "Guest"
            st.rerun()
            
    st.stop() # Prevents rendering the rest of the app if not authenticated

# ==========================================
# 5. Sidebar: My Portfolio
# ==========================================
with st.sidebar:
    st.title("💼 My Portfolio")
    
    if st.session_state.user_name:
        st.markdown(f"**Welcome, {st.session_state.user_name}**")
        
    # Financial metrics using st.metric
    st.metric(label="Net Worth", value="₹12,45,000", delta="+1.2%")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Available Cash", value="₹45,000")
    with col2:
        st.metric(label="Day Volatility", value="High")

    st.divider()
    
    st.markdown("""
    **Current Holdings:**
    - RELIANCE.NS (100 shares)
    - TCS.NS (50 shares)
    - HDFCBANK.NS (200 shares)
    """)
    
    st.divider()
    st.info("The **ET Market Oracle** is an elite AI agent backed by LangGraph. It dynamically searches Pinecone for market news or queries PostgreSQL for stock prices to deliver accurate insights.")

    if st.session_state.auth_status == "guest":
        st.warning("Guest Mode Active: Portfolio data is stored temporarily. Login to save portfolios.")
        
    st.divider()
    if st.button("Logout"):
        st.session_state.auth_status = None
        st.session_state.token = None
        st.session_state.user_name = None
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 6. Main Interface
# ==========================================
st.title("🤖 ET Market Oracle")
st.markdown("Your elite, tool-calling financial advisor.")

# Render previous chat messages from Session State
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 7. Chat Logic
# ==========================================
if prompt := st.chat_input("Ask about your portfolio or market news..."):
    # Append the user's prompt to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user's message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Set up AI response container
    with st.chat_message("assistant"):
        with st.spinner("Analyzing markets & executing tools..."):
            try:
                # Call the LangGraph agent
                response = st.session_state.agent.invoke({"messages": [("user", prompt)]})
                
                # Extract text using response["messages"][-1].content
                bot_reply = "The agent did not return a valid message array."
                if "messages" in response and len(response["messages"]) > 0:
                    bot_reply = response["messages"][-1].content
                    
                st.markdown(bot_reply)
                
                # Append the AI's reply to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                error_msg = f"**An error occurred explicitly during agent execution:**\n```\n{str(e)}\n```"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
