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
        df = yf.download(ticker.upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 200: return {"error": "Insufficient data"}
        
        # Calculate indicators
        data = df.tail(60).copy()
        # Use .iloc[-1] to get the single latest value for comparisons
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(200).mean().iloc[-1])
        
        # Metrics
        recent = df.tail(30)
        psych = round(((last_close - float(recent['Low'].min())) / (float(recent['High'].max()) - float(recent['Low'].min()))) * 100, 0)
        sharpe = round((df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252), 2)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        regime = "BULL" if last_close > ma200 else "BEAR"
        action = "HOLD LONG" if (regime == "BULL" and last_close > ma20) else "HOLD SHORT"
        
        return {
            "regime": regime, "action": action, "psych_score": float(psych),
            "psych_meaning": "Greed (Tighten Stops)" if psych >= 75 else "Panic (Accumulate)" if psych <= 25 else "Neutral Flow",
            "sharpe": float(sharpe), "volatility": float(vol), "perf": float(perf),
            "chart_data": data.to_dict(orient='list')
        }
    except Exception as e:
        return {"error": str(e)}
