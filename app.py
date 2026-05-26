import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Systematic Behavioral Dashboard", layout="wide")

# CRITICAL: Hardcoded link directly to your running Render web backend root domain
API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"

st.title("🧠 Behavioral Finance & Systematic Portfolio Matrix")
st.markdown("Analyzing institutional money flows, dynamic volatility boundaries, and collective crowd psychology.")

# Sidebar Configuration Controls
st.sidebar.header("Strategy Configurations")
mode = st.sidebar.selectbox("Select Portfolio Risk Profile", ["Consistent", "Aggressive"])

# Trigger Backend Data Harvest
if st.sidebar.button("Execute Data Sync"):
    st.cache_data.clear()

try:
    with st.spinner("Fetching active systematic signals and emotional indices from Render cloud..."):
        response = requests.get(f"{API_BASE_URL}/signals?mode={mode.lower()}", timeout=15)
        
    if response.status_code == 200:
        payload = response.json()
        
        # 1. Visualizing the Crowd Psychology Layer
        score = payload.get("sentiment_score", 50)
        classification = payload.get("sentiment_class", "Neutral")
        
        st.subheader("📊 Collective Market Psychology Status")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric(label="Global Crowd Sentiment Index", value=f"{score} / 100")
        with col_s2:
            st.metric(label="Emotional Classification", value=str(classification).upper())
        with col_s3:
            if score <= 25:
                st.warning("⚠️ Market State: EXTREME FEAR (High Accumulation Opportunity)")
            elif score >= 75:
                st.error("🚨 Market State: EXTREME GREED (High Overbought Risk)")
            else:
                st.success("✅ Market State: Rational Distribution")
                
        st.progress(score / 100)
        st.markdown("---")
        
        # 2. Portfolio Summary Architecture
        st.subheader("📋 Portfolio System Performance")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Strategy Mean Portfolio Return", value=f"{payload['avg_portfolio_return_pct']}%")
        with col2:
            st.metric(label="Dynamic ATR Trailing Multiplier", value=f"{payload['atr_stop_multiplier']}x")
        with col3:
            st.metric(label="Active Asset Monitored Count", value=len(payload['assets']))
            
        # 3. Dynamic Technical & Psychological Data Grid
        st.subheader("⚡ Systematic Asset Matrix")
        df_assets = pd.DataFrame(payload['assets'])
        
        # Reordering columns to prioritize behavioral indicators beautifully
        df_assets = df_assets[[
            "ticker", "current_price", "regime", "action", 
            "stop_level", "backtest_return_pct", "metrics_sharpe", "behavioral_bias"
        ]]
        
        # Clean formatting definitions for UI display
        df_assets.columns = [
            "Asset Ticker", "Current Price", "Institutional Regime", 
            "System Action", "ATR Stop Level", "Backtest Return", "Sharpe Ratio", "Psychological/Behavioral Bias Insight"
        ]
        
        st.dataframe(df_assets.style.format({
            "Current Price": "${:.2f}",
            "ATR Stop Level": "${:.2f}",
            "Backtest Return": "{:.1f}%",
            "Sharpe Ratio": "{:.2f}"
        }), use_container_width=True)
        
except Exception as e:
    st.error(f"Failed to bridge pipeline to backend server.")
    st.info("Ensure your Render engine has finished initializing and that Line 11 matches your running domain.")
