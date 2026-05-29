import streamlit as st
import requests
import plotly.graph_objects as go

st.set_page_config(
    page_title="Nexus Quantitative Engine",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #060a12;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

h1 {
    color: white;
    font-size: 46px !important;
    font-weight: 900 !important;
}

h2, h3 {
    color: white;
    font-weight: 800 !important;
}

label, p, span {
    color: white !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #10203f, #172554);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #3b82f6;
    box-shadow: 0 0 18px rgba(59, 130, 246, 0.18);
}

div[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    font-weight: 800 !important;
    color: #dbeafe !important;
}

div[data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
}

.stButton > button {
    background: #22c55e;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.75rem 1.2rem;
    font-weight: 900;
    font-size: 16px;
}

.stButton > button:hover {
    background: #16a34a;
    color: white;
}

div[data-baseweb="select"] > div {
    background-color: white !important;
    color: black !important;
    border-radius: 10px !important;
}

.stTextInput input {
    background-color: white !important;
    color: black !important;
    border-radius: 10px !important;
}

.stSelectbox label,
.stTextInput label,
.stRadio label {
    color: white !important;
    font-weight: 800 !important;
}

.nexus-card {
    background: linear-gradient(135deg, #0f172a, #111827);
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #334155;
    margin-bottom: 20px;
}

.signal-box {
    background: linear-gradient(135deg, #052e16, #14532d);
    color: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #22c55e;
    font-size: 26px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 20px;
}

.wait-box {
    background: linear-gradient(135deg, #422006, #713f12);
    color: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #f59e0b;
    font-size: 26px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 20px;
}

.short-box {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    color: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #ef4444;
    font-size: 26px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth = False

with st.sidebar:
    st.title("Nexus Terminal")

    if not st.session_state.auth:
        key = st.text_input("Enter Passkey", type="password")

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

st.title("Nexus Quantitative Engine")

st.markdown("""
<div class="nexus-card">
<b>Quant.Rafati Signal Engine</b><br>
Regime classification, moving-average confirmation, ATR volatility stops, psychology mapping, backtest return, and Sharpe ratio.
</div>
""", unsafe_allow_html=True)

if not st.session_state.auth:
    st.info("Enter passkey, start trial, or subscribe to access the terminal.")
    st.stop()

base_url = st.secrets.get("API_BASE_URL")

if not base_url:
    st.error("Missing API_BASE_URL")
    st.stop()

try:
    movers = requests.get(
        f"{base_url}/market_movers",
        timeout=10
    ).json()
except Exception as e:
    st.error(f"Backend connection failed: {e}")
    st.stop()

top1, top2, top3 = st.columns([1.3, 1.3, 0.8])

choice = top1.selectbox(
    "Popular Assets",
    movers
)

search = top2.text_input(
    "Or Search Ticker",
    placeholder="Examples: NVDA, BTC-USD, CL=F"
)

mode = top3.radio(
    "Mode",
    ["consistent", "aggressive"],
    horizontal=False
)

ticker = search.upper().strip() if search else choice

if st.button("Execute Nexus Scan"):

    if ticker == "SELECT ASSET":
        st.warning("Choose or search an asset first.")
        st.stop()

    try:
        res = requests.get(
            f"{base_url}/signals",
            params={"ticker": ticker, "mode": mode},
            timeout=30
        ).json()
    except Exception as e:
        st.error(f"API request failed: {e}")
        st.stop()

    if "error" in res:
        st.error(res["error"])
        st.stop()

    st.subheader(f"Quantitative Analysis for {res['ticker']}")

    if res["action"] == "ENTER LONG":
        st.markdown(f'<div class="signal-box">ACTION: {res["action"]}</div>', unsafe_allow_html=True)
    elif res["action"] == "ENTER SHORT":
        st.markdown(f'<div class="short-box">ACTION: {res["action"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="wait-box">ACTION: {res["action"]}</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Regime", res["regime"])
    m2.metric("Psychology", f'{res["psych_meaning"]} ({res["psych_score"]})')
    m3.metric("Current Price", f'${res["price"]}')
    m4.metric("Mode", res["mode"])

    m5, m6, m7, m8 = st.columns(4)

    m5.metric("ATR", res["atr"])
    m6.metric("Stop Level", res["stop_level"])
    m7.metric("Take Profit", res["take_profit"])
    m8.metric("Sharpe", res["sharpe"])

    m9, m10 = st.columns(2)

    m9.metric("Strategy Backtest Return", f'{res["backtest_return"]}%')
    m10.metric("Asset Return", f'{res["annual_return"]}%')

    dates = res["chart_data"]["Date"]

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=res["chart_data"]["Open"],
            high=res["chart_data"]["High"],
            low=res["chart_data"]["Low"],
            close=res["chart_data"]["Close"],
            name="Price"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=res["chart_data"]["MA5"],
            mode="lines",
            name="MA5"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=res["chart_data"]["MA20"],
            mode="lines",
            name="MA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=res["chart_data"]["MA10"],
            mode="lines",
            name="MA10"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=res["chart_data"]["MA50"],
            mode="lines",
            name="MA50"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=res["chart_data"]["MA200"],
            mode="lines",
            name="MA200"
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=650,
        paper_bgcolor="#060a12",
        plot_bgcolor="#0f172a",
        title=f'{res["ticker"]} Price Action + Nexus Moving Average System',
        xaxis_title="Date",
        yaxis_title="Price",
        font=dict(size=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="nexus-card">
    <b>How to read this:</b><br>
    The engine uses MA200 for market regime, MA10/MA50 for slower confirmation,
    MA5/MA20 for faster signal timing, and ATR for volatility-based risk levels.
    This is not financial advice. It is a systematic market-analysis tool.
    </div>
    """, unsafe_allow_html=True)
