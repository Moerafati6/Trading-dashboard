import streamlit as st
import requests

# 1. Configuration
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"

# 2. Page Setup
st.set_page_config(page_title="Nexus Terminal", layout="wide")
st.title("Nexus Quantitative Terminal")

# 3. Session State Management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 4. Authentication & Payment Sidebar
if not st.session_state.authenticated:
    st.sidebar.header("Authentication")
    user_passkey = st.sidebar.text_input("Enter Passkey", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        db_query = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}&is_active=eq.true"
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(db_query, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid or inactive access key.")
            else:
                st.error(f"Connection failed (Status {response.status_code})")
        except Exception as e:
            st.error(f"Connection error: {e}")

    # Stripe Payment Section
    st.sidebar.markdown("---")
    st.sidebar.write("Don't have an access key?")
    st.sidebar.link_button("Purchase Premium Access", "https://buy.stripe.com/YOUR_LINK_HERE")

# 5. Dashboard (Only shows if authenticated)
if st.session_state.authenticated:
    st.success("Access Granted. Initializing Nexus Core...")
    st.subheader("Market Data Feed")
    # Your premium content goes here
    st.line_chart([10, 20, 15, 30, 45, 40])
    st.write("Live signals active for premium members.")
    
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
