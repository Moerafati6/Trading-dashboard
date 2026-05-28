import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Nexus terminal")

# Initialize authentication state
if "auth" not in st.session_state: st.session_state.auth = False

# Sidebar - Trial & Payment Flow
with st.sidebar:
    st.title("Nexus Terminal")
    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")
        if st.button("Unlock"):
            # Ensure 'PASSKEY' is set correctly in your Streamlit secrets
            if key == st.secrets.get("PASSKEY"): st.session_state.auth = True; st.rerun()
            else: st.error("Invalid Key")
        
        # Add payment buttons for production look
        if st.button("Start 7-Day Free Trial"): st.session_state.auth = True; st.rerun()
        st.link_button("Subscribe ($29/mo)", "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801")
    else:
        if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.title("Nexus Quantitative Engine")

if st.session_state.auth:
    # Get standard movers from backend
    try:
        movers_res = requests.get(f"{st.secrets['API_BASE_URL']}/market_movers").json()
        choice = st.selectbox("Hot Market Movers", movers_res)
    except:
        choice = st.selectbox("Hot Market Movers", ["NVDA"]) # Default safe ticker

    # Define ticker
    search = st.text_input("Or Search Ticker").upper()
    ticker = search if search else choice
    
    if st.button("Execute Scan"):
        # Make the API call to your live backend
        try:
            res = requests.get(f"{st.secrets['API_BASE_URL']}/signals?ticker={ticker}").json()
            
            if "error" in res:
                # Catch ticker not found or API errors
                st.error(f"Scan failed: {res['error']}")
            else:
                # Top Metrics
                c1, c2, c3 = st.columns(3)
                c1.metric("Regime", res['regime'])
                c2.metric("Psych Score", f"{res['psych_score']}/100")
                c3.metric("Return", f"{res['perf']}%")
                
                # Detailed Summary
                st.info(f"**Action:** {res['action']} | **Sentiment:** {res['psych_meaning']} | **Price:** ${res['price']:.2f} | **Vol:** {res['volatility']*100:.2f}%")
                
                # Plot Candlestick Chart
                fig = go.Figure(data=[go.Candlestick(
                    x=list(range(len(res['chart_data']['Open']))),
                    open=res['chart_data']['Open'], high=res['chart_data']['High'], 
                    low=res['chart_data']['Low'], close=res['chart_data']['Close']
                )])
                fig.update_layout(template="plotly_dark", height=500, title_text=f"{ticker} Chart")
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Connection Error to Engine Backend: {e}")
