```python
import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(
    page_title="Nexus Quantitative Engine",
    layout="wide"
)

# -----------------------------
# CUSTOM DARK STYLING
# -----------------------------

st.markdown("""
<style>

.stApp {
    background-color: #070b12;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 {
    color: white;
}

div[data-testid="stMetric"] {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

.stButton > button {
    background: #16a34a;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.6rem 1rem;
    font-weight: 700;
}

.stSelectbox label,
.stTextInput label {
    color: white !important;
}

div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
}

.stTextInput input {
    background-color: white !important;
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE
# -----------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.title("Nexus Terminal")

    if not st.session_state.auth:

        key = st.text_input(
            "Enter Passkey",
            type="password"
        )

        if st.button("Unlock"):

            if key == st.secrets.get("PASSKEY"):

                st.session_state.auth = True
                st.rerun()

            else:

                st.error("Wrong passkey")

        if st.button("Start 7-Day Free Trial"):

            st.session_state.auth = True
            st.rerun()

        st.link_button(
            "Subscribe ($29/mo)",
            "https://buy.stripe.com/7sY14g9LV4Sq1Za2nPcs801"
        )

    else:

        st.success("Access granted")

        if st.button("Logout"):

            st.session_state.auth = False
            st.rerun()

# -----------------------------
# MAIN PAGE
# -----------------------------

st.title("Nexus Quantitative Engine")

if not st.session_state.auth:

    st.info(
        "Enter passkey, start trial, or subscribe to access the terminal."
    )

    st.stop()

# -----------------------------
# API CONNECTION
# -----------------------------

base_url = st.secrets.get("API_BASE_URL")

if not base_url:

    st.error("Missing API_BASE_URL")

    st.stop()

# -----------------------------
# LOAD TICKERS
# -----------------------------

try:

    movers = requests.get(
        f"{base_url}/market_movers",
        timeout=10
    ).json()

except Exception as e:

    st.error(f"Backend connection failed: {e}")

    st.stop()

# -----------------------------
# TICKER SELECT
# -----------------------------

c1, c2 = st.columns(2)

choice = c1.selectbox(
    "Market Movers",
    movers
)

search = c2.text_input(
    "Or Search Ticker",
    placeholder="Example: NVDA"
)

ticker = search.upper().strip() if search else choice

# -----------------------------
# EXECUTE SCAN
# -----------------------------

if st.button("Execute Scan"):

    if ticker == "SELECT TICKER":

        st.warning("Choose a ticker first.")

        st.stop()

    try:

        res = requests.get(
            f"{base_url}/signals",
            params={"ticker": ticker},
            timeout=20
        ).json()

    except Exception as e:

        st.error(f"API request failed: {e}")

        st.stop()

    if "error" in res:

        st.error(res["error"])

        st.stop()

    # -----------------------------
    # METRICS
    # -----------------------------

    st.subheader(
        f"Quantitative Analysis for {res['ticker']}"
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Regime",
        res["regime"]
    )

    m2.metric(
        "Psych Score",
        f"{res['psych_meaning']} ({res['psych_score']})"
    )

    m3.metric(
        "Annual Return",
        f"{res['annual_return']}%"
    )

    # -----------------------------
    # CHART
    # -----------------------------

    fig = go.Figure(data=[

        go.Candlestick(
            open=res["chart_data"]["Open"],
            high=res["chart_data"]["High"],
            low=res["chart_data"]["Low"],
            close=res["chart_data"]["Close"],
            name=res["ticker"]
        )

    ])

    fig.update_layout(
        template="plotly_dark",
        height=550,
        paper_bgcolor="#070b12",
        plot_bgcolor="#111827",
        title=res["ticker"],
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
```
