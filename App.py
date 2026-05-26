import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Systematic Trading Interface", layout="wide")

# =====================================================
# CONFIGURATION - PASTE YOUR LIVE NGROK URL HERE
# =====================================================
API_BASE_URL = "https://dipping-finite-edgy.ngrok-free.dev/signals?mode=aggressive"

st.title("⚡ Systematic Trading Engine Dashboard")
st.markdown("Real-time trend confluences, macro regimes, and dynamic ATR trailing stops.")
st.write("---")

# Dropdown to toggle between your crypto and equity baskets
mode = st.selectbox("Select Active Portfolio Basket:", ["aggressive", "consistent"])

try:
    # Connect directly to your live Ngrok data tunnel
    api_url = f"{API_BASE_URL}/signals?mode={mode}"
    response = requests.get(api_url, timeout=12)
    data = response.json()
    
    if "error" in data:
        st.error(f"Backend Processing Error: {data['error']}")
    else:
        # Display clean KPI block cards at the top
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Average Portfolio Return", value=f"{data['avg_portfolio_return_pct']}%")
        with col2:
            st.metric(label="ATR Stop Multiplier", value=f"{data['atr_multiplier']}x")
        with col3:
            st.metric(label="Total Tracked Assets", value=len(data['assets']))
            
        st.write("###")
        st.subheader("🎯 Active Execution Signals")
        
        # Turn the raw text into a clean visual spreadsheet table
        df = pd.DataFrame(data["assets"])
        column_order = ["ticker", "regime", "action", "current_price", "stop_level", "backtest_return_pct", "metrics_sharpe"]
        df = df[column_order]
        df.columns = ["Asset Ticker", "Macro Regime", "Action Status", "Live Price ($)", "ATR Trailing Stop", "Historical Return (%)", "Sharpe Ratio"]
        
        # Color coding for easy scannability on your phone
        def highlight_matrix(val):
            if "LONG" in str(val):
                return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            elif "SHORT" in str(val):
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            elif "BULL" in str(val):
                return 'color: #28a745; font-weight: bold;'
            elif "BEAR" in str(val):
                return 'color: #dc3545; font-weight: bold;'
            return ''

        st.dataframe(df.style.applymap(highlight_matrix), use_container_width=True, height=450)
        
except Exception as e:
    st.error("🔴 Connection Interrupted: Unable to contact the cloud trading engine server.")
    st.info("Ensure your Google Colab notebook cell is still actively running and hasn't timed out.")
