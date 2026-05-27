import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
# Replace with your actual Render URL and Supabase keys
API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# --- AUTHENTICATION VAULT ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

def check_supabase(key):
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

# --- SIDEBAR: AUTH & SUBSCRIPTION ---
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.authenticated:
        st.subheader("Institutional Login")
        key = st.text_input("Access Key", type="password")
        if st.button("Unlock Core Engine"):
            if check_supabase(key):
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Invalid Key.")
        st.link_button("Subscribe for Premium Access", STRIPE_LINK)
    else:
        if st.button("Logout"): st.session_state.authenticated = False; st.rerun()

# --- MAIN DASHBOARD: THE "FACE" ---
st.title("Nexus Quantitative Terminal")

# PUBLIC PSYCHOLOGY (FREE TIER)
st.subheader("Global Market Psychology (Public Preview)")
try:
    res = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=5)
    if res.status_code == 200:
        val = res.json().get('sentiment_score', 28)
        st.metric("Crowd Sentiment Index", f"{val}/100", "Fear" if val < 50 else "Greed")
except: st.info("Public sentiment engine initializing...")

st.markdown("---")

# INSTITUTIONAL ASSET MATRIX (PREMIUM TIER)
if st.session_state.authenticated:
    st.subheader("⚡ Institutional Asset Matrix")
    ticker = st.text_input("Enter Ticker", "AAPL").upper()
    
    if st.button("Generate Institutional Signal"):
        try:
            res = requests.get(f"{API_BASE_URL}/signals?mode=aggressive", timeout=10)
            if res.status_code == 200:
                assets = res.json().get('assets', [])
                data = next((a for a in assets if a['ticker'] == ticker), None)
                
                if data:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Regime", data['regime'])
                    c2.metric("System Action", data['action'])
                    c3.metric("ATR Stop", f"${data['stop_level']}")
                    
                    # Charting the Signal
                    fig = go.Figure(data=[go.Candlestick(x=pd.to_datetime(data['history']['dates']),
                                    open=data['history']['open'], high=data['history']['high'],
                                    low=data['history']['low'], close=data['history']['close'])])
                    fig.add_trace(go.Scatter(x=pd.to_datetime(data['history']['dates']), y=data['history']['stop_line'], name='ATR Stop', line=dict(dash='dot')))
                    st.plotly_chart(fig, use_container_width=True)
                else: st.warning("Ticker not found in institutional watch-list.")
        except: st.error("Backend offline. Check Render deployment.")
else:
    st.warning("⚠️ Institutional data is locked. Authenticate in the sidebar to view ATR signals and System Actions.")
