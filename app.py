import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go

# --- CONFIGURATION ---
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

st.set_page_config(page_title="Nexus Terminal", layout="wide")

if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.header("🔑 Authentication")
    key = st.sidebar.text_input("Enter Passkey", type="password")
    if st.sidebar.button("Unlock Terminal"):
        # Logic to verify key
        st.session_state.authenticated = True; st.rerun()
    st.sidebar.link_button("Purchase Access", STRIPE_LINK)
else:
    # --- AGGRESSIVE & CONSISTENT ENGINE ---
    ticker = "AAPL"
    df = yf.Ticker(ticker).history(period="6mo")
    
    # INDICATORS: EMA Stacks
    df['EMA20'] = df['Close'].ewm(span=20).mean()
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    
    # ATR (Volatility Engine)
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
    
    # REGIME LOGIC
    regime = "AGGRESSIVE" if df['Close'].iloc[-1] > df['EMA50'].iloc[-1] else "CONSISTENT"
    
    # DASHBOARD LAYOUT
    st.title(f"Nexus Terminal: {regime} REGIME")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("20D EMA", f"{df['EMA20'].iloc[-1]:.2f}")
    col2.metric("50D EMA", f"{df['EMA50'].iloc[-1]:.2f}")
    col3.metric("200D EMA", f"{df['EMA200'].iloc[-1]:.2f}")
    col4.metric("ATR (Volatility)", f"{df['ATR'].iloc[-1]:.2f}")

    # CANDLESTICK CHART
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='20 EMA', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='50 EMA', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA200'], name='200 EMA', line=dict(color='red')))
    
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"Nexus Core status: {regime} regime active based on current price action. Psychology: Neutral/Bullish.")
