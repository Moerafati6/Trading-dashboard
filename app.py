import streamlit as st
import requests

# --- CONFIGURATION ---
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk" # Put your long key here
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nexus Terminal", layout="wide", page_icon="📈")
st.title("Nexus Quantitative Terminal")

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- SIDEBAR: AUTH & STRIPE ---
if not st.session_state.authenticated:
    st.sidebar.header("🔑 Authentication")
    user_passkey = st.sidebar.text_input("Enter Passkey", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        db_query = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}&is_active=eq.true"
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        
        try:
            response = requests.get(db_query, headers=headers)
            if response.status_code == 200 and len(response.json()) > 0:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid or inactive access key.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    st.sidebar.markdown("---")
    st.sidebar.write("### New User?")
    st.sidebar.link_button("Purchase Premium Access", STRIPE_LINK)
    st.sidebar.info("Gain access to Nexus Core signals and proprietary market data.")

# --- MAIN DASHBOARD (ONLY IF AUTHENTICATED) ---
if st.session_state.authenticated:
    st.success("Access Granted. Nexus Core Online.")
    
    # Psychological Indicators
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Sentiment", "Bullish", "+2.4%")
    col2.metric("Fear & Greed", "65", "Greed")
    col3.metric("Volume Analysis", "High", "Active")
    
    st.markdown("---")

    # Visual Data Layout
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Price Momentum")
        st.line_chart([10, 20, 15, 30, 45, 40])
    with c2:
        st.subheader("Order Flow Distribution")
        st.bar_chart([5, 10, 15, 20, 25])
        
    st.info("**Nexus Core Insight:** Momentum is holding above the 50-day moving average. Maintain cautious bullish bias.")
    
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
