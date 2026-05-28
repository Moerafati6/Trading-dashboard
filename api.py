from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Nexus API running"}

@app.get("/market_movers")
def get_movers():
    return ["SELECT TICKER", "NVDA", "AMD", "AVGO", "TSM", "MSFT"]

@app.get("/signals")
def get_signals(ticker: str):
    try:
        ticker = ticker.upper().strip()

        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return {"error": "Ticker not found"}

        close = df["Close"]
        ma200 = close.rolling(200).mean()

        latest_close = float(close.iloc[-1])
        latest_ma200 = float(ma200.iloc[-1])

        regime = "BULLISH" if latest_close > latest_ma200 else "BEARISH"

        return {
            "ticker": ticker,
            "regime": regime,
            "psych_score": 78,
            "psych_meaning": "GREED",
            "annual_return": 12.4,
            "chart_data": {
                "Open": df["Open"].tail(60).astype(float).tolist(),
                "High": df["High"].tail(60).astype(float).tolist(),
                "Low": df["Low"].tail(60).astype(float).tolist(),
                "Close": df["Close"].tail(60).astype(float).tolist(),
            },
        }

    except Exception as e:
        return {"error": str(e)}
