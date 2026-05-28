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
    return [
        "SELECT TICKER",
        "NVDA",
        "AMD",
        "AVGO",
        "TSM",
        "MSFT",
        "AAPL",
        "TSLA",
        "MU",
        "META",
        "GOOGL"
    ]

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

        open_prices = df["Open"].squeeze()
        high_prices = df["High"].squeeze()
        low_prices = df["Low"].squeeze()
        close_prices = df["Close"].squeeze()

        latest_close = float(close_prices.iloc[-1])
        first_close = float(close_prices.iloc[0])

        ma200 = close_prices.rolling(200).mean()
        latest_ma200 = float(ma200.iloc[-1])

        regime = (
            "BULLISH"
            if latest_close > latest_ma200
            else "BEARISH"
        )

        annual_return = round(
            ((latest_close / first_close) - 1) * 100,
            2
        )

        # PSYCHOLOGY ENGINE

        if annual_return > 40:
            psych_score = 82
            psych_meaning = "EUPHORIA"

        elif annual_return > 20:
            psych_score = 70
            psych_meaning = "GREED"

        elif annual_return > 0:
            psych_score = 55
            psych_meaning = "OPTIMISM"

        elif annual_return > -15:
            psych_score = 40
            psych_meaning = "FEAR"

        else:
            psych_score = 22
            psych_meaning = "PANIC"

        return {

            "ticker": ticker,
            "regime": regime,
            "psych_score": psych_score,
            "psych_meaning": psych_meaning,
            "annual_return": annual_return,

            "chart_data": {

                "Open": open_prices.tail(60).astype(float).tolist(),
                "High": high_prices.tail(60).astype(float).tolist(),
                "Low": low_prices.tail(60).astype(float).tolist(),
                "Close": close_prices.tail(60).astype(float).tolist(),

            },
        }

    except Exception as e:

        return {"error": str(e)}
