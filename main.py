from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI(title="Behavioral Finance & Systematic Quant Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_signals(tickers, mode_name):
    assets_summary = []
    total_return = 0.0
    valid_assets_count = 0
    
    # Matching your exact notebook multi-moving-average parameters
    atr_multiplier = 2.0 if mode_name == "consistent" else 1.5
    
    for ticker in tickers:
        try:
            # Pull 2 years of daily data to remove lookahead bias and compute true multi-day moving averages
            df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True, progress=False)
            if df.empty or len(df) < 200:
                continue
                
            # Flatten structures
            data = pd.DataFrame(index=df.index)
            data["Open"] = df["Open"].values.flatten()
            data["High"] = df["High"].values.flatten()
            data["Low"] = df["Low"].values.flatten()
            data["Close"] = df["Close"].values.flatten()
            
            # Replicating your core multi-timeframe moving average matrix
            data["MA5"] = data["Close"].rolling(5).mean()
            data["MA10"] = data["Close"].rolling(10).mean()
            data["MA20"] = data["Close"].rolling(20).mean()
            data["MA50"] = data["Close"].rolling(50).mean()
            data["MA200"] = data["Close"].rolling(200).mean()
            
            # Volatility Envelope (True Average True Range calculation)
            hl = data['High'] - data['Low']
            hc = np.abs(data['High'] - data['Close'].shift())
            lc = np.abs(data['Low'] - data['Close'].shift())
            data['ATR'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean()
            data = data.dropna()
            
            current_price = round(float(data['Close'].iloc[-1]), 2)
            
            # 1. Market Psychology / Trend Regime Mapping
            # Close vs MA200 defines institutional sentiment macro cycles (BULL/BEAR herd behavior)
            last_row = data.iloc[-1]
            regime = "BULL" if last_row["Close"] > last_row["MA200"] else "BEAR"
            
            # Fast/Slow confluences map short-term retail momentum vs medium-term accumulation
            fast_signal = 1 if last_row["MA5"] > last_row["MA20"] else -1
            slow_signal = 1 if last_row["MA10"] > last_row["MA50"] else -1
            
            # 2. Execution Triggers matching your exact script rules
            if regime == "BULL" and slow_signal == 1 and fast_signal == 1:
                action = "HOLD LONG"
            elif regime == "BEAR" and slow_signal == -1 and fast_signal == -1:
                action = "HOLD SHORT"
            else:
                action = "WAIT / NO SIGNAL"
                
            # 3. Dynamic Volatility Stops
            atr_val = last_row["ATR"]
            if "LONG" in action:
                stop_level = round(current_price - (atr_val * atr_multiplier), 2)
            else:
                stop_level = round(current_price + (atr_val * atr_multiplier), 2)
                
            # 4. Legitimate Historical Backtest Simulation Loop (No Lookahead Bias)
            data['Strategy_Return'] = 0.0
            pos, entry, trades = 0, 0, []
            
            for i in range(1, len(data) - 1):
                price_today = data["Close"].iloc[i]
                atr_today = data["ATR"].iloc[i]
                curr = data.iloc[i]
                next_open = data["Open"].iloc[i+1]
                
                # Check for alignment across MAs
                reg_status = 1 if curr["Close"] > curr["MA200"] else -1
                f_status = 1 if curr["MA5"] > curr["MA20"] else -1
                s_status = 1 if curr["MA10"] > curr["MA50"] else -1
                
                if pos == 0:
                    if reg_status == 1 and s_status == 1 and f_status == 1:
                        pos, entry = 1, next_open
                    elif reg_status == -1 and s_status == -1 and f_status == -1:
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
            
            # Annualized Sharpe Ratio calculation from historical volatility
            daily_mean = data['Strategy_Return'].mean()
            daily_std = data['Strategy_Return'].std()
            sharpe_ratio = round((daily_mean / daily_std) * np.sqrt(252), 2) if daily_std > 0 else 0.0
            
            total_return += actual_return_pct
            valid_assets_count += 1
            
            assets_summary.append({
                "ticker": ticker,
                "regime": regime,
                "action": action,
                "current_price": current_price,
                "stop_level": stop_level,
                "backtest_return_pct": actual_return_pct,
                "metrics_sharpe": sharpe_ratio
            })
        except Exception:
            continue
            
    avg_portfolio_return = round(total_return / valid_assets_count, 1) if valid_assets_count > 0 else 0.0
    
    return {
        "avg_portfolio_return_pct": avg_portfolio_return,
        "atr_stop_multiplier": atr_multiplier,
        "assets": assets_summary
    }

@app.get("/")
def root():
    return {"status": "online", "message": "Behavioral Finance Quant Engine Running Live."}

@app.get("/signals")
def get_signals(mode: str = "consistent"):
    mode_lower = mode.lower()
    
    # Pulling your exact notebook baskets verbatim
    if mode_lower == "consistent":
        tickers = ["TOST", "MU", "DOCS", "NOK", "WDC", "IBRX", "BE", "BTC-USD", "NVDA", "MSFT", "GLD", "CL=F", "SOFI"]
    else:
        tickers = ["BTC-USD", "XRP-USD", "SOL-USD", "DOGE-USD", "AAVE-USD", "AVAX-USD"]
        
    return calculate_signals(tickers, mode_lower)
