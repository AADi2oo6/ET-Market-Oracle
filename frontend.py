import streamlit as st
import logging
import requests
import re
import yfinance as yf
import pandas as pd
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
if "tracked_stocks" not in st.session_state:
    st.session_state.tracked_stocks = []

# Cookie Hydration
cookie_token = controller.get("auth_token")
if cookie_token and st.session_state.auth_status != "logged_in":
    st.session_state.auth_status = "logged_in"
    st.session_state.token = cookie_token

# Portfolio Auto-Fetch
if st.session_state.auth_status == "logged_in":
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    if not st.session_state.portfolio:
        try:
            res = requests.get(f"{API_URL}/portfolio/me", headers=headers)
            if res.status_code == 200:
                st.session_state.portfolio = res.json().get("holdings", [])
        except Exception:
            pass
            
    if not st.session_state.tracked_stocks:
        try:
            w_res = requests.get(f"{API_URL}/watchlist/me", headers=headers)
            if w_res.status_code == 200:
                st.session_state.tracked_stocks = w_res.json().get("tracked_stocks", [])
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
    
    st.subheader("📈 Direct Equity Watchlist")
    available_stocks = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Infosys": "INFY.NS",
        "ITC": "ITC.NS",
        "State Bank of India": "SBIN.NS",
        "Bharti Airtel": "BHARTIARTL.NS"
    }
    reverse_map = {v: k for k, v in available_stocks.items()}
    current_names = [reverse_map[t] for t in st.session_state.tracked_stocks if t in reverse_map]
    
    selected_names = st.multiselect(
        "Select stocks to track & auto-sync:", 
        options=list(available_stocks.keys()), 
        default=current_names
    )
    
    if st.button("🔄 Sync Live Market Data"):
        if st.session_state.auth_status != "logged_in":
            st.error("Please login to save your watchlist.")
        else:
            selected_tickers = [available_stocks[name] for name in selected_names]
            with st.spinner("Fetching live prices for watchlist..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    res = requests.post(f"{API_URL}/watchlist/sync", json={"tickers": selected_tickers}, headers=headers)
                    if res.status_code == 200:
                        st.session_state.tracked_stocks = selected_tickers
                        st.success("Watchlist synced successfully!")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Error syncing watchlist"))
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")

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

if "tracked_stocks" in st.session_state and st.session_state.tracked_stocks and st.session_state.auth_status in ["logged_in", "guest"]:
    with st.expander("📊 Live Watchlist Charts & Comparison", expanded=False):
        
        # 0. Add timeframe selector
        timeframe = st.radio("Select Timeframe:", ["1mo", "6mo", "1y", "5y", "max"], horizontal=True)
        
        # 1. Add a multiselect specifically for filtering the chart
        stocks_to_plot = st.multiselect(
            "Select stocks to compare on the chart:",
            options=st.session_state.tracked_stocks,
            default=st.session_state.tracked_stocks
        )
        
        if stocks_to_plot:
            try:
                with st.spinner("Fetching comparison data..."):
                    # 2. Create an empty DataFrame to hold all stock prices
                    chart_data = pd.DataFrame()
                    
                    # 3. Fetch data for each selected stock and add it as a column
                    for ticker in stocks_to_plot:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period=timeframe)
                        if not hist.empty:
                            # Add the 'Close' price as a new column named after the ticker
                            chart_data[ticker] = hist['Close']
                    
                    # 4. Draw a single unified chart (Streamlit automatically color-codes multiple columns!)
                    if not chart_data.empty:
                        if isinstance(chart_data.index, pd.DatetimeIndex):
                            chart_data.index = chart_data.index.tz_localize(None)
                        st.line_chart(chart_data, height=400)
                    else:
                        st.caption("No historical data found for selected stocks.")
                        
            except Exception as e:
                st.error(f"Error generating comparison chart: {str(e)}")
        else:
            st.info("Please select at least one stock to view the chart.")

# Render previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "chart":
            st.caption("📈 Context chart:")
            # Re-fetch and draw (or use cached data if available)
            c_data = pd.DataFrame()
            for t in msg["tickers"]:
                try:
                    h = yf.Ticker(t).history(period="3mo")
                    if not h.empty:
                        c_data[t] = h['Close']
                except Exception:
                    pass
            if not c_data.empty and isinstance(c_data.index, pd.DatetimeIndex):
                c_data.index = c_data.index.tz_localize(None)
            st.line_chart(c_data, height=250)
        else:
            st.markdown(msg["content"])

