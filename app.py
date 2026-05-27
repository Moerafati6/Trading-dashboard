import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Nexus Quantitative Terminal", layout="wide")
API_BASE_URL = st.secrets["API_BASE_URL"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def is_authorized(key):
    url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{key}&is_active=eq.true"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200 and len(response.json()) > 0
    except: return False

if "auth" not in st.session_state: st.session_state.auth = False

with st.sidebar:
    st.header("Nexus Access")
    if not st.session_state.auth:
        key = st.text_input("Enter Premium Key", type="password")
        if st.button("Unlock"):
            if is_authorized(key): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        if st.button("Start 7-Day Free Trial"):
            st.session_state.auth = True; st.rerun()
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Terminal")

if st.session_state.auth:
    ticker = st.text_input("Scan Asset", "AAPL").upper()
    if st.button("Scan Asset"):
        # Debugging Logic added here
        try:
            response = requests.get(f"{API_BASE_URL}/signals?ticker={ticker}", timeout=10)
            if response.status_code == 200:
                res = response.json()
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Regime", res['regime'])
                c2.metric("Psych Score", f"{res['psych_score']}/100")
                c3.metric("Sharpe Ratio", res['sharpe'])
                c4.metric("Volatility", f"{res['volatility']*100:.2f}%")
                st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']}")
                
                fig = make_subplots(rows=1, cols=1)
                fig.add_trace(go.Candlestick(x=list(range(60)), open=res['chart_data']['Open'], high=res['chart_data']['High'],
                                             low=res['chart_data']['Low'], close=res['chart_data']['Close'], name="Price"))
                for ma, color in [("MA20", "yellow"), ("MA50", "orange"), ("MA200", "red")]:
                    fig.add_trace(go.Scatter(y=res['chart_data'][ma], name=ma, line=dict(color=color, width=1)))
                fig.update_layout(template="plotly_dark", xaxis_title="Time", yaxis_title="Price")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"API Error: Status {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Connection Failed: {e}")
