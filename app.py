import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Initialize session state for auth
if "auth" not in st.session_state: st.session_state.auth = False

# Sidebar
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            # Replace 'YOUR_SECRET_KEY' with the key in your Streamlit Secrets
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.auth:
    # Get Movers from API
    try:
        movers = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
        choice = st.selectbox("Hot Market Movers", movers)
        search = st.text_input("Or Search Ticker").upper()
        ticker = search if search else choice
        
        if st.button("Execute Scan"):
            res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
            if "error" in res: st.error(f"Engine Error: {res['error']}")
            else:
                # Dashboard logic here... (same as previous professional block)
                st.write(f"Regime: {res['regime']} | Psych: {res['psych_meaning']}")
    except Exception as e:
        st.error(f"Connection error: {e}")
