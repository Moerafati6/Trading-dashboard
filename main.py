from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import requests

app = FastAPI(title="Behavioral Finance & Systematic Quant Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_crowd_sentiment():
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            return {"value": value, "class": classification}
    except Exception:
        pass
    return {"value": 50, "class": "Neutral"}

def calculate_signals(tickers, mode_name):
    assets_summary = []
    total_return = 0.0
    valid_assets_count = 0
    
    atr_multiplier = 2.0 if mode_name == "consistent" else 1.5
    sentiment = get_crowd_sentiment()
    
    for ticker in tickers:
        try:
            df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True, progress=False)
            if df.empty or len(df) < 200:
                continue
                
            data = pd.DataFrame(index=df.index)
            data["Open"] = df["Open"].values.flatten()
            data["High"] = df["High"].values.flatten()
            data["Low"] = df["Low"].values.flatten()
            data["Close"] = df["Close"].values.flatten()
            
            data["MA5"] = data["Close"].rolling(5).mean()
            data["MA10"] = data["Close"].rolling(10).mean()
            data["MA20"] = data["Close"].rolling(20).mean()
            data["MA50"] = data["Close"].rolling(50).mean()
            data["MA200"] = data["Close"].rolling(200).mean()
            
            hl = data['High'] - data['Low']
            hc = np.abs(data['High'] - data['Close'].shift())
            lc = np.abs(data['Low'] - data['Close'].shift())
            data['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
            data = data.dropna()
            
            current_price = round(float(data['Close'].iloc[-1]), 2)
            last_row = data.iloc[-1]
            
            regime = "BULL" if last_row["Close"] > last_row["MA200"] else "BEAR"
            fast_signal = 1 if last_row["MA5"] > last_row["MA20"] else -1
            slow_signal = 1 if last_row["MA10"] > last_row["MA50"] else -1
            
            if regime == "BULL" and slow_signal == 1 and fast_signal == 1:
                action = "HOLD LONG"
            elif regime == "BEAR" and slow_signal == -1 and fast_signal == -1:
                action = "HOLD SHORT"
            else:
                action = "WAIT / NO SIGNAL"
                
            # Compute rolling history array of the ATR stop line for visualization
            if "LONG" in action:
                data["Stop_History"] = data["Close"] - (data["ATR"] * atr_multiplier)
            else:
                data["Stop_History"] = data["Close"] + (data["ATR"] * atr_multiplier)
                
            stop_level = round(float(data["Stop_History"].iloc[-1]), 2)
            
            # Historical Simulation Loop (1-Year Backtest)
            data['Strategy_Return'] = 0.0
            pos, entry, trades = 0, 0, []
            
            for i in range(1, len(data) - 1):
                price_today = data["Close"].iloc[i]
                atr_today = data["ATR"].iloc[i]
                curr = data.iloc[i]
                next_open = data["Open"].iloc[i+1]
                
                r_status = 1 if curr["Close"] > curr["MA200"] else -1
                f_status = 1 if curr["MA5"] > curr["MA20"] else -1
                s_status = 1 if curr["MA10"] > curr["MA50"] else -1
                
                if pos == 0:
                    if r_status == 1 and s_status == 1 and f_status == 1:
                        pos, entry = 1, next_open
                    elif r_status == -1 and s_status == -1 and f_status == -1:
                        pos, entry = -1, next_open
                elif pos == 1:
                    data['Strategy_Return'].iloc[i] = (data['Close'].iloc[i] / data['Close'].iloc[i-1]) - 1
                    if price_today <= (entry - (atr_today * atr_multiplier)) or f_status == -1:
                        trades.append((price_today / entry) - 1)
                        pos = 0
                elif pos == -1:
                    data['Strategy_Return'].iloc[i] = 1 - (data['Close'].iloc[i] / data['Close'].iloc[i-1])
                    if price_today >= (entry + (atr_today * atr_multiplier)) or f_status == 1:
                        trades.append((entry / price_today) - 1)
                        pos = 0
                        
            actual_return_pct = round((((1 + pd.Series(trades)).prod() - 1) * 100), 1) if trades else 0.0
            
            daily_mean = data['Strategy_Return'].mean()
            daily_std = data['Strategy_Return'].std()
            sharpe_ratio = round((daily_mean / daily_std) * np.sqrt(252), 2) if daily_std > 0 else 0.0
            
            if regime == "BEAR" and sentiment["value"] <= 25:
                bias_insight = "Capitulation Phase: Crowd is panic selling into institutional support."
            elif regime == "BULL" and sentiment["value"] >= 75:
                bias_insight = "Retail FOMO: Mass overconfidence. Trailing stops should be tightened."
            else:
                bias_insight = f"Normal herd distribution in an institutional {regime} cycle."

            # Package up the last 30 intervals of timeline tracking points
            recent_data = data.tail(30)
            chart_history = {
                "dates": recent_data.index.strftime('%Y-%m-%d').tolist(),
                "open": recent_data["Open"].round(2).tolist(),
                "high": recent_data["High"].round(2).tolist(),
                "low": recent_data["Low"].round(2).tolist(),
                "close": recent_data["Close"].round(2).tolist(),
                "stop_line": recent_data["Stop_History"].round(2).tolist()
            }

            total_return += actual_return_pct
            valid_assets_count += 1
            
            assets_summary.append({
                "ticker": ticker,
                "regime": regime,
                "action": action,
                "current_price": current_price,
                "stop_level": stop_level,
                "backtest_return_pct": actual_return_pct,
                "metrics_sharpe": sharpe_ratio,
                "behavioral_bias": bias_insight,
                "history": chart_history
            })
        except Exception:
            continue
            
    avg_portfolio_return = round(total_return / valid_assets_count, 1) if valid_assets_count > 0 else 0.0
    
    return {
        "avg_portfolio_return_pct": avg_portfolio_return,
        "atr_stop_multiplier": atr_multiplier,
        "sentiment_score": sentiment["value"],
        "sentiment_class": sentiment["class"],
        "assets": assets_summary
    }

@app.get("/")
def root():
    return {"status": "online", "message": "Behavioral Finance Quant Engine Running Live."}

@app.get("/signals")
def get_signals(mode: str = "consistent"):
    mode_lower = mode.lower()
    if mode_lower == "consistent":
        tickers = ["TOST", "MU", "DOCS", "NOK", "WDC", "IBRX", "BE", "BTC-USD", "NVDA", "MSFT", "GLD", "CL=F", "SOFI"]
    else:
        tickers = ["BTC-USD", "XRP-USD", "SOL-USD", "DOGE-USD", "AAVE-USD", "AVAX-USD"]
        
    return calculate_signals(tickers, mode_lower)
