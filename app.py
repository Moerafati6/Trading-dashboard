import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

def is_authorized(key):
    try:
        url = f"{st.secrets['SUPABASE_URL']}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
        headers = {"apikey": st.secrets['SUPABASE_KEY'], "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"}
        return requests.get(url, headers=headers, timeout=5).status_code == 200 and len(requests.get(url, headers=headers).json()) > 0
    except: return False

with st.sidebar:
    st.title("Nexus Institutional")
    if not st.session_state.get("auth", False):
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            if is_authorized(key): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")
if st.session_state.get("auth"):
    ticker = st.text_input("Ticker", "NVDA").upper()
    if st.button("Execute Scan"):
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        if "error" in res: st.error(res['error'])
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Regime", res['regime'])
            c2.metric("Psych", f"{res['psych_score']}/100")
            c3.metric("Sharpe", res['sharpe'])
            c4.metric("Performance", f"{res['perf']}%")
            st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']} | **Volatility:** {res['volatility']*100:.2f}%")
            
            fig = go.Figure(data=[go.Candlestick(x=list(range(60)), open=res['chart_data']['Open'], high=res['chart_data']['High'], low=res['chart_data']['Low'], close=res['chart_data']['Close'])])
            for ma, color in [("MA20", "yellow"), ("MA50", "orange"), ("MA200", "red")]:
                fig.add_trace(go.Scatter(y=res['chart_data'][ma], name=ma, line=dict(color=color, width=1)))
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)
