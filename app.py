import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Initialize Session
if "auth" not in st.session_state: st.session_state.auth = False

# Sidebar: Auth & Subscription
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            # Ensure this matches the key in your Streamlit Secrets exactly
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.auth:
    ticker = st.text_input("Enter Ticker", "NVDA").upper()
    if st.button("Execute Scan"):
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res:
            st.error(f"Engine Error: {res['error']}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Regime", res['regime'])
            c2.metric("Psych Score", f"{res['psych_score']}/100")
            c3.metric("Return", f"{res['perf']}%")
            
            st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']}")
            
            # Visualizing the chart
            fig = go.Figure(data=[go.Candlestick(
                x=list(range(len(res['chart_data']['Open']))),
                open=res['chart_data']['Open'], high=res['chart_data']['High'], 
                low=res['chart_data']['Low'], close=res['chart_data']['Close']
            )])
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
