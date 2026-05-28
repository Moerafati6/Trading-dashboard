import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# 1. Setup Session State
if "auth" not in st.session_state: st.session_state.auth = False

# 2. Sidebar with Error Handling
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            # Use .get() to prevent crash if secret is missing
            if key == st.secrets.get("PASSKEY", "default_key"): st.session_state.auth = True; st.rerun()
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

# 3. Main Logic
if st.session_state.auth:
    base_url = st.secrets.get("API_BASE_URL", "http://localhost:8000")
    
    try:
        movers = requests.get(f"{base_url}/market_movers", timeout=5).json()
    except:
        movers = ["SELECT TICKER", "NVDA", "AMD", "AVGO", "TSM", "MSFT"]
        
    col1, col2 = st.columns(2)
    choice = col1.selectbox("Hot Market Movers", movers)
    search = col2.text_input("Or Search Ticker")
    ticker = search.upper() if search else choice
    
    if st.button("Execute Scan"):
        if ticker == "SELECT TICKER":
            st.warning("Please select a ticker.")
        else:
            try:
                res = requests.get(f"{base_url}/signals?ticker={ticker}", timeout=10).json()
                if "error" in res:
                    st.error(res['error'])
                else:
                    st.metric("Regime", res.get("regime", "N/A"))
                    st.write(f"Psych: {res.get('psych_meaning')} ({res.get('psych_score')}) | Return: {res.get('perf')}%")
                    
                    fig = go.Figure(data=[go.Candlestick(
                        open=res['chart_data']['Open'], high=res['chart_data']['High'],
                        low=res['chart_data']['Low'], close=res['chart_data']['Close']
                    )])
                    fig.update_layout(template="plotly_dark", height=500)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Connection failed: {e}")
