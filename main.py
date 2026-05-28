from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/market_movers")
def get_movers():
    return ["NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
async def get_signals(ticker: str):
    try:
        df = yf.download(ticker.upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return {"error": "Ticker not found"}
        
        # FIX: Force scalar extraction using .iloc[-1]
        last_close = float(df['Close'].iloc[-1])
        ma20 = float(df['Close'].rolling(20, min_periods=1).mean().iloc[-1])
        ma200 = float(df['Close'].rolling(200, min_periods=1).mean().iloc[-1])
        
        return {
            "regime": "BULL" if last_close > ma200 else "BEAR",
            "action": "LONG" if (last_close > ma200 and last_close > ma20) else "SHORT",
            "price": last_close
        }
    except Exception as e:
        return {"error": str(e)}
