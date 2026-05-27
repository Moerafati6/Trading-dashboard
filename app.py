import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800" # Your Stripe URL
# Secrets are managed via Streamlit Cloud Settings -> Secrets
SUPABASE_URL = st.secrets["https://acjjbmtjouundpsbycue.supabase.co"]
SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"]

st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# --- AUTHENTICATION GATE ---
def check_auth(key):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    try:
        res = requests.get(url, headers=headers)
        return res.status_code == 200 and len(res.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

# --- SIDEBAR: AUTH & SUBSCRIPTION ---
with st.sidebar:
    st.header("Nexus Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Access Key", type="password")
        if st.button("Unlock Terminal"):
            if check_auth(key): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        st.link_button("Subscribe for $29/mo", STRIPE_LINK)
    else:
        st.success("Premium Access Active")
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- MAIN DASHBOARD ---
st.title("🧠 Behavioral Finance & Systematic Portfolio Matrix")

# 1. PUBLIC PREVIEW (Visible to all)
try:
    response = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=5)
    payload = response.json()
    st.metric("Global Crowd Sentiment Index", f"{payload.get('sentiment_score', 0)}/100")
except: st.info("Public data pulse initializing...")

# 2. PREMIUM TERMINAL (Locked behind Auth)
if st.session_state.auth:
    st.divider()
    st.subheader("⚡ Institutional Asset Search")
    
    # Dynamic Search: Allow user to type any ticker
    user_ticker = st.text_input("Enter Ticker to Analyze (e.g., AAPL, NVDA, TSLA)", "AAPL").upper()
    
    if st.button("Execute Institutional Scan"):
        try:
            res = requests.get(f"{API_BASE_URL}/signals?mode=aggressive", timeout=10).json()
            # Logic: Find the asset in the backend list
            asset = next((a for a in res['assets'] if a['ticker'] == user_ticker), None)
            
            if asset:
                # [Insert your Metric columns here]
                c1, c2, c3 = st.columns(3)
                c1.metric("Regime", asset['regime'])
                c2.metric("System Action", asset['action'])
                c3.metric("ATR Stop", f"${asset['stop_level']}")
                
                # [Insert your Charting Engine here]
                # (Use the asset['current_price'] and asset['stop_level'] variables)
                st.success(f"Systematic analysis for {user_ticker} complete.")
            else:
                st.warning(f"Ticker '{user_ticker}' not found in the institutional watch-list.")
        except Exception as e:
            st.error("Engine failed to return data. Verify backend is active.")
else:
    st.warning("⚠️ Institutional Matrix is locked. Please enter your premium key to unlock.")
