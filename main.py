from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def interpret_psych(score):
    if score >= 75: return "Greed/Overbought: Tighten Stops"
    if score <= 25: return "Panic/Oversold: Potential Support"
    return "Neutral Institutional Flow"

@app.get("/signals")
def get_signals(ticker: str = "AAPL"):
    df = yf.download(ticker.upper(), period="1y", interval="1d", auto_adjust=True, progress=False)
    if df.empty: return {"error": "Invalid Ticker"}
    
    data = pd.DataFrame(index=df.index)
    data[["Open", "High", "Low", "Close"]] = df[["Open", "High", "Low", "Close"]]
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["MA200"] = data["Close"].rolling(200).mean()
    
    recent = data.tail(30)
    psych = round(((data['Close'].iloc[-1] - recent['Low'].min()) / (recent['High'].max() - recent['Low'].min())) * 100, 0)
    sharpe = round((data['Close'].pct_change().mean() / data['Close'].pct_change().std()) * np.sqrt(252), 2)
    vol = round(data['Close'].pct_change().std() * np.sqrt(252), 4)
    ret_pct = round(((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100, 2)
    
    regime = "BULL" if data['Close'].iloc[-1] > data['MA200'].iloc[-1] else "BEAR"
    action = "HOLD LONG" if (regime == "BULL" and data['Close'].iloc[-1] > data['MA20'].iloc[-1]) else "HOLD SHORT"
    
    return {
        "ticker": ticker.upper(), "regime": regime, "action": action,
        "psych_score": psych, "psych_meaning": interpret_psych(psych),
        "sharpe": sharpe, "return_pct": ret_pct, "volatility": vol,
        "chart_data": data.tail(60).to_dict(orient='list')
    }
