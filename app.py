import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Systematic Trading Interface", layout="wide")

# =====================================================
# CONFIGURATION - CLEAN ROOT LINK ONLY
# =====================================================
API_BASE_URL = "https://4a39-34-124-211-137.ngrok-free.app"

st.title("⚡ Systematic Trading Engine Dashboard")
st.markdown("Real-time trend confluences, macro regimes, and dynamic ATR trailing stops.")
st.write("---")

selected_mode = st.selectbox("Select Active Portfolio Basket:", ["Aggressive", "Consistent"])

try:
    mode = selected_mode.lower()
    api_url = f"{API_BASE_URL}/signals?mode={mode}"
    
    response = requests.get(api_url, timeout=12)
    data = response.json()
    
    if "error" in data:
        st.error(f"Backend Processing Error: {data['error']}")
    else:
        # Safe metric extraction (prevents KeyError crashes)
        avg_return = data.get('avg_portfolio_return_pct', data.get('portfolio_average_return', '0.0'))
        atr_mult = data.get('atr_multiplier', data.get('atr_stop_multiplier', 'N/A'))
        assets_list = data.get('assets', [])
        
        # Render top metric summary cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Average Portfolio Return", value=f"{avg_return}%")
        with col2:
            st.metric(label="ATR Stop Multiplier", value=f"{atr_mult}x")
        with col3:
            st.metric(label="Total Tracked Assets", value=len(assets_list))
            
        st.write("###")
        st.subheader("🎯 Active Execution Signals")
        
        if assets_list:
            df = pd.DataFrame(assets_list)
            
            # Dynamically handle column alignment to prevent formatting crashes
            all_cols = df.columns.tolist()
            column_order = [c for c in ["ticker", "regime", "action", "current_price", "stop_level", "backtest_return_pct", "metrics_sharpe"] if c in all_cols]
            
            df = df[column_order]
            
            def highlight_matrix(val):
                if "LONG" in str(val):
                    return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif "SHORT" in str(val):
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
                elif "BULL" in str(val):
                    return 'color: #28a745; font-weight: bold;'
                elif "BEAR" in str(val):
                    return 'color: #dc3545; font-weight: bold;'
                return ''

            st.dataframe(df.style.applymap(highlight_matrix), use_container_width=True, height=450)
        else:
            st.info("No active assets found in this portfolio basket stream.")
        
except Exception as e:
    st.error("🔴 Connection Interrupted: Unable to contact the cloud trading engine server.")
    st.info("Ensure your Google Colab notebook cell is still actively running and hasn't timed out.")
