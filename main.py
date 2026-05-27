from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

cache = {}

@app.get("/signals")
async def get_signals(ticker: str):
    ticker = ticker.upper()
    now = time.time()
    
    # Return cached data if less than 5 minutes old to avoid rate limits
    if ticker in cache and (now - cache[ticker][0]) < 300:
        return cache[ticker][1]

    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": "Ticker not found"}
        
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20, min_periods=1).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        
        recent = df.tail(30)
        psych = round(((last_close - float(recent['Low'].min())) / (float(recent['High'].max()) - float(recent['Low'].min()) + 0.01)) * 100, 0)
        sharpe = round((df['Close'].pct_change().mean() / df['Close'].pct_change().std()) * np.sqrt(252), 2)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        regime = "BULL" if last_close > ma200 else "BEAR"
        
        data = {
            "regime": regime,
            "action": "HOLD LONG" if (regime == "BULL" and last_close > ma20) else "HOLD SHORT",
            "psych_score": float(psych),
            "psych_meaning": "Greed" if psych >= 75 else "Panic" if psych <= 25 else "Neutral",
            "sharpe": float(sharpe),
            "volatility": float(vol),
            "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list')
        }
        cache[ticker] = (now, data)
        return data
    except Exception as e:
        return {"error": str(e)}
