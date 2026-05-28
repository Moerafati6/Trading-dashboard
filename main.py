from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    return ["NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    ticker = ticker.strip().upper()
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": f"Ticker '{ticker}' not found"}
        
        # Scalar extraction: .iloc[-1] forces the Series into a single value
        last_close = float(df['Close'].iloc[-1])
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        ma20 = float(df['Close'].rolling(20, min_periods=1).mean().iloc[-1])
        
        recent = df.tail(30)
        low_val = float(recent['Low'].min())
        high_val = float(recent['High'].max())
        
        psych = round(((last_close - low_val) / (high_val - low_val + 0.01)) * 100, 0)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        return {
            "ticker": ticker,
            "regime": "BULLISH" if last_close > ma200 else "BEARISH",
            "action": "HOLD LONG" if (last_close > ma200 and last_close > ma20) else "HOLD SHORT",
            "psych_score": float(psych),
            "psych_meaning": "GREED" if psych >= 75 else "PANIC" if psych <= 25 else "NEUTRAL",
            "price": last_close,
            "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list')
        }
    except Exception as e:
        return {"error": str(e)}
