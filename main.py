from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/signals")
async def get_signals(ticker: str):
    try:
        # Fetch data with safety checks
        df = yf.download(ticker.upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 200: 
            raise HTTPException(status_code=400, detail="Insufficient data for ticker.")
        
        # Calculate indicators
        data = df.tail(60).copy()
        data["MA20"] = df["Close"].rolling(20).mean().tail(60)
        data["MA50"] = df["Close"].rolling(50).mean().tail(60)
        data["MA200"] = df["Close"].rolling(200).mean().tail(60)
        
        # Behavioral/Systematic Metrics
        recent = df.tail(30)
        psych = round(((df['Close'].iloc[-1] - recent['Low'].min()) / (recent['High'].max() - recent['Low'].min())) * 100, 0)
        sharpe = round((df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252), 2)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        
        regime = "BULL" if df['Close'].iloc[-1] > df['Close'].rolling(200).mean().iloc[-1] else "BEAR"
        action = "HOLD LONG" if regime == "BULL" else "HOLD SHORT"
        
        return {
            "regime": regime, "action": action, "psych_score": psych,
            "psych_meaning": "Greed (Tighten Stops)" if psych >= 75 else "Panic (Accumulate)" if psych <= 25 else "Neutral Flow",
            "sharpe": sharpe, "volatility": vol,
            "chart_data": data.to_dict(orient='list')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
