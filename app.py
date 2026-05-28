import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

if "auth" not in st.session_state: st.session_state.auth = False

with st.sidebar:
    st.title("Nexus Terminal")
    key = st.text_input("Enter Passkey", type="password")
    if st.button("Unlock"):
        if key == st.secrets.get("PASSKEY"): st.session_state.auth = True
    if st.button("Start 7-Day Free Trial"): st.session_state.auth = True

st.title("Nexus Quantitative Engine")
if st.session_state.auth:
    movers = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
    ticker = st.selectbox("Hot Market Movers", movers)
    
    if st.button("Execute Scan"):
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res:
            st.error(res['error'])
        else:
            st.metric("Regime", res['regime'])
            st.write(f"Psych: {res['psych_meaning']} ({res['psych_score']}) | Return: {res['perf']}%")
            
            fig = go.Figure(data=[go.Candlestick(
                open=res['chart_data']['Open'], high=res['chart_data']['High'],
                low=res['chart_data']['Low'], close=res['chart_data']['Close']
            )])
            st.plotly_chart(fig)
