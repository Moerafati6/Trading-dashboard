from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
import stripe
from fastapi import Request
from supabase import create_client

warnings.filterwarnings("ignore")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

ASSET_MAP = {
    "SELECT ASSET": "",
    "NVDA": "NVDA",
    "AMD": "AMD",
    "AVGO": "AVGO",
    "TSM": "TSM",
    "MSFT": "MSFT",
    "AAPL": "AAPL",
    "TSLA": "TSLA",
    "MU": "MU",
    "SOFI": "SOFI",
    "ONDS": "ONDS",
    "DOCS": "DOCS",
    "GLD": "GLD",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "Avalanche": "AVAX-USD",
    "Aave": "AAVE-USD",
    "XRP": "XRP-USD",
    "Dogecoin": "DOGE-USD",
    "Crude Oil Futures": "CL=F",
    "Gold Futures": "GC=F",
    "Silver Futures": "SI=F",
    "Natural Gas Futures": "NG=F",
}

WATCHLIST = [
    "NVDA", "AMD", "MSFT", "AAPL", "TSLA", "MU",
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD",
    "GLD", "CL=F"
]


@app.get("/")
def home():
    return {"status": "Nexus API running"}
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            stripe_webhook_secret
        )
    except Exception as e:
        return {"error": str(e)}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        email = None

        if session.get("customer_details"):
            email = session["customer_details"].get("email")

        if not email:
            email = session.get("customer_email")

        if email:
            clean_email = email.strip().lower()

            supabase.table("subscribers").upsert({
                "email": clean_email,
                "status": "active"
            }).execute()

    return {"status": "success"}

@app.get("/market_movers")
def get_movers():
    return list(ASSET_MAP.keys())