# ==========================================
# 7. Chat Logic
# ==========================================
if prompt := st.chat_input("Ask about your portfolio or market news..."):
    # 1. Prepare the hidden context
    portfolio_context = ""
    if "portfolio" in st.session_state and st.session_state.portfolio:
        # Format the portfolio nicely for the LLM
        holdings_str = "\n".join([f"- {item['scheme_name']}: ₹{item['current_value']}" for item in st.session_state.portfolio])
        portfolio_context += f"\n\n[SYSTEM NOTE: The user's current portfolio holdings are:\n{holdings_str}\nBase your personalized advice, warnings, and news searches on these specific holdings.]"
        
        total_value = sum(item.get('current_value', 0) for item in st.session_state.portfolio) if "portfolio" in st.session_state else 0
        portfolio_context += f"\n\n[SYSTEM NOTE: The user's total calculated portfolio net worth is exactly {total_value}. Pass this exact number into the simulate_trade tool if requested.]"
        
    if "tracked_stocks" in st.session_state and st.session_state.tracked_stocks:
        portfolio_context += f"\n\n[SYSTEM NOTE: The user is actively tracking these direct stocks: {', '.join(st.session_state.tracked_stocks)}. Prioritize news and price checks for these companies.]"
    
    # 2. Combine the user's prompt with the hidden context
    full_prompt_for_llm = prompt + portfolio_context
    
    # 3. Display ONLY the user's original prompt in the UI
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 4. Add the original prompt to the visual chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Send the HIDDEN full prompt to the agent
    with st.spinner("Analyzing markets and your portfolio..."):
        try:
            # 1. Build the conversation history from session state (excluding the duplicate just-added prompt)
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                # Map Streamlit roles to LangGraph expected tuples
                role = "assistant" if msg["role"] == "assistant" else "user"
                chat_history.append((role, msg["content"]))
            
            # 2. Append the current prompt (which includes the hidden portfolio context)
            chat_history.append(("user", full_prompt_for_llm))
            
            # 3. Send the entire history to the agent
            response = st.session_state.agent.invoke({"messages": chat_history})
            
            raw_bot_reply = "The agent did not return a valid message array."
            if "messages" in response and len(response["messages"]) > 0:
                raw_bot_reply = response["messages"][-1].content
                
            # Extract the hidden tickers
            chart_tickers = re.findall(r'\[CHART_TICKER:(.*?)\]', raw_bot_reply)

            # Clean the reply so the user doesn't see the tags
            clean_reply = re.sub(r'\[CHART_TICKER:.*?\]', '', raw_bot_reply).strip()

            with st.chat_message("assistant"):
                st.markdown(clean_reply)

                # If we found a trigger, draw the chart!
                if chart_tickers:
                    st.caption("📈 Context chart:")
                    inline_chart_data = pd.DataFrame()
                    for t in chart_tickers:
                        # Clean the string
                        t = t.strip().upper()
                        # Hackathon Failsafe: Auto-append .NS for common Indian stocks if the AI forgets
                        indian_bluechips = ["TCS", "ZOMATO", "RELIANCE", "ITC", "INFY", "SBIN", "HDFCBANK", "TATAMOTORS"]
                        if t in indian_bluechips:
                            t += ".NS"
                            
                        try:
                            hist = yf.Ticker(t).history(period="3mo")
                            if not hist.empty:
                                inline_chart_data[t] = hist['Close']
                        except:
                            pass

                    if not inline_chart_data.empty:
                        if isinstance(inline_chart_data.index, pd.DatetimeIndex):
                            inline_chart_data.index = inline_chart_data.index.tz_localize(None)
                        st.line_chart(inline_chart_data, height=250)

            # Save to visual history with the extracted tickers
            st.session_state.messages.append({
                "role": "assistant", 
                "content": clean_reply, 
                "type": "chart" if chart_tickers else "text", 
                "tickers": chart_tickers
            })
            
        except Exception as e:
            error_msg = f"**An error occurred explicitly during agent execution:**\n```\n{str(e)}\n```"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
