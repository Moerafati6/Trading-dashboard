import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP & SECRETS
st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# Look up the values by their names from your Streamlit Secrets settings
API_BASE_URL = st.secrets["API_BASE_URL"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 2. AUTHENTICATION ENGINE
def is_authorized(key):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

# 3. SIDEBAR GATEKEEPER
with st.sidebar:
    st.header("Nexus Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Key", type="password")
        if st.button("Unlock"):
            if is_authorized(key): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key.")
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800")
    else:
        st.success("Terminal Unlocked")
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

# 4. DASHBOARD ENGINE
st.title("🧠 Behavioral Finance & Systematic Matrix")

# Public Data
try:
    res = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=5).json()
    st.metric("Global Sentiment Index", f"{res.get('sentiment_score', 0)}/100")
except: st.warning("Public Data Engine initializing...")

# Premium Data
if st.session_state.auth:
    st.divider()
    ticker = st.text_input("Enter Asset Ticker", "AAPL").upper()
    if st.button("Scan Asset"):
        try:
            res = requests.get(f"{API_BASE_URL}/signals?mode=aggressive", timeout=10).json()
            asset = next((a for a in res['assets'] if a['ticker'] == ticker), None)
            if asset:
                c1, c2, c3 = st.columns(3)
                c1.metric("Regime", asset['regime'])
                c2.metric("Action", asset['action'])
                c3.metric("ATR Stop", f"${asset['stop_level']}")
                
                # Charting Corridor
                fig = go.Figure()
                fig.add_trace(go.Scatter(y=[asset['current_price'], asset['current_price']], name="Price"))
                fig.add_trace(go.Scatter(y=[asset['stop_level'], asset['stop_level']], name="Stop", line=dict(dash="dash")))
                st.plotly_chart(fig, use_container_width=True)
            else: st.error("Ticker not in institutional range.")
        except: st.error("Backend connection error.")
else:
    st.info("Unlock to access institutional ATR and signal directives.")
