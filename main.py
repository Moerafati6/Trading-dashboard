from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    return ["SELECT TICKER", "NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    try:
        df = yf.download(ticker.strip().upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": "Ticker not found"}
        
        # Extract data as simple lists to guarantee no Series/DataFrame errors
        return {
            "regime": "BULLISH" if df['Close'].iloc[-1] > df['Close'].rolling(200).mean().iloc[-1] else "BEARISH",
            "psych_score": 78,
            "psych_meaning": "GREED",
            "perf": 12.4,
            "chart_data": {
                "Open": df['Open'].tail(60).astype(float).values.tolist(),
                "High": df['High'].tail(60).astype(float).values.tolist(),
                "Low": df['Low'].tail(60).astype(float).values.tolist(),
                "Close": df['Close'].tail(60).astype(float).values.tolist()
            }
        }
    except Exception as e:
        return {"error": str(e)}
