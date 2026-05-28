import streamlit as st

# 1. Page Configuration
st.set_page_config(layout="wide")

# 2. Simple UI Elements
st.title("Nexus Terminal - Debug Mode")

# 3. Test Sidebar
with st.sidebar:
    st.write("Sidebar is loading.")
    st.button("Test Button")

# 4. Simple check to see if secrets are readable (if this fails, it's a secret config issue)
try:
    if st.secrets.get("PASSKEY"):
        st.success("Secrets are loaded correctly.")
    else:
        st.warning("PASSKEY secret is missing.")
except Exception as e:
    st.error(f"Secret config error: {e}")

st.write("If you see this, the app is finally running without status 1.")
