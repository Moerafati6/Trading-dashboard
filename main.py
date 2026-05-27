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
        # Force download with a more generous period
        df = yf.download(ticker.upper(), period="2y", interval="1d", auto_adjust=True, progress=False)
        
        # Log the length to your Render console to debug
        print(f"DEBUG: Ticker {ticker} data length: {len(df)}")
        
        if df.empty:
            return {"error": "Ticker not found or no data returned"}
        
        # Fill missing values to keep indicators moving even with short history
        df = df.ffill()
        
        # Calculate indicators
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(window=20, min_periods=1).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(window=200, min_periods=1).mean().iloc[-1])
        
        # Metrics
        recent = df.tail(30)
        psych = round(((last_close - float(recent['Low'].min())) / (float(recent['High'].max()) - float(recent['Low'].min()) + 0.01)) * 100, 0)
        sharpe = round((df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252), 2)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        regime = "BULL" if last_close > ma200 else "BEAR"
        action = "HOLD LONG" if (regime == "BULL" and last_close > ma20) else "HOLD SHORT"
        
        return {
            "regime": regime, "action": action, "psych_score": float(psych),
            "psych_meaning": "Greed" if psych >= 75 else "Panic" if psych <= 25 else "Neutral",
            "sharpe": float(sharpe), "volatility": float(vol), "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list')
        }
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return {"error": str(e)}
