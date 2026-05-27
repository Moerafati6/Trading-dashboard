import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Systematic Behavioral Dashboard", layout="wide")

API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"

# =====================================================
# PHASE 2: LIGHTWEIGHT CLIENT SIDE AUTHENTICATION WALL
# =====================================================
if "premium_access" not in st.session_state:
    st.session_state["premium_access"] = False

st.sidebar.title("🔐 Member Terminal")

if not st.session_state["premium_access"]:
    st.sidebar.subheader("Premium Terminal Login")
    # This token can be easily tied directly to your Stripe webhook access or a custom password
    access_token = st.sidebar.text_input("Enter Premium Access Passphrase", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        # Setting a temporary master launch key for your initial beta testers
        if access_token == "MICH_QUANT_2026":
            st.session_state["premium_access"] = True
            st.rerun()
        else:
            st.sidebar.error("Invalid Premium Passphrase. Access Denied.")
            
    # Free Tier Content Visible to Everyone
    st.title("📊 Collective Market Psychology Status (Free Tier)")
    st.markdown("Broad retail sentiment indexes monitored across global crowds.")
    
    # Quick live fallback call to fetch just the emotional baseline numbers safely
    try:
        with st.spinner("Connecting to sentiment engine..."):
            res = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=15)
            if res.status_code == 200:
                p = res.json()
                score = p.get("sentiment_score", 50)
                classification = p.get("sentiment_class", "Neutral")
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.metric(label="Global Crowd Sentiment Index", value=f"{score} / 100")
                with col_f2:
                    st.metric(label="Emotional Classification", value=str(classification).upper())
                st.progress(score / 100)
    except Exception:
        st.info("🔄 The backend cloud engine is warming up from standby mode. Please wait 60 seconds and refresh.")

    st.markdown("---")
    st.info("🔒 **Premium Features Locked:** The Systematic Asset Matrix, Sharpe Risk Metrics, Dynamic ATR Volatility Floors, and 30-Day Interactive Candlestick Charting rooms are restricted to active tier members.")
    
    # Add a clean informational card for your future Stripe payment integration link
    st.markdown("""
    ### 🚀 Unlock the Complete Quant Portfolio Suite
    Gain direct visibility into real-time institutional trend regimes and algorithmic risk boundaries.
    * **Automated Asset Matrix:** Real-time track points for tech equities, macro assets, and crypto portfolios.
    * **Precision Risk Corridors:** Daily calculated volatility trailing stops to remove exit hesitation.
    * **Interactive Candlestick Rooms:** Hover-state timeline analytics for professional execution.
    
    👉 [Click Here to Subscribe & Get Your Access Key via Stripe]
    """)

else:
    # Authenticated Premium Dashboard Layer Unlocks Safely Here
    st.sidebar.success("🔑 Premium Access Granted")
    if st.sidebar.button("Lock Terminal / Log Out"):
        st.session_state["premium_access"] = False
        st.rerun()

    st.title("🧠 Behavioral Finance & Systematic Portfolio Matrix")
    st.markdown("Analyzing institutional money flows, dynamic volatility boundaries, and collective crowd psychology.")

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
            
            # 2. Portfolio Summary Performance Metrics
            st.subheader("📋 Portfolio System Performance")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Strategy Mean Portfolio Return", value=f"{payload['avg_portfolio_return_pct']}%")
            with col2:
                st.metric(label="Dynamic ATR Trailing Multiplier", value=f"{payload['atr_stop_multiplier']}x")
            with col3:
                st.metric(label="Active Asset Monitored Count", value=len(payload['assets']))
                
            # 3. Dynamic Technical Data Grid
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
            
            # 4. Candlestick Visual Room
            st.subheader("📈 Interactive Behavioral Charting Room")
            target_ticker = st.selectbox("Select Asset to Map Visually", df_assets["ticker"].tolist())
            
            asset_data = df_assets[df_assets["ticker"] == target_ticker].iloc[0]
            hist = asset_data["history"]
            
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=hist["dates"], open=hist["open"], high=hist["high"], low=hist["low"], close=hist["close"],
                increasing_line_color="#00FFCC", decreasing_line_color="#FF3366", name="Price Candle"
            ))
            
            fig.add_trace(go.Scatter(
                x=hist["dates"], y=hist["stop_line"], mode="lines",
                line=dict(color="#FFFF00", width=2, dash="dot"), name="ATR Trailing Stop"
            ))
            
            fig.update_layout(
                title=f"30-Day Rolling Candlestick & Systematic Risk Corridor: {target_ticker}",
                template="plotly_dark", height=450,
                xaxis=dict(rangeslider_visible=False, type="category"),
                yaxis=dict(title="Price Level ($)", tickformat=".2f"),
                margin=dict(l=40, r=40, t=40, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.info(f"💡 Behavioral Analysis: {asset_data['behavioral_bias']}")
            
    except Exception as e:
        st.error(f"Failed to bridge pipeline to backend server.")
        st.info("The cloud environment is awakening from standby mode. Hit the sync controls or refresh in 30 seconds.")
