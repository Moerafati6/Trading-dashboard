import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Nexus Quantitative Terminal", layout="wide")

# Sidebar: Institutional Access Control
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.get("auth", False):
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

# Main Display
st.title("Nexus Quantitative Engine")
if st.session_state.get("auth"):
    ticker = st.text_input("Enter Ticker (e.g., MU, NVDA)", "MU").upper()
    if st.button("Execute Scan"):
        try:
            res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
            
            # Institutional Metric Row
            cols = st.columns(4)
            cols[0].metric("Regime", res['regime'])
            cols[1].metric("Psych Score", f"{res['psych_score']}/100")
            cols[2].metric("Sharpe", res['sharpe'])
            cols[3].metric("Volatility", f"{res['volatility']*100:.2f}%")
            st.info(f"**Strategy:** {res['action']} | **Sentiment:** {res['psych_meaning']}")
            
            # Institutional Chart
            fig = go.Figure(data=[go.Candlestick(x=list(range(60)), open=res['chart_data']['Open'], 
                                   high=res['chart_data']['High'], low=res['chart_data']['Low'], 
                                   close=res['chart_data']['Close'])])
            for ma, color in [("MA20", "yellow"), ("MA50", "orange"), ("MA200", "red")]:
                fig.add_trace(go.Scatter(y=res['chart_data'][ma], name=ma, line=dict(color=color, width=1)))
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Terminal Connection Error: Ensure your API backend is running.")
else:
    st.warning("Please activate your trial or enter your premium key.")
