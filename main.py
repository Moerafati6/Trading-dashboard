from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import requests

app = FastAPI(title="Nexus Institutional Quant Engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def calculate_metrics(data):
    # Psych Score (30-day relative strength)
    recent = data.tail(30)
    psych_score = round(((data['Close'].iloc[-1] - recent['Low'].min()) / (recent['High'].max() - recent['Low'].min())) * 100, 0)
    # Sharpe Ratio
    returns = data['Close'].pct_change().dropna()
    sharpe = round((returns.mean() / returns.std()) * np.sqrt(252), 2)
    # Return
    total_return = round(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100, 2)
    return psych_score, sharpe, total_return

@app.get("/signals")
def get_signals(ticker: str = "AAPL"):
    df = yf.download(ticker.upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
    if df.empty: return {"error": "Ticker not found"}
    
    data = pd.DataFrame(index=df.index)
    data["Open"], data["High"], data["Low"], data["Close"] = df["Open"], df["High"], df["Low"], df["Close"]
    data["MA200"] = data["Close"].rolling(200).mean()
    
    psych, sharpe, ret = calculate_metrics(data)
    regime = "BULL" if data['Close'].iloc[-1] > data['MA200'].iloc[-1] else "BEAR"
    
    return {
        "ticker": ticker.upper(), "regime": regime, "psych_score": psych,
        "sharpe": sharpe, "return_pct": ret, "current_price": round(float(data['Close'].iloc[-1]), 2),
        "history": data.tail(30)[["Close"]].to_dict(orient='list')
    }
