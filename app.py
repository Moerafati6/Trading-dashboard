import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Nexus Terminal")

# Sidebar - Subscription/Auth Logic
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.get("auth", False):
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.get("auth", False):
    movers = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
    col1, col2 = st.columns([1, 2])
    with col1:
        choice = st.selectbox("Hot Market Movers", movers)
        search = st.text_input("Or Search Ticker").upper()
        ticker = search if search else choice
        scan = st.button("Execute Scan")

    if scan:
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res: st.error(f"Engine Error: {res['error']}")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Regime", res['regime'])
            c2.metric("Psych", f"{res['psych_score']}/100")
            c3.metric("Sharpe", res['sharpe'])
            c4.metric("Performance", f"{res['perf']}%")
            st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']} | **Vol:** {res['volatility']*100:.2f}%")
            
            fig = go.Figure(data=[go.Candlestick(x=list(range(len(res['chart_data']['Open']))),
                            open=res['chart_data']['Open'], high=res['chart_data']['High'], 
                            low=res['chart_data']['Low'], close=res['chart_data']['Close'])])
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
