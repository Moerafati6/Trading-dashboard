import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Systematic Behavioral Dashboard", layout="wide")

# Permanent backend API link connected directly to your running Render web service
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
        
        # 1. Collective Market Psychology Status Window
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
        
        # 2. Portfolio Summary Architecture Metrics
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
        
        # 4. Enhanced Visual Corridor Engine Deep Dive (No Slanted Lines)
        st.subheader("📈 Interactive Behavioral Charting Room")
        target_ticker = st.selectbox("Select Asset to Map Visually", df_assets["ticker"].tolist())
        
        # Extract row properties for selected asset
        asset_data = df_assets[df_assets["ticker"] == target_ticker].iloc[0]
        cp = asset_data["current_price"]
        sl = asset_data["stop_level"]
        
        fig = go.Figure()
        
        # Flat Line 1: Current Price Threshold
        fig.add_trace(go.Scatter(
            x=["Structural Baseline", "Current Market Price Spot"],
            y=[cp, cp],
            mode="lines+markers+text",
            text=["", f"Current Spot: ${cp:.2f}"],
            textposition="top left",
            line=dict(color="#00FFCC", width=4),
            marker=dict(size=12, color="#00FFCC"),
            name="Current Price"
        ))
        
        # Flat Line 2: Dynamic ATR Trailing Risk Floor
        fig.add_trace(go.Scatter(
            x=["Structural Baseline", "Current Market Price Spot"],
            y=[sl, sl],
            mode="lines+markers+text",
            text=["", f"Risk Stop Floor: ${sl:.2f}"],
            textposition="bottom left",
            line=dict(color="#FF3366", width=3, dash="dash"),
            marker=dict(size=12, color="#FF3366"),
            name="ATR Risk Boundary"
        ))
        
        # Add a shading block showing the literal corridor of acceptable volatility
        fig.add_hrect(
            y0=min(cp, sl), y1=max(cp, sl),
            fillcolor="rgba(0, 255, 204, 0.04)", line_width=0,
            annotation_text="Volatility Protection Envelope", annotation_position="top left"
        )
        
        fig.update_layout(
            title=f"Risk Corridor Mapping: {target_ticker} ({asset_data['action']})",
            template="plotly_dark",
            height=400,
            yaxis=dict(
                title="Asset Price Unit ($)", 
                range=[min(cp, sl) * 0.92, max(cp, sl) * 1.08], 
                tickformat=".2f"
            ),
            xaxis=dict(showgrid=False),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 Behavioral Analysis: {asset_data['behavioral_bias']}")
        
except Exception as e:
    st.error(f"Failed to bridge pipeline to backend server.")
    st.info("Check that your Render backend has fully completed its deployment process.")
