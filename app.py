import streamlit as st
import requests

# 1. Configuration
SUPABASE_URL = "https://acjjbmtjouundpsbycue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjamJtdGpvdXVuZHBzYnljdWUiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcxNTM4Nzc3NywiZXhwIjoyMDMwOTYzNzc3fQ.3tO-qj7ZJdOqfT-N0eL_aM5lJmO6nN4p9_P6_vS3B6k"
STRIPE_LINK = "https://buy.stripe.com/dRm6oAe2b98GeLWBMdcs800"

# 2. Page Setup
st.set_page_config(page_title="Nexus Terminal", layout="wide")
st.title("Nexus Quantitative Terminal")

# 3. Session State Management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 4. Authentication & Payment UI
if not st.session_state.authenticated:
    st.sidebar.header("Authentication")
    user_passkey = st.sidebar.text_input("Enter Passkey", type="password")
    
    if st.sidebar.button("Unlock Dashboard Interface"):
        # Corrected URL path for querying your Supabase table
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
                st.error(f"Connection failed: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

    st.sidebar.markdown("---")
    st.sidebar.write("Don't have an access key?")
    st.sidebar.link_button("Purchase Premium Access", STRIPE_LINK)

# 5. Protected Dashboard
if st.session_state.authenticated:
    st.success("Access Granted. Initializing Nexus Core...")
    st.write("Welcome to the Premium Quantitative Suite.")
    # Here you will eventually add your charts/data
    st.line_chart([10, 20, 15, 30, 45, 40])
