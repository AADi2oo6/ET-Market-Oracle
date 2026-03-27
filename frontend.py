import streamlit as st
import logging
import requests
from streamlit_cookies_controller import CookieController

from app.core.database import SessionLocal
from app.agents.orchestrator import create_market_agent

# Configure logging to console
logging.basicConfig(level=logging.INFO)

API_URL = "http://localhost:8000/api"

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
# 2.5 Cookies Initialization
# ==========================================
controller = CookieController()

# ==========================================
# 3. Session State
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

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
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# Cookie Hydration
cookie_token = controller.get("auth_token")
if cookie_token and st.session_state.auth_status != "logged_in":
    st.session_state.auth_status = "logged_in"
    st.session_state.token = cookie_token

# Portfolio Auto-Fetch
if st.session_state.auth_status == "logged_in" and not st.session_state.portfolio:
    try:
        res = requests.get(f"{API_URL}/portfolio/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if res.status_code == 200:
            st.session_state.portfolio = res.json().get("holdings", [])
    except Exception:
        pass

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
                    response = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get("access_token")
                        st.session_state.auth_status = "logged_in"
                        st.session_state.token = token
                        st.session_state.user_name = data.get("name")
                        controller.set("auth_token", token, max_age=86400)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
                    
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
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
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
            
    st.stop()

# ==========================================
# 5. Sidebar: My Portfolio
# ==========================================
with st.sidebar:
    st.title("💼 My Portfolio")
    
    if st.session_state.user_name:
        st.markdown(f"**Welcome, {st.session_state.user_name}**")
        
    # Calculate Dynamic Net Worth
    net_worth = sum(item.get("current_value", 0) for item in st.session_state.portfolio)
    
    st.metric(label="Net Worth", value=f"₹{net_worth:,.2f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Schemes", value=len(st.session_state.portfolio))
    with col2:
        st.metric(label="Day Volatility", value="High")

    st.divider()
    
    st.markdown("**1-Click Portfolio Sync**")
    
    with st.popover("ℹ️ How to get your CAS file"):
        st.markdown("""
**Step-by-Step Guide:**
1. Go to [camsonline.com](https://www.camsonline.com/).
2. Click on **Statements > CAS - CAMS+KFintech**.
3. Select **Detailed Statement**.
4. Enter your registered Email and PAN Card number.
5. You will receive a PDF in your email within 2 minutes.
6. Upload that PDF here and use your **PAN Card (in ALL CAPS)** as the password!
""")
        
    uploaded_file = st.file_uploader("Upload CAS (CAMS/KFintech) PDF", type=["pdf"])
    cas_password = st.text_input("PDF Password (usually PAN)", type="password")
    
    if st.button("Upload & Analyze"):
        if not uploaded_file or not cas_password:
            st.error("Please provide both the PDF file and password.")
        else:
            with st.spinner("Analyzing CAS Statement..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"password": cas_password}
                    
                    headers = {}
                    if st.session_state.auth_status == "logged_in" and st.session_state.token:
                        headers["Authorization"] = f"Bearer {st.session_state.token}"
                        
                    res = requests.post(f"{API_URL}/portfolio/upload", files=files, data=data, headers=headers)
                    if res.status_code == 200:
                        parsed_holdings = res.json().get("holdings", [])
                        st.session_state.portfolio = parsed_holdings
                        st.success("Portfolio beautifully synced!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Unknown error occurred"))
                except Exception as e:
                    st.error(f"Error uploading file: {e}")

    st.divider()
    
    if len(st.session_state.portfolio) > 0:
        st.markdown("**Current Holdings:**")
        # Display up to top 5 holdings
        for holding in st.session_state.portfolio[:5]:
            scheme = holding.get("scheme_name", "Unknown")
            val = holding.get("current_value", 0)
            st.markdown(f"- **{scheme[:25]}...**\n  - ₹{val:,.2f}")
        
    st.divider()
    st.info("The **ET Market Oracle** is an elite AI agent backed by LangGraph. It dynamically searches Pinecone for market news or queries PostgreSQL for stock prices.")

    if st.session_state.auth_status == "guest":
        st.warning("Guest Mode Active: Portfolio data is stored temporarily. Login to save portfolios.")
        
    st.divider()
    if st.button("Logout"):
        controller.remove("auth_token")
        st.session_state.auth_status = None
        st.session_state.token = None
        st.session_state.user_name = None
        st.session_state.messages = []
        st.session_state.portfolio = []
        st.rerun()

# ==========================================
# 6. Main Interface
# ==========================================
st.title("🤖 ET Market Oracle")
st.markdown("Your elite, tool-calling financial advisor.")

# Render previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 7. Chat Logic
# ==========================================
if prompt := st.chat_input("Ask about your portfolio or market news..."):
    # Append the user's prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Analyzing markets & executing tools..."):
            try:
                # Call the LangGraph agent
                response = st.session_state.agent.invoke({"messages": [("user", prompt)]})
                
                bot_reply = "The agent did not return a valid message array."
                if "messages" in response and len(response["messages"]) > 0:
                    bot_reply = response["messages"][-1].content
                    
                st.markdown(bot_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except Exception as e:
                error_msg = f"**An error occurred explicitly during agent execution:**\n```\n{str(e)}\n```"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
