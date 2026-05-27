import streamlit as st
import requests
import plotly.graph_objects as go

# 1. SETUP
st.set_page_config(page_title="Nexus Quantitative Terminal", layout="wide")

# Secrets
API_BASE_URL = st.secrets["API_BASE_URL"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 2. AUTHENTICATION
def is_authorized(key):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

# 3. SIDEBAR
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

# 4. DATA FETCHING
st.title("Nexus Quantitative Terminal")

try:
    # Public sentiment pulse
    response = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=30)
    if response.status_code == 200:
        data = response.json()
        st.metric("Global Sentiment", f"{data.get('sentiment_score', 0)}/100")
        
        if st.session_state.auth:
            st.divider()
            ticker = st.text_input("Search Any Asset (e.g., NVDA, TSLA, BTC-USD)", "AAPL").upper()
            if st.button("Scan Asset"):
                # Pass the dynamic ticker to the backend
                url = f"{API_BASE_URL}/signals?mode=aggressive&ticker={ticker}"
                res = requests.get(url, timeout=30).json()
                
                if res.get('assets'):
                    asset = res['assets'][0]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Regime", asset['regime'])
                    c2.metric("Action", asset['action'])
                    c3.metric("ATR Stop", f"${asset['stop_level']}")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=asset['history']['close'], name="Price"))
                    fig.add_trace(go.Scatter(y=asset['history']['stop_line'], name="Stop", line=dict(dash="dash")))
                    st.plotly_chart(fig, use_container_width=True)
                else: 
                    st.error("Asset data unavailable. Ensure the ticker is correct.")
    else:
        st.error(f"Backend connection error (Status {response.status_code})")
except Exception as e:
    st.error(f"Connection Error: {e}")
