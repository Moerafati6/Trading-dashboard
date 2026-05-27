import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. SETUP
st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# Get secrets
API_BASE_URL = st.secrets["API_BASE_URL"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 2. AUTHENTICATION
def is_authorized(key):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

# 3. SIDEBAR (FIXED STRIPE BUTTON)
with st.sidebar:
    st.header("Nexus Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Key", type="password")
        if st.button("Unlock"):
            if is_authorized(key): 
                st.session_state.auth = True
                st.rerun()
            else: 
                st.error("Invalid Key")
        # THIS IS THE FIX: link_button handles the Stripe URL correctly
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800")
    else:
        st.success("Terminal Unlocked")
        if st.button("Logout"): 
            st.session_state.auth = False
            st.rerun()

# 4. DATA FETCHING (FIXED CONNECTION)
st.title("Nexus Institutional Terminal")

try:
    # If this fails, try changing "/signals/?" to "/signals?" 
    response = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=10)
    if response.status_code == 200:
        data = response.json()
        st.metric("Global Sentiment", f"{data.get('sentiment_score', 0)}/100")
        
        if st.session_state.auth:
            ticker = st.text_input("Asset Ticker", "AAPL").upper()
            if st.button("Scan Asset"):
                res = requests.get(f"{API_BASE_URL}/signals?mode=aggressive", timeout=10).json()
                asset = next((a for a in res['assets'] if a['ticker'] == ticker), None)
                if asset:
                    st.write(f"Regime: {asset['regime']} | Action: {asset['action']}")
                else: st.error("Ticker not found.")
    else:
        st.error(f"Backend returned status {response.status_code}")
except Exception as e:
    st.error(f"Connection Error: {e}")
