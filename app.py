import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")
if st.session_state.auth:
    ticker = st.text_input("Search Ticker", value="NVDA").upper()
    if st.button("Execute Scan"):
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res: st.error(res['error'])
        else:
            st.metric("Regime", res['regime'])
            st.info(f"Psych: {res['psych_meaning']} ({res['psych_score']}) | Return: {res['perf']}%")
            
            fig = go.Figure(data=[go.Candlestick(
                open=res['chart_data']['Open'], high=res['chart_data']['High'],
                low=res['chart_data']['Low'], close=res['chart_data']['Close']
            )])
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
