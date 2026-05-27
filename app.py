import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Nexus Institutional Terminal", layout="wide")

# Secrets
API_BASE_URL = st.secrets["API_BASE_URL"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def is_authorized(key):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

with st.sidebar:
    st.header("Nexus Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Key", type="password")
        if st.button("Unlock"):
            if is_authorized(key): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        st.success("Terminal Unlocked")
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Terminal")

if st.session_state.auth:
    ticker = st.text_input("Search Asset", "AAPL").upper()
    if st.button("Scan Asset"):
        res = requests.get(f"{API_BASE_URL}/signals?ticker={ticker}").json()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Regime", res['regime'])
        c2.metric("Psych Score", f"{res['psych_score']}/100")
        c3.metric("Sharpe Ratio", res['sharpe'])
        c4.metric("Return", f"{res['return_pct']}%")
        
        fig = go.Figure(data=go.Scatter(y=res['history']['Close'], name="Price"))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please unlock the terminal to access institutional data.")
