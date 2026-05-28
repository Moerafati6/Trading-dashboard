from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    # Return 5 standard popular tickers
    return ["NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    # Strip whitespace and capitalize to prevent format errors
    ticker = ticker.strip().upper()
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty or len(df) < 50: return {"error": f"Insufficient data found for '{ticker}'"}
        
        # KEY FIXED LINE 1: Scalar extraction (.iloc[-1]) prevents Series ambiguity errors
        last_close = float(df['Close'].iloc[-1])
        
        # KEY FIXED LINE 2: We extract the single scalar mean value
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        
        # KEY FIXED LINE 3: The 20-day MA scalar is extracted
        ma20 = float(df['Close'].rolling(20, min_periods=1).mean().iloc[-1])
        
        # Calculate Psychology Score (Greed/Panic)
        recent = df.tail(30)
        low_val = float(recent['Low'].min())
        high_val = float(recent['High'].max())
        psych_score = round(((last_close - low_val) / (high_val - low_val + 0.01)) * 100, 0)
        
        # Calculate annualized volatility
        vol = round(df['Close'].pct_change().std() * np.sqrt(252), 4)
        
        # Calculate percentage performance (1-year return)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        return {
            "ticker_confirmed": ticker,
            "price": last_close,
            "regime": "BULL" if last_close > ma200 else "BEAR",
            "action": "HOLD LONG" if (last_close > ma200 and last_close > ma20) else "HOLD SHORT",
            "psych_score": float(psych_score),
            "psych_meaning": "Greed" if psych_score >= 75 else "Panic" if psych_score <= 25 else "Neutral",
            "volatility": float(vol),
            "perf": float(perf),
            "chart_data": df.tail(60).to_dict(orient='list')
        }
    except Exception as e:
        # Catch unexpected API errors
        return {"error": f"Engine Calculation Error: {str(e)}"}
