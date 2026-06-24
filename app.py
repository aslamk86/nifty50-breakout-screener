import streamlit as st
import yfinance as yf
import pandas as pd

# Set up page layout
st.set_page_config(page_title="Nifty 50 Institutional Breakout Screener", layout="wide")
st.title("🔥 Nifty 50 High-Volume Breakout Screener")
st.write("Scans for stocks breaking 20-day resistance with institutional volume confirmation (>1.5x average).")

# List of Nifty 50 tickers with .NS suffix for Yahoo Finance
NIFTY_50_TICKERS = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "ZEEL.NS"
]

@st.cache_data(ttl=1800)  # Caches data for 30 minutes
def check_high_volume_breakouts():
    breakout_stocks = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(NIFTY_50_TICKERS):
        status_text.text(f"Scanning {ticker}...")
        progress_bar.progress((idx + 1) / len(NIFTY_50_TICKERS))
        
        try:
            # Fetch 3 months of daily historical data
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo")
            
            if len(df) < 21:
                continue
                
            current_close = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            # Historical baselines (excluding the live/current day)
            historical_df = df.iloc[:-1]
            resistance_20d = historical_df['High'].tail(20).max()
            avg_volume_20d = historical_df['Volume'].tail(20).mean()
            
            # Trend context: 50-day EMA
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            ema_50 = df['EMA50'].iloc[-1]
            
            # STRICT FILTER CONDITIONS
            is_breaking_resistance = current_close >= resistance_20d
            is_high_volume = current_volume >= (avg_volume_20d * 1.5)
            is_bullish_trend = current_close > ema_50
            
            # All 3 conditions must be met to show up
            if is_breaking_resistance and is_high_volume and is_bullish_trend:
                volume_mult = current_volume / avg_volume_20d
                breakout_stocks.append({
                    "Ticker": ticker.replace(".NS", ""),
                    "Current Price (₹)": round(current_close, 2),
                    "20D Resistance (₹)": round(resistance_20d, 2),
                    "Volume Multiplier": f"{round(volume_mult, 2)}x",
                    "Trend (vs 50 EMA)": "Bullish"
                })
        except Exception as e:
            pass
            
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(breakout_stocks)

# UI Execution Button
if st.button("🔥 Scan for High Volume Breakouts"):
    results_df = check_high_volume_breakouts()
    
    if not results_df.empty:
        st.success(f"Found {len(results_df)} institutional-grade breakout setups!")
        
        # Format table for visual pop
        def highlight_strong_volume(val):
            try:
                mult = float(val.replace('x', ''))
                if mult >= 3.0:  # Hyper-volume alert
                    return 'background-color: #1e8449; color: white; font-weight: bold;'
                return 'background-color: #2ecc71; color: black;'
            except:
                return ''
                
        styled_df = results_df.style.applymap(highlight_strong_volume, subset=['Volume Multiplier'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No Nifty 50 stocks are clearing major resistance on high volume today.")
