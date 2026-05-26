import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Systematic Behavioral Dashboard", layout="wide")

API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"

st.title("🧠 Behavioral Finance & Systematic Portfolio Matrix")
st.markdown("Analyzing institutional money flows, dynamic volatility boundaries, and collective crowd psychology.")

# Sidebar Configuration Controls
st.sidebar.header("Strategy Configurations")
mode = st.sidebar.selectbox("Select Portfolio Risk Profile", ["Consistent", "Aggressive"])

if st.sidebar.button("Execute Data Sync"):
    st.cache_data.clear()

try:
    with st.spinner("Fetching active systematic signals and emotional indices from Render cloud..."):
        response = requests.get(f"{API_BASE_URL}/signals?mode={mode.lower()}", timeout=15)
        
    if response.status_code == 200:
        payload = response.json()
        
        # 1. Collective Market Psychology Status
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
            
        # 3. Dynamic Data Grid
        st.subheader("⚡ Systematic Asset Matrix")
        df_assets = pd.DataFrame(payload['assets'])
        
        df_assets_display = df_assets[[
            "ticker", "current_price", "regime", "action", 
            "stop_level", "backtest_return_pct", "metrics_sharpe", "behavioral_bias"
        ]].copy()
        
        df_assets_display.columns = [
            "Asset Ticker", "Current Price", "Institutional Regime", 
            "System Action", "ATR Stop Level", "Backtest Return", "Sharpe Ratio", "Psychological/Behavioral Bias Insight"
        ]
        
        st.dataframe(df_assets_display.style.format({
            "Current Price": "${:.2f}",
            "ATR Stop Level": "${:.2f}",
            "Backtest Return": "{:.1f}%",
            "Sharpe Ratio": "{:.2f}"
        }), use_container_width=True)
        
        st.markdown("---")
        
        # 4. Phase 1 Addition: Visual Engine Deep Dive
        st.subheader("📈 Interactive Behavioral Charting Room")
        target_ticker = st.selectbox("Select Asset to Map Visually", df_assets["ticker"].tolist())
        
        # Find selected row parameters
        asset_data = df_assets[df_assets["ticker"] == target_ticker].iloc[0]
        
        # Create a beautiful, production-grade visual analytics box
        fig = go.Figure()
        
        # Current Value Anchor
        fig.add_trace(go.Scatter(
            x=["Current Price", "Risk Stop Boundary"],
            y=[asset_data["current_price"], asset_data["stop_level"]],
            mode="markers+text+lines",
            text=[f"${asset_data['current_price']}", f"${asset_data['stop_level']}"],
            textposition="top center",
            marker=dict(color=["#00FFCC", "#FF3366"], size=[15, 15]),
            line=dict(color="#444444", width=2, dash="dash"),
            name="System Parameters"
        ))
        
        fig.update_layout(
            title=f"Risk Corridor Mapping for {target_ticker} (Action: {asset_data['action']})",
            template="plotly_dark",
            height=400,
            yaxis=dict(title="Price Level ($)"),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 Visual Insight: {asset_data['behavioral_bias']}")
        
except Exception as e:
    st.error(f"Failed to bridge pipeline to backend server.")
