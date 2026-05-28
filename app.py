import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Initialize session state for authentication
if "auth" not in st.session_state:
    st.session_state.auth = False

with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            if key == st.secrets.get("PASSKEY"):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"):
            st.session_state.auth = True
            st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.auth:
    # Fetch movers for the dropdown
    try:
        movers = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
    except:
        movers = ["NVDA", "AMD", "AVGO", "TSM", "MSFT"]
        
    choice = st.selectbox("Hot Market Movers", movers)
    search = st.text_input("Or Search Ticker")
    ticker = search if search else choice
    
    if st.button("Execute Scan"):
        # Fixed logic: Ticker is passed cleanly to the backend
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        
        if "error" in res:
            st.error(res['error'])
        else:
            # Display metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Regime", res['regime'])
            c2.metric("Psych", f"{res['psych_score']}/100")
            c3.metric("Return", f"{res['perf']}%")
            
            # Display psychology and action
            st.info(f"Sentiment: {res['psych_meaning']} | Action: {res['action']}")
            
            # Display Candlestick Chart
            fig = go.Figure(data=[go.Candlestick(
                x=list(range(len(res['chart_data']['Open']))),
                open=res['chart_data']['Open'],
                high=res['chart_data']['High'],
                low=res['chart_data']['Low'],
                close=res['chart_data']['Close']
            )])
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