def run_engine(ticker: str, mode: str = "consistent"):
    raw_ticker = ticker.strip()
    yf_ticker = ASSET_MAP.get(raw_ticker, raw_ticker).upper()

    if yf_ticker == "":
        return {"error": "Choose or search an asset first."}

    atr_mult = 2.0 if mode == "consistent" else 1.5

    df = pd.DataFrame()

    for attempt in range(3):
        try:
            df = yf.download(
                yf_ticker,
                period="2y",
                interval="1d",
                auto_adjust=True,
                progress=False,
            )

            if not df.empty:
                break

        except Exception:
            pass

    if df.empty or len(df) < 220:
        return {"error": f"Data temporarily unavailable for {yf_ticker}. Try again in a few seconds."}

    data = pd.DataFrame(index=df.index)
    data["Open"] = np.ravel(df["Open"].values)
    data["High"] = np.ravel(df["High"].values)
    data["Low"] = np.ravel(df["Low"].values)
    data["Close"] = np.ravel(df["Close"].values)

    data["MA5"] = data["Close"].rolling(5).mean()
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA10"] = data["Close"].rolling(10).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["MA200"] = data["Close"].rolling(200).mean()

    hl = data["High"] - data["Low"]
    hc = abs(data["High"] - data["Close"].shift())
    lc = abs(data["Low"] - data["Close"].shift())
    data["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()

    data = data.dropna()

    data["regime"] = np.where(data["Close"] > data["MA200"], 1, -1)
    data["fast"] = np.where(data["MA5"] > data["MA20"], 1, -1)
    data["slow"] = np.where(data["MA10"] > data["MA50"], 1, -1)
    data["Strategy_Return"] = 0.0

    pos = 0
    entry = 0.0
    stop = 0.0
    trades = []

    for i in range(1, len(data) - 1):
        price_today = float(data["Close"].iloc[i])
        atr_today = float(data["ATR"].iloc[i])
        curr = data.iloc[i]
        next_open = float(data["Open"].iloc[i + 1])
        if pos == 0:
            if curr["regime"] == 1 and curr["slow"] == 1 and curr["fast"] == 1:
                pos = 1
                entry = next_open
                stop = next_open - (atr_today * atr_mult)

            elif curr["regime"] == -1 and curr["slow"] == -1 and curr["fast"] == -1:
                pos = -1
                entry = next_open
                stop = next_open + (atr_today * atr_mult)

        elif pos == 1:
            data.loc[data.index[i], "Strategy_Return"] = (
                data["Close"].iloc[i] / data["Close"].iloc[i - 1]
            ) - 1

            if price_today <= stop or curr["fast"] == -1:
                trades.append((price_today / entry) - 1)
                pos = 0

        elif pos == -1:
            data.loc[data.index[i], "Strategy_Return"] = 1 - (
                data["Close"].iloc[i] / data["Close"].iloc[i - 1]
            )

            if price_today >= stop or curr["fast"] == 1:
                trades.append((entry / price_today) - 1)
                pos = 0

    rets = pd.Series(trades)
    backtest_return = float((1 + rets).prod() - 1) if not rets.empty else 0.0

    daily_mean = float(data["Strategy_Return"].mean())
    daily_std = float(data["Strategy_Return"].std())
    sharpe = float((daily_mean / daily_std) * np.sqrt(252)) if daily_std > 0 else 0.0

    last = data.iloc[-1]
    price = float(last["Close"])
    atr = float(last["ATR"])
    
    prev_close = float(data["Close"].iloc[-2])
    daily_change = ((price / prev_close) - 1) * 100

    regime_name = "BULLISH" if last["regime"] == 1 else "BEARISH"

    alignment_score = 0
    if last["regime"] == 1:
        alignment_score += 30
    if last["slow"] == 1:
        alignment_score += 30
    if last["fast"] == 1:
        alignment_score += 25
    if sharpe > 0:
        alignment_score += 15

    short_alignment_score = 0
    if last["regime"] == -1:
        short_alignment_score += 30
    if last["slow"] == -1:
        short_alignment_score += 30
    if last["fast"] == -1:
        short_alignment_score += 25
    if sharpe > 0:
         short_alignment_score += 15


    if last["regime"] == 1 and last["slow"] == 1 and last["fast"] == 1:
        action = "LONG BIAS"
        confidence = min(100, alignment_score)
        stop_level = price - (atr * atr_mult)
        take_profit = price + (atr * atr_mult * 1.5)

    elif last["regime"] == -1 and last["slow"] == -1 and last["fast"] == -1:
        action = "SHORT BIAS"
        confidence = min(100, short_alignment_score)
        stop_level = price + (atr * atr_mult)
        take_profit = price - (atr * atr_mult * 1.5)

    else:
        action = "NEUTRAL/CHOPPY"
        confidence = max(alignment_score, short_alignment_score)
        stop_level = None
        take_profit = None
    confidence_breakdown = []

    if action == "LONG BIAS":
        if last["regime"] == 1:
            confidence_breakdown.append("Market Regime +30")
        if last["slow"] == 1:
            confidence_breakdown.append("Trend Alignment +30")
        if last["fast"] == 1:
            confidence_breakdown.append("Momentum +25")
        if sharpe > 0:
            confidence_breakdown.append("Risk Score +15")

    elif action == "SHORT BIAS":
        if last["regime"] == -1:
            confidence_breakdown.append("Market Regime +30")
        if last["slow"] == -1:
            confidence_breakdown.append("Trend Alignment +30")
        if last["fast"] == -1:
            confidence_breakdown.append("Momentum +25")
        if sharpe > 0:
            confidence_breakdown.append("Risk Score +15")

    else:
        if max(alignment_score, short_alignment_score) >= 30:
            confidence_breakdown.append("Partial Market Alignment")
        if sharpe > 0:
            confidence_breakdown.append("Positive Risk Score +15")
        confidence_breakdown.append("Mixed or choppy trend signals")

    asset_return = ((price / float(data["Close"].iloc[0])) - 1) * 100

    if action == "LONG BIAS":
        psych_score = 72
        psych_meaning = "GREED"
    elif action == "SHORT BIAS":
        psych_score = 31
        psych_meaning = "FEAR"
    elif asset_return > 40:
        psych_score = 82
        psych_meaning = "EUPHORIA"
    elif asset_return > 10:
        psych_score = 62
        psych_meaning = "OPTIMISM"
    elif asset_return > -15:
        psych_score = 45
        psych_meaning = "UNCERTAINTY"
    else:
        psych_score = 24
        psych_meaning = "PANIC"
    # ==========================
    # MA CROSSOVER DETECTION
    # ==========================
    recent = data.tail(90).copy()

    recent["fast_cross"] = recent["fast"].diff()

    bull_crosses = recent[recent["fast_cross"] == 2]
    bear_crosses = recent[recent["fast_cross"] == -2]

    crossovers = []

    for idx, row in bull_crosses.iterrows():
        crossovers.append({
            "date": idx.strftime("%Y-%m-%d"),
            "price": round(float(row["Close"]), 2),
            "type": "BULLISH CROSS"
        })

    for idx, row in bear_crosses.iterrows():
        crossovers.append({
           "date": idx.strftime("%Y-%m-%d"),
           "price": round(float(row["Close"]), 2),
           "type": "BEARISH CROSS"
        })
    
    
    confidence_reasons = []

    if last["regime"] == 1:
        confidence_reasons.append("Bullish long-term market regime")
    else:
        confidence_reasons.append("Bearish long-term market regime")

    if last["slow"] == 1:
        confidence_reasons.append("Trend confirmation is positive")
    else:
        confidence_reasons.append("Trend confirmation is negative")

    if last["fast"] == 1:
        confidence_reasons.append("Momentum is strengthening")
    else:
        confidence_reasons.append("Momentum is weakening")

    if sharpe > 0:
        confidence_reasons.append("Positive risk-adjusted performance")
    else:
        confidence_reasons.append("Weak risk-adjusted performance")
    return {
        "ticker": yf_ticker,
        "mode": mode.upper(),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "price": round(price, 2),
        "daily_change": round(daily_change, 2),
        "regime": regime_name,
        "action": action,
        "confidence": int(confidence),
        "confidence_breakdown": confidence_breakdown,
        "psych_score": psych_score,
        "psych_meaning": psych_meaning,
        "asset_return": round(float(asset_return), 2),
        "backtest_return": round(backtest_return * 100, 2),
        "sharpe": round(sharpe, 2),
        "atr": round(atr, 2),
        "stop_level": round(stop_level, 2) if stop_level else "N/A",
        "take_profit": round(take_profit, 2) if take_profit else "N/A",
        "chart_data": {
            "Date": [d.strftime("%Y-%m-%d") for d in recent.index],
            "Open": recent["Open"].astype(float).tolist(),
            "High": recent["High"].astype(float).tolist(),
            "Low": recent["Low"].astype(float).tolist(),
            "Close": recent["Close"].astype(float).tolist(),
            "MA5": recent["MA5"].astype(float).tolist(),
            "MA20": recent["MA20"].astype(float).tolist(),
            "MA10": recent["MA10"].astype(float).tolist(),
            "MA50": recent["MA50"].astype(float).tolist(),
            "MA200": recent["MA200"].astype(float).tolist(),
            "Crossovers": crossovers,
        },
    }


@app.get("/signals")
def get_signals(ticker: str, mode: str = "consistent"):
    try:
        return run_engine(ticker, mode)
    except Exception as e:
        return {"error": str(e)}


@app.get("/scanner")
def scanner(mode: str = "consistent", tickers: str = ""):
    results = []

    if tickers:
        scan_list = [
            t.strip().upper()
            for t in tickers.split(",")
            if t.strip()
        ]
    else:
        scan_list = WATCHLIST

    for ticker in scan_list:
        try:
            res = run_engine(ticker, mode)
            if "error" not in res:
                results.append({
                    "ticker": res["ticker"],
                    "action": res["action"],
                    "confidence": res["confidence"],
                    "regime": res["regime"],
                    "psychology": f'{res["psych_meaning"]} ({res["psych_score"]})',
                    "price": res["price"],
                    "atr": res["atr"],
                    "stop_level": res["stop_level"],
                    "take_profit": res["take_profit"],
                    "sharpe": res["sharpe"],
                    "backtest_return": res["backtest_return"],
                    "asset_return": res["asset_return"],
                })
        except Exception:
            pass

    results = sorted(
        results,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results

    for ticker in WATCHLIST:
        try:
            res = run_engine(ticker, mode)
            if "error" not in res:
                results.append({
                    "ticker": res["ticker"],
                    "action": res["action"],
                    "confidence": res["confidence"],
                    "regime": res["regime"],
                    "psychology": f'{res["psych_meaning"]} ({res["psych_score"]})',
                    "price": res["price"],
                    "atr": res["atr"],
                    "stop_level": res["stop_level"],
                    "take_profit": res["take_profit"],
                    "sharpe": res["sharpe"],
                    "backtest_return": res["backtest_return"],
                    "asset_return": res["asset_return"],
                })
        except Exception:
            pass

    results = sorted(results, key=lambda x: x["confidence"], reverse=True)

    return results
