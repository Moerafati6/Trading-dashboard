from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    # Added "SELECT TICKER" as the blank default option
    return ["SELECT TICKER", "NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    ticker = ticker.strip().upper()
    if ticker == "SELECT TICKER" or not ticker:
        return {"error": "Please select a valid ticker."}
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": f"Ticker '{ticker}' not found"}
        
        # Force conversion to float explicitly
        last_close = float(df['Close'].iloc[-1])
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        
        recent = df.tail(30)
        low_val = float(recent['Low'].min())
        high_val = float(recent['High'].max())
        
        psych = round(((last_close - low_val) / (high_val - low_val + 0.01)) * 100, 0)
        perf = round(((last_close / float(df['Close'].iloc[0])) - 1) * 100, 2)
        
        return {
            "ticker": ticker,
            "regime": "BULLISH" if last_close > ma200 else "BEARISH",
            "psych_score": float(psych),
            "psych_meaning": "GREED" if psych >= 75 else "PANIC" if psych <= 25 else "NEUTRAL",
            "perf": float(perf),
            "chart_data": {
                "Open": df['Open'].tail(60).astype(float).tolist(),
                "High": df['High'].tail(60).astype(float).tolist(),
                "Low": df['Low'].tail(60).tolist(),
                "Close": df['Close'].tail(60).tolist()
            }
        }
    except Exception as e:
        return {"error": str(e)}str(e)}
