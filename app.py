import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Nexus Quantitative Terminal", layout="wide")

# API Configuration
API_BASE_URL = "https://trading-dashboard-u7pl.onrender.com"
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLW8Mdcs800"
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"

# Session State
if "premium_access" not in st.session_state:
    st.session_state["premium_access"] = False

st.sidebar.title("🔐 Nexus Terminal")

# Authentication Logic
if not st.session_state["premium_access"]:
    st.sidebar.subheader("Premium Terminal Login")
    user_passkey = st.sidebar.text_input("Enter Your Premium Access Key", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        db_query = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}&is_active=eq.true"
        
        try:
            db_res = requests.get(db_query, headers=headers)
            if db_res.status_code == 200 and len(db_res.json()) > 0:
                record = db_res.json()[0]
                current_session = st.runtime.scriptrunner.script_run_context.get_script_run_context().session_id
                
                if record["session_id"] is None or record["session_id"] == current_session:
                    update_url = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}"
                    requests.patch(update_url, headers=headers, json={"session_id": current_session})
                    st.session_state["premium_access"] = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ Key active on another device.")
            else:
                st.sidebar.error("❌ Invalid Access Key.")
        except Exception:
            st.sidebar.error("⚠️ Connection error.")

    st.title("📊 Collective Market Psychology (Public Tier)")
    st.markdown("Broad retail sentiment indexes monitored across global crowds.")
    
    # Simple sentiment fetch
    try:
        res = requests.get(f"{API_BASE_URL}/signals?mode=consistent", timeout=10)
        if res.status_code == 200:
            p = res.json()
            st.metric("Global Crowd Sentiment", f"{p.get('sentiment_score', 50)} / 100")
            st.progress(p.get('sentiment_score', 50) / 100)
    except:
        st.info("Backend warming up...")

    st.markdown("---")
    st.markdown(f"""
    ### 🚀 Unlock the Nexus Quantitative Suite
    Gain direct visibility into institutional trend regimes and dynamic risk boundaries.
    
    👉 **[Click Here to Subscribe to Nexus Quantitative via Stripe]({STRIPE_PAYMENT_LINK})**
    
    *After subscribing, check your email for your unique access key.*
    """)

else:
    # Full Authenticated Terminal
    if st.sidebar.button("Logout"):
        st.session_state["premium_access"] = False
        st.rerun()

    st.title("🧠 Nexus Quantitative Terminal")
    mode = st.sidebar.selectbox("Risk Profile", ["Consistent", "Aggressive"])
    
    if st.sidebar.button("Execute Data Sync"):
        st.cache_data.clear()

    try:
        res = requests.get(f"{API_BASE_URL}/signals?mode={mode.lower()}", timeout=15)
        if res.status_code == 200:
            payload = res.json()
            df_assets = pd.DataFrame(payload['assets'])
            
            st.subheader("⚡ Systematic Asset Matrix")
            st.dataframe(df_assets, use_container_width=True)
            
            target = st.selectbox("Select Asset to Map", df_assets["ticker"].tolist())
            hist = df_assets[df_assets["ticker"] == target].iloc[0]["history"]
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=hist["dates"], open=hist["open"], high=hist["high"], low=hist["low"], close=hist["close"]))
            fig.add_trace(go.Scatter(x=hist["dates"], y=hist["stop_line"], line=dict(color="#FFFF00", dash="dot"), name="ATR Stop"))
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error("Terminal offline. Please wait 60 seconds for server wake-up.")
