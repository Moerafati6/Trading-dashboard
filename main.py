from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/signals")
async def get_signals(ticker: str):
    try:
        # Download 2 years of data to ensure we have enough for a 200-day MA
        df = yf.download(ticker.upper(), period="2y", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 200:
            return {"error": "Insufficient data"}
        
        # Calculate Indicators (Ensure we use .iloc[-1] to get single values)
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(200).mean().iloc[-1])
        
        # Metrics
        recent = df.tail(30)
        psych = round(((last_close - float(recent['Low'].min())) / 
                       (float(recent['High'].max()) - float(recent['Low'].min()))) * 100, 0)
        sharpe = round((df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252), 2)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        # Logic with single values (prevents "Series ambiguous" error)
        regime = "BULL" if last_close > ma200 else "BEAR"
        action = "HOLD LONG" if (regime == "BULL" and last_close > ma20) else "HOLD SHORT"
        
        # Data for chart
        chart_data = df.tail(60).copy()
        chart_data["MA20"] = df['Close'].rolling(20).mean().tail(60)
        chart_data["MA50"] = df['Close'].rolling(50).mean().tail(60)
        chart_data["MA200"] = df['Close'].rolling(200).mean().tail(60)
        
        return {
            "regime": regime, "action": action, "psych_score": float(psych),
            "psych_meaning": "Greed" if psych >= 75 else "Panic" if psych <= 25 else "Neutral",
            "sharpe": float(sharpe), "volatility": float(vol), "perf": float(perf),
            "chart_data": chart_data.to_dict(orient='list')
        }
    except Exception as e:
        return {"error": str(e)}
