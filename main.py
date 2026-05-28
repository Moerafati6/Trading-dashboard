from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    # Return 5 aktuell hot market tickers
    return ["NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    # CRITICAL FIX 1: Explicit string cleaning before yfinance API call
    ticker = ticker.strip().upper()
    try:
        # Load enough data for a 200MA (1 year period works)
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": f"Ticker '{ticker}' not found"}
        
        # CRITICAL FIX 2: Explicit Scalar Extraction (forcing conversion to a single float)
        # Using .iloc[-1] to get the most recent valid single value.
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20, min_periods=1).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        
        # Calculate Psychology Score (Greed/Panic metric over 30 days)
        recent = df.tail(30)
        low_val = float(recent['Low'].min())
        high_val = float(recent['High'].max())
        
        # Calculate single scalar values for all output metrics
        psych = round(((last_close - low_val) / (high_val - low_val + 0.01)) * 100, 0)
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4) # Annualized volatility
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2) # Total period performance
        
        # The frontend expects these precise single-value metrics to populate the dashboard.
        return {
            "ticker_confirmed": ticker,
            "regime": "BULL" if last_close > ma200 else "BEAR",
            "action": "HOLD LONG" if (last_close > ma200 and last_close > ma20) else "HOLD SHORT",
            "psych_score": float(psych),
            "psych_meaning": "Greed" if psych >= 75 else "Panic" if psych <= 25 else "Neutral",
            "price": last_close,
            "volatility": float(vol),
            "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list') # Data for Plotly visualization
        }
    except Exception as e:
        return {"error": f"Internal Engine Error: {str(e)}"}
