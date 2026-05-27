import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION ---
API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk" # <--- INPUT YOUR KEY HERE
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# --- AUTHENTICATION ENGINE ---
def check_key(key):
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    res = requests.get(url, headers=headers)
    return res.status_code == 200 and len(res.json()) > 0

if "auth" not in st.session_state: st.session_state.auth = False

# --- UI LAYER ---
st.title("📈 Nexus Institutional Terminal")

# Sidebar: The Vault
with st.sidebar:
    st.header("Terminal Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Key", type="password")
        if st.button("Unlock Engine"):
            if check_key(key): st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied.")
        st.link_button("Purchase Access ($29)", STRIPE_LINK)
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

# Public Preview
st.subheader("Market Psychology (Public)")
try:
    data = requests.get(f"{API_BASE_URL}/signals?mode=consistent").json()
    st.metric("Sentiment Score", f"{data.get('sentiment_score', 0)}/100")
except: st.write("Public preview initializing...")

# Premium Institutional Suite
if st.session_state.auth:
    st.divider()
    st.subheader("⚡ Systematic Asset Matrix")
    ticker = st.text_input("Analyze Specific Asset", "AAPL").upper()
    
    if st.button("Generate Signal"):
        res = requests.get(f"{API_BASE_URL}/signals?mode=aggressive").json()
        asset = next((a for a in res['assets'] if a['ticker'] == ticker), None)
        if asset:
            c1, c2, c3 = st.columns(3)
            c1.metric("Regime", asset['regime'])
            c2.metric("System Action", asset['action'])
            c3.metric("ATR Stop", f"${asset['stop_level']}")
            st.success(f"Strategy: {asset['action']} now.")
        else: st.warning("Ticker not currently in systematic range.")
else:
    st.info("Unlock the terminal to access institutional ATR signals and Entry/Exit directives.")
