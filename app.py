import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

# Auth Function
def is_authorized(key):
    try:
        # Note: Ensure SUPABASE_URL and SUPABASE_KEY are in Streamlit Secrets
        url = f"{st.secrets['SUPABASE_URL']}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
        headers = {"apikey": st.secrets['SUPABASE_KEY'], "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}"}
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

# Sidebar UI
st.sidebar.title("Nexus Terminal")
if not st.session_state.get("auth", False):
    key = st.sidebar.text_input("Enter Premium Key", type="password")
    if st.sidebar.button("Unlock"):
        if is_authorized(key): st.session_state.auth = True; st.rerun()
        else: st.sidebar.error("Invalid Key")
    if st.sidebar.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
    st.sidebar.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
else:
    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()

# Main UI
st.title("Nexus Quantitative Engine")
if st.session_state.get("auth"):
    ticker = st.text_input("Enter Ticker", "MU").upper()
    if st.button("Execute Scan"):
        try:
            # Add timeout to catch connection issues early
            res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}", timeout=15).json()
            
            # Dashboard
            cols = st.columns(4)
            cols[0].metric("Regime", res['regime'])
            cols[1].metric("Psych Score", f"{res['psych_score']}/100")
            cols[2].metric("Sharpe", res['sharpe'])
            cols[3].metric("Volatility", f"{res['volatility']*100:.2f}%")
            st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']}")
            
            # Chart
            fig = go.Figure(data=[go.Candlestick(x=list(range(60)), open=res['chart_data']['Open'], 
                                   high=res['chart_data']['High'], low=res['chart_data']['Low'], 
                                   close=res['chart_data']['Close'])])
            for ma, color in [("MA20", "yellow"), ("MA50", "orange"), ("MA200", "red")]:
                fig.add_trace(go.Scatter(y=res['chart_data'][ma], name=ma, line=dict(color=color, width=1)))
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Cannot connect to API at {st.secrets['API_BASE_URL']}. Ensure backend is live on Render. Error: {e}")
