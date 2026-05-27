from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import requests

app = FastAPI(title="Nexus Quantitative Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_crowd_sentiment():
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"value": int(data['data'][0]['value']), "class": data['data'][0]['value_classification']}
    except: pass
    return {"value": 50, "class": "Neutral"}

def calculate_signals(tickers, mode_name):
    assets_summary = []
    atr_multiplier = 2.0 if mode_name == "consistent" else 1.5
    sentiment = get_crowd_sentiment()
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True, progress=False)
            if df.empty or len(df) < 200: continue
            
            data = pd.DataFrame(index=df.index)
            data["Open"] = df["Open"].values.flatten()
            data["High"] = df["High"].values.flatten()
            data["Low"] = df["Low"].values.flatten()
            data["Close"] = df["Close"].values.flatten()
            data["MA5"] = data["Close"].rolling(5).mean()
            data["MA20"] = data["Close"].rolling(20).mean()
            data["MA50"] = data["Close"].rolling(50).mean()
            data["MA200"] = data["Close"].rolling(200).mean()
            
            hl = data['High'] - data['Low']
            hc = np.abs(data['High'] - data['Close'].shift())
            lc = np.abs(data['Low'] - data['Close'].shift())
            data['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
            data = data.dropna()
            
            current_price = round(float(data['Close'].iloc[-1]), 2)
            regime = "BULL" if data['Close'].iloc[-1] > data['MA200'].iloc[-1] else "BEAR"
            
            fast_sig = 1 if data['MA5'].iloc[-1] > data['MA20'].iloc[-1] else -1
            slow_sig = 1 if data['MA20'].iloc[-1] > data['MA50'].iloc[-1] else -1
            
            action = "HOLD LONG" if (regime == "BULL" and slow_sig == 1 and fast_sig == 1) else ("HOLD SHORT" if (regime == "BEAR" and slow_sig == -1 and fast_sig == -1) else "WAIT")
            
            stop_val = data['Close'].iloc[-1] - (data['ATR'].iloc[-1] * atr_multiplier) if "LONG" in action else data['Close'].iloc[-1] + (data['ATR'].iloc[-1] * atr_multiplier)
            
            recent = data.tail(30)
            assets_summary.append({
                "ticker": ticker, "regime": regime, "action": action, 
                "current_price": current_price, "stop_level": round(float(stop_val), 2),
                "history": {"close": recent["Close"].tolist(), "stop_line": (recent["Close"] - (recent["ATR"] * atr_multiplier)).tolist()}
            })
        except: continue
    return {"sentiment_score": sentiment["value"], "assets": assets_summary}

@app.get("/signals")
def get_signals(mode: str = "consistent", ticker: str = None):
    mode_lower = mode.lower()
    # DYNAMIC LOGIC: If a user sends a ticker, use it. Otherwise, use defaults.
    if ticker:
        tickers = [ticker.upper()]
    else:
        tickers = ["TOST", "MU", "DOCS", "NOK", "WDC", "BTC-USD"] if mode_lower == "consistent" else ["BTC-USD", "XRP-USD", "SOL-USD"]
    return calculate_signals(tickers, mode_lower)
