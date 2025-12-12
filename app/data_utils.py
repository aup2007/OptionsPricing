import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st

# @st.cache_data
def fetch_underlying_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            return data['Close'].iloc[-1]
    except Exception:
        pass
    return None

@st.cache_data
def fetch_historical_prices(ticker, period="1y"):
    try:
        data = yf.Ticker(ticker).history(period=period)
        return data['Close']
    except Exception:
        return pd.Series()

def compute_historical_volatility(prices):
    if len(prices) < 2:
        return 0.0
    log_returns = np.log(prices / prices.shift(1))
    daily_vol = log_returns.std()
    return daily_vol * np.sqrt(252)

@st.cache_data
def fetch_options_chain(ticker, expiry):
    """Returns calls_df, puts_df for a specific expiry."""
    try:
        tk = yf.Ticker(ticker)
        chain = tk.option_chain(expiry)
        return chain.calls, chain.puts
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

@st.cache_data
def get_expirations(ticker):
    try:
        return yf.Ticker(ticker).options
    except Exception:
        return []