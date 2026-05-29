import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, timezone
from supabase import create_client

st.set_page_config(
    page_title="Nexus Quantitative Engine",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #060a12;
    color: #f8fafc;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #020617);
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

h1 {
    color: #f8fafc !important;
    font-size: 46px !important;
    font-weight: 900 !important;
}

h2, h3 {
    color: #f8fafc !important;
    font-weight: 900 !important;
}

label, p, span {
    color: #f8fafc !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #10203f, #172554);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #38bdf8;
    box-shadow: 0 0 22px rgba(56, 189, 248, 0.20);
}

div[data-testid="stMetricLabel"] {
    font-size: 15px !important;
    font-weight: 900 !important;
    color: #dbeafe !important;
}

div[data-testid="stMetricValue"] {
    font-size: 31px !important;
    font-weight: 950 !important;
    color: #ffffff !important;
}

.stButton > button {
    background: #22c55e;
    color: white !important;
    border-radius: 12px;
    border: none;
    padding: 0.75rem 1.2rem;
    font-weight: 900;
    font-size: 16px;
}

.stButton > button:hover {
    background: #16a34a;
    color: white !important;
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
    color: #f8fafc !important;
    font-weight: 900 !important;
}

.nexus-card {
    background: linear-gradient(135deg, #0f172a, #111827);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #334155;
    margin-bottom: 22px;
    color: #f8fafc;
    font-size: 17px;
}

.signal-box {
    background: linear-gradient(135deg, #052e16, #14532d);
    color: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #22c55e;
    font-size: 30px;
    font-weight: 950;
    text-align: center;
    margin-bottom: 22px;
    box-shadow: 0 0 30px rgba(34, 197, 94, 0.25);
}

.wait-box {
    background: linear-gradient(135deg, #422006, #713f12);
    color: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #f59e0b;
    font-size: 30px;
    font-weight: 950;
    text-align: center;
    margin-bottom: 22px;
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.25);
}

.short-box {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    color: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #ef4444;
    font-size: 30px;
    font-weight: 950;
    text-align: center;
    margin-bottom: 22px;
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.25);
}
a[data-testid="stLinkButton"] {
    background: #2563eb !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    border: 1px solid #60a5fa !important;
}

a[data-testid="stLinkButton"] p {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

supabase_url = st.secrets.get("SUPABASE_URL")
supabase_key = st.secrets.get("SUPABASE_KEY")

supabase = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)


def utc_now():
    return datetime.now(timezone.utc)


def start_trial(email):
    now = utc_now()
    expires = now + timedelta(days=7)

    existing = supabase.table("trials").select("*").eq("email", email).execute()

    if existing.data:
        trial = existing.data[0]
        expires_at = datetime.fromisoformat(trial["expires_at"].replace("Z", "+00:00"))

        if expires_at > now:
            return True, expires_at

        return False, expires_at

    supabase.table("trials").insert({
        "email": email,
        "started_at": now.isoformat(),
        "expires_at": expires.isoformat()
    }).execute()

    return True, expires


def check_trial(email):
    existing = supabase.table("trials").select("*").eq("email", email).execute()

    if not existing.data:
        return False, None

    trial = existing.data[0]
    expires_at = datetime.fromisoformat(trial["expires_at"].replace("Z", "+00:00"))

    return expires_at > utc_now(), expires_at

with st.sidebar:
    st.title("Nexus Terminal")
    st.caption("Quant.Rafati Signal Engine")

    if not st.session_state.auth:
        st.caption("Already subscribed? Enter your member passkey below.")

        key = st.text_input(
            "Member / Subscriber Passkey",
            type="password",
            key="sidebar_passkey"
        )

        if st.button("Unlock", key="sidebar_unlock"):
            if key == st.secrets.get("PASSKEY"):
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Wrong passkey")

        st.markdown("""
        <a href="https://buy.stripe.com/00w6oAaPZgB86fq1jLcs803" target="_blank">
            <button style="
                background:#ef4444;
                color:white;
                border:none;
                border-radius:12px;
                padding:12px 18px;
                font-weight:900;
                width:100%;
                cursor:pointer;
                font-size:16px;
                margin-top:10px;
            ">
                Subscribe ($29/mo)
            </button>
        </a>
        """, unsafe_allow_html=True)

    else:
        st.success("Access granted")

        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()
st.title("Nexus Quantitative Engine")

st.markdown("""
<div class="nexus-card">
<b>Premium systematic market scanner:</b><br>
Regime classification, MA5/MA20 fast confirmation, MA10/MA50 slow confirmation,
MA200 trend filter, ATR volatility stops, take-profit zones, confidence scoring,
psychology mapping, Sharpe ratio, and portfolio scanner.
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="nexus-card">
<b>How to use Nexus:</b><br><br>
1. Use <b>Execute Nexus Scan</b> to analyze one asset like AAPL, NVDA, BTC-USD, or CL=F.<br>
2. Review the action signal, confidence score, regime, ATR stop, take-profit level, and chart.<br>
3. Use <b>Portfolio Scanner</b> below to build your own watchlist and scan multiple assets at once.<br>
4. Green crosses show bullish moving-average crosses. Red X marks bearish crosses.<br><br>
This tool is for systematic market analysis, not financial advice.
</div>
""", unsafe_allow_html=True)

if not st.session_state.auth:
    st.info("Start a free trial or subscribe to access the Nexus Terminal.")
    st.markdown("### Already a member?")
main_key = st.text_input("Member / Subscriber Passkey", type="password", key="main_passkey")

if st.button("Unlock Member Access", key="main_unlock"):
    if main_key == st.secrets.get("PASSKEY"):
        st.session_state.auth = True
        st.rerun()
    else:
        st.error("Wrong passkey")

    email_main = st.text_input("Email for 7-Day Free Trial", key="main_trial_email")

    cta1, cta2 = st.columns(2)

    with cta1:
        if st.button("Start 7-Day Free Trial", key="main_trial_button"):
            if not supabase:
                st.error("Trial system is not connected yet.")
            elif not email_main:
                st.error("Enter your email first.")
            else:
                active, expires_at = start_trial(email_main.strip().lower())

                if active:
                    st.session_state.auth = True
                    st.session_state.user_email = email_main.strip().lower()
                    st.success(f"Trial active until {expires_at.strftime('%b %d, %Y')}")
                    st.rerun()
                else:
                    st.error("Your free trial has expired. Subscribe to continue.")

    with cta2:
        st.markdown("""
        <a href="https://buy.stripe.com/00w6oAaPZgB86fq1jLcs803" target="_blank">
            <button style="
                background:#ef4444;
                color:white;
                border:none;
                border-radius:12px;
                padding:12px 18px;
                font-weight:900;
                width:100%;
                cursor:pointer;
                font-size:16px;
                margin-top:28px;
            ">
                Subscribe ($29/mo)
            </button>
        </a>
        """, unsafe_allow_html=True)

    st.stop()

base_url = st.secrets.get("API_BASE_URL")

if not base_url:
    st.error("Missing API_BASE_URL")
    st.stop()

try:
    movers = requests.get(f"{base_url}/market_movers", timeout=10).json()
except Exception as e:
    st.error(f"Backend connection failed: {e}")
    st.stop()

top1, top2, top3 = st.columns([1.25, 1.25, 0.7])

choice = top1.selectbox("Popular Assets", movers)
search = top2.text_input("Or Search Ticker", placeholder="Examples: NVDA, BTC-USD, CL=F")
mode = top3.radio("Mode", ["consistent", "aggressive"], horizontal=False)

ticker = search.upper().strip() if search else choice

if "portfolio_assets" not in st.session_state:
    st.session_state.portfolio_assets = ["AAPL", "NVDA", "MSFT", "BTC-USD", "ETH-USD"]

scan_col, portfolio_col = st.columns([1, 1])

run_single = scan_col.button("Execute Nexus Scan")



if run_single:
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
    st.caption(f"Last Updated: {res.get('last_updated', 'N/A')}")

    if res["action"] == "ENTER LONG":
        st.markdown(f'<div class="signal-box">ACTION: {res["action"]} | CONFIDENCE: {res["confidence"]}%</div>', unsafe_allow_html=True)
    elif res["action"] == "ENTER SHORT":
        st.markdown(f'<div class="short-box">ACTION: {res["action"]} | CONFIDENCE: {res["confidence"]}%</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="wait-box">ACTION: {res["action"]} | CONFIDENCE: {res["confidence"]}%</div>', unsafe_allow_html=True)

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
    m10.metric("Asset Return", f'{res["asset_return"]}%')

    dates = res["chart_data"]["Date"]

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=dates,
        open=res["chart_data"]["Open"],
        high=res["chart_data"]["High"],
        low=res["chart_data"]["Low"],
        close=res["chart_data"]["Close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(x=dates, y=res["chart_data"]["MA5"], mode="lines", name="MA5"))
    fig.add_trace(go.Scatter(x=dates, y=res["chart_data"]["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=dates, y=res["chart_data"]["MA10"], mode="lines", name="MA10"))
    fig.add_trace(go.Scatter(x=dates, y=res["chart_data"]["MA50"], mode="lines", name="MA50"))
    fig.add_trace(go.Scatter(x=dates, y=res["chart_data"]["MA200"], mode="lines", name="MA200"))
    # ==========================
    # CROSSOVER MARKERS
    # ==========================

    bull_dates = []
    bull_prices = []
    bear_dates = []
    bear_prices = []

    for cross in res["chart_data"].get("Crossovers", []):

        if cross["type"] == "BULLISH CROSS":
            bull_dates.append(cross["date"])
            bull_prices.append(cross["price"])

        elif cross["type"] == "BEARISH CROSS":
            bear_dates.append(cross["date"])
            bear_prices.append(cross["price"])

    fig.add_trace(
        go.Scatter(
            x=bull_dates,
            y=bull_prices,
            mode="markers",
            name="Bull Cross",
            marker=dict(
                symbol="cross",
                size=16,
                color="#22c55e",
                line=dict(width=2, color="white")
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=bear_dates,
            y=bear_prices,
            mode="markers",
            name="Bear Cross",
            marker=dict(
                symbol="x",
                size=16,
                color="#ef4444",
                line=dict(width=2, color="white")
            )
        )
    )


    fig.update_layout(
        template="plotly_dark",
        height=680,
        paper_bgcolor="#060a12",
        plot_bgcolor="#0f172a",
        title=dict(
            text=f'{res["ticker"]} Price Action + Nexus Moving Average System',
            y=0.98,
            x=0.01,
            xanchor="left",
            yanchor="top"
        ),
        xaxis_title="Date",
        yaxis_title="Price",
        font=dict(color="#f8fafc", size=15),
        title_font=dict(color="#f8fafc", size=22),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="right",
            x=1,
            font=dict(color="#f8fafc", size=13)
        ),
        margin=dict(l=50, r=50, t=90, b=50),
        xaxis=dict(
            title_font=dict(color="#f8fafc", size=18),
            tickfont=dict(color="#f8fafc", size=14),
            gridcolor="rgba(248,250,252,0.20)"
        ),
        yaxis=dict(
            title_font=dict(color="#f8fafc", size=18),
            tickfont=dict(color="#f8fafc", size=14),
            gridcolor="rgba(248,250,252,0.20)"
        ),
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="nexus-card">
    <b>How to read this:</b><br>
    The engine uses MA200 for regime, MA10/MA50 for trend confirmation,
    MA5/MA20 for timing, ATR for volatility-based stop and take-profit zones,
    and confidence scoring to rank signal quality. This is not financial advice.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class="nexus-card">
<b>Portfolio Scanner</b><br>
Build your own watchlist, then scan multiple assets at once using the Nexus signal engine.
</div>
""", unsafe_allow_html=True)

portfolio_input = st.text_input(
    "Add assets to portfolio scanner",
    placeholder="Examples: AAPL, NVDA, BTC-USD, ETH-USD, CL=F"
)

add_col, clear_col, run_col = st.columns([1, 1, 1])

with add_col:
    if st.button("Add Assets"):
        new_assets = [
            t.strip().upper()
            for t in portfolio_input.split(",")
            if t.strip()
        ]

        for asset in new_assets:
            if asset not in st.session_state.portfolio_assets:
                st.session_state.portfolio_assets.append(asset)

        st.success("Assets added.")

with clear_col:
    if st.button("Clear Portfolio"):
        st.session_state.portfolio_assets = []
        st.warning("Portfolio cleared.")

with run_col:
    run_portfolio = st.button("Run Portfolio Scanner")

if st.session_state.portfolio_assets:
    st.write("Current Portfolio Scanner List:")
    st.code(", ".join(st.session_state.portfolio_assets))
else:
    st.info("No assets added yet.")

if run_portfolio:
    if not st.session_state.portfolio_assets:
        st.warning("Add at least one asset first.")
    else:
        try:
            scanner = requests.get(
                f"{base_url}/scanner",
                params={
                    "mode": mode,
                    "tickers": ",".join(st.session_state.portfolio_assets)
                },
                timeout=90
            ).json()

            if not scanner:
                st.warning("No scanner results returned.")
            else:
                st.subheader("Portfolio Scanner Results")

                df = pd.DataFrame(scanner)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.markdown("""
                <div class="nexus-card">
                <b>Scanner logic:</b> Your portfolio is ranked by signal confidence.
                Higher confidence means stronger alignment between regime, slow trend,
                fast timing, ATR risk structure, and risk-adjusted performance.
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Scanner failed: {e}")
