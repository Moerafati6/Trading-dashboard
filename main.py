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
        
        # .item() extracts the value, .tolist() converts the series to a standard list
        last_close = float(df['Close'].iloc[-1].item())
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1].item())
        
        return {
            "regime": "BULLISH" if last_close > ma200 else "BEARISH",
            "psych_score": 78.0, 
            "psych_meaning": "GREED",
            "perf": 124.0,
            "chart_data": {
                "Open": df['Open'].tail(60).astype(float).tolist(),
                "High": df['High'].tail(60).astype(float).tolist(),
                "Low": df['Low'].tail(60).astype(float).tolist(),
                "Close": df['Close'].tail(60).astype(float).tolist()
            }
        }
    except Exception as e:
        return {"error": str(e)}
