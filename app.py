import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Nexus Quantitative Engine")
ticker = st.text_input("Enter Ticker", "NVDA").upper()

if st.button("Execute Scan"):
    try:
        # Ensure API_BASE_URL is set in your Streamlit Secrets
        res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
        
        if "error" in res:
            st.error(f"Engine Error: {res['error']}")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Regime", res['regime'])
            c2.metric("Psych", f"{res['psych_score']}/100")
            c3.metric("Sharpe", res['sharpe'])
            c4.metric("Performance", f"{res['perf']}%")
            
            st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']} | **Vol:** {res['volatility']*100:.2f}%")
            
            # Rendering the candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=list(range(len(res['chart_data']['Open']))),
                open=res['chart_data']['Open'], 
                high=res['chart_data']['High'], 
                low=res['chart_data']['Low'], 
                close=res['chart_data']['Close']
            )])
            fig.update_layout(template="plotly_dark", height=500)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Connection Failed: {e}")
Key fixes applied:
