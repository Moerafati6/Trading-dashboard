import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- CONFIGURATION ---
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk" # KEEP THIS SECURE
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# --- SESSION & AUTH ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

def get_auth(key):
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    return requests.get(url, headers=headers).status_code == 200

# --- UI: MARKET PSYCHOLOGY (THE HOOK) ---
st.title("Nexus Quantitative Terminal")
st.sidebar.title("Nexus Control Panel")

# GLOBAL SENTIMENT (PUBLIC)
col_psych1, col_psych2 = st.columns([1, 3])
with col_psych1:
    st.metric("Global Crowd Sentiment", "34 / 100", "FEAR")
    st.caption("Tracking institutional regime vs. retail panic.")

# --- ASSET MATRIX (THE SYSTEM) ---
ticker = st.sidebar.selectbox("Asset Matrix", ["AAPL", "MU", "DOCS", "NVDA", "BTC-USD"])
df = yf.Ticker(ticker).history(period="6mo")

# QUANTITATIVE ENGINE (EMA/ATR)
df['EMA200'] = df['Close'].ewm(span=200).mean()
df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

# --- THE GATE ---
if not st.session_state.authenticated:
    st.warning("⚠️ INSTITUTIONAL DATA LOCKED: Premium members only.")
    key = st.text_input("Enter Institutional Access Key", type="password")
    if st.button("Unlock Core Engine"):
        if get_auth(key):
            st.session_state.authenticated = True
            st.rerun()
    st.link_button("Acquire Institutional Access", STRIPE_LINK)
else:
    # --- PREMIUM INSTITUTIONAL SUITE ---
    st.success("✅ Nexus Core: Institutional Engine Online")
    
    # SYSTEMATIC MATRIX LOGIC
    regime = "BULL" if df['Close'].iloc[-1] > df['EMA200'].iloc[-1] else "BEAR"
    action = "HOLD LONG" if regime == "BULL" else "HOLD SHORT"
    stop_level = df['Close'].iloc[-1] - (df['ATR'].iloc[-1] * 2)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Institutional Regime", regime)
    c2.metric("System Action", action)
    c3.metric("ATR Stop Level", f"${stop_level:.2f}")
    
    # INSTITUTIONAL CHART
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
