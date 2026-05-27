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
        # Use a more stable fetch method
        ticker_obj = yf.Ticker(ticker.upper())
        df = ticker_obj.history(period="1y")
        
        # Check if the dataframe is actually populated
        if df.empty or len(df) < 50:
            return {"error": "Ticker not found or data empty"}
        
        # Standardize calculations
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(window=20, min_periods=1).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(window=200, min_periods=1).mean().iloc[-1])
        
        # Calculate metrics using .iloc[-1] to ensure single values
        recent = df.tail(30)
        high = float(recent['High'].max())
        low = float(recent['Low'].min())
        psych = round(((last_close - low) / (high - low + 0.001)) * 100, 0)
        
        returns = df['Close'].pct_change().dropna()
        sharpe = round((returns.mean() / returns.std()) * np.sqrt(252), 2)
        vol = round(returns.std() * np.sqrt(252), 4)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        regime = "BULL" if last_close > ma200 else "BEAR"
        action = "HOLD LONG" if (regime == "BULL" and last_close > ma20) else "HOLD SHORT"
        
        return {
            "regime": regime,
            "action": action,
            "psych_score": float(psych),
            "sharpe": float(sharpe),
            "volatility": float(vol),
            "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list')
        }
    except Exception as e:
        return {"error": str(e)}
