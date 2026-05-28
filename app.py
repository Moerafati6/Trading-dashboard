import streamlit as st
import requests

st.set_page_config(layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            # Uses the secret key you set in your dashboard
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.auth:
    # Fetch movers for the dropdown
    movers_res = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
    ticker = st.selectbox("Hot Market Movers", movers_res)
    
    if st.button("Execute Scan"):
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res:
            st.error(f"Engine Error: {res['error']}")
        else:
            st.success(f"Regime: {res['regime']} | Action: {res['action']} | Price: ${res['price']:.2f}")dth=True)
