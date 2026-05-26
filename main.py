from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI(title="Systematic Trading Engine Backend")

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
    
    # Strategy risk parameters
    atr_multiplier = 1.5 if mode_name == "aggressive" else 2.5
    
    for ticker in tickers:
        try:
            # Pull a full 1-year window to calculate legitimate historical returns and risk metrics
            data = yf.Ticker(ticker).history(period="1y")
            if data.empty or len(data) < 20:
                continue
                
            current_price = round(float(data['Close'].iloc[-1]), 2)
            
            # 1. Trend Regime Logic (Close vs 5-Day Moving Average)
            ma5 = data['Close'].rolling(window=5).mean().iloc[-1]
            regime = "BULL" if current_price > ma5 else "BEAR"
            action = "LONG" if regime == "BULL" else "SHORT"
            
            # 2. Volatility Stop Logic (True Average True Range)
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            if action == "LONG":
                stop_level = round(current_price - (atr * atr_multiplier), 2)
            else:
                stop_level = round(current_price + (atr * atr_multiplier), 2)
            
            # 3. REAL Historical Performance Math (1-Year Asset Return)
            initial_price = data['Close'].iloc[0]
            actual_return_pct = round(((current_price - initial_price) / initial_price) * 100, 1)
            
            # 4. REAL Risk/Reward Math (Sharpe Ratio = Mean Return / Volatility)
            # Calculate daily percentage updates
            data['Daily_Return'] = data['Close'].pct_change()
            mean_return = data['Daily_Return'].mean()
            std_return = data['Daily_Return'].std()
            
            # Annualize the standard Sharpe formula (assuming 252 trading days and 0% risk-free rate)
            if std_return > 0:
                sharpe_ratio = round((mean_return / std_return) * np.sqrt(252), 2)
            else:
                sharpe_ratio = 0.0
                
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
    return {"status": "online", "message": "Systematic Quant Engine is running live on Render 24/7."}

@app.get("/signals")
def get_signals(mode: str = "aggressive"):
    mode_lower = mode.lower()
    if mode_lower == "consistent":
        tickers = ["ZTS", "MU", "AAPL", "MSFT", "GOOGL"]
    else:
        tickers = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"]
        
    return calculate_signals(tickers, mode_lower)
