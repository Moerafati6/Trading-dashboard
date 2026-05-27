import streamlit as st
import requests

# --- CONFIGURATION ---
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
# Paste your LONG anon public key here (between the quotes)
SUPABASE_KEY = "]eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjampibXRqb3V1bmRwc2J5Y3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4NTMzNjYsImV4cCI6MjA5NTQyOTM2Nn0.FpkwT9sHXnT-Qj1v7c5ETFj9sKmAOal4oXsnWxfhyCk"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

# --- PAGE SETUP ---
st.set_page_config(page_title="Nexus Terminal", layout="wide")
st.title("Nexus Quantitative Terminal")

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- AUTHENTICATION LOGIC ---
if not st.session_state.authenticated:
    st.sidebar.header("Authentication")
    user_passkey = st.sidebar.text_input("Enter Passkey", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        # This query hits your premium_keys table directly
        db_query = f"{SUPABASE_URL}/rest/v1/premium_keys?key_string=eq.{user_passkey}&is_active=eq.true"
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
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
                st.error(f"Error {response.status_code}: Please check your API Key and RLS policy.")
        except Exception as e:
            st.error(f"Connection error: {e}")

    st.sidebar.markdown("---")
    st.sidebar.link_button("Purchase Premium Access", STRIPE_LINK)

# --- DASHBOARD CONTENT ---
if st.session_state.authenticated:
    st.success("Access Granted. Initializing Nexus Core...")
    st.line_chart([10, 20, 15, 30, 45, 40])
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()
