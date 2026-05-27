import streamlit as st
import requests
import yfinance as yf

# --- CONFIGURATION ---
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus Terminal", layout="wide", page_icon="📈")
st.title("Nexus Quantitative Terminal")

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- AUTHENTICATION ---
if not st.session_state.authenticated:
    st.sidebar.header("🔑 Authentication")
    user_passkey = st.sidebar.text_input("Enter Passkey", type="password")
    if st.sidebar.button("Unlock Dashboard"):
        db_query = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}&is_active=eq.true"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        try:
            response = requests.get(db_query, headers=headers)
            if response.status_code == 200 and len(response.json()) > 0:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid or inactive access key.")
        except Exception as e:
            st.error(f"Connection error: {e}")
    st.sidebar.markdown("---")
    st.sidebar.link_button("Purchase Premium Access", STRIPE_LINK)

# --- PROTECTED DASHBOARD ---
if st.session_state.authenticated:
    st.success("Access Granted. Nexus Core Online.")
    
    # Fetching Live Data
    ticker_data = yf.Ticker("AAPL").history(period="1mo")
    btc_data = yf.Ticker("BTC-USD").history(period="1mo")

    # Psychological Indicators
    col1, col2, col3 = st.columns(3)
    col1.metric("AAPL Current Price", f"${ticker_data['Close'].iloc[-1]:.2f}")
    col2.metric("BTC Market Price", f"${btc_data['Close'].iloc[-1]:,.0f}")
    col3.metric("System Status", "Live", "Stable")
    
    st.markdown("---")

    # Visual Data Layout
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("AAPL Price Momentum (1mo)")
        st.line_chart(ticker_data['Close'])
    with c2:
        st.subheader("BTC Price Momentum (1mo)")
        st.line_chart(btc_data['Close'])
        
    st.info("**Nexus Core Insight:** Real-time data feed synchronized. Analytics engine active.")
    
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
