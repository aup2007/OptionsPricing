import numpy as np
from scipy.stats import norm
import pandas as pd
from app.black_scholes import black_scholes_call, black_scholes_put

def implied_vol_solver(market_price, S, K, T, r, option_type='call'):
    """Newton-Raphson method to find Implied Volatility."""
    sigma = 0.5 # Initial guess
    tol = 1e-5
    max_iter = 100
    
    for i in range(max_iter):
        # Calculate Price and Vega
        if option_type == 'call':
            price = black_scholes_call(S, K, T, r, sigma)
        else:
            price = black_scholes_put(S, K, T, r, sigma)
            
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        vega = S * np.sqrt(T) * norm.pdf(d1)
        
        diff = market_price - price
        
        if abs(diff) < tol:
            return sigma
        
        if vega == 0:
            break
            
        sigma = sigma + diff / vega
        
    return np.nan # Failed to converge

def compute_iv_smile(ticker, expiry, S, r, option_type='call'):
    from app.data_utils import fetch_options_chain
    
    calls, puts = fetch_options_chain(ticker, expiry)
    df = calls if option_type == 'call' else puts
    
    if df.empty:
        return pd.DataFrame()
    
    # Calculate T (Time to expiry in years)
    T = (pd.to_datetime(expiry) - pd.Timestamp.now()).days / 365.0
    if T <= 0: T = 0.001
    
    smile_data = []
    
    for index, row in df.iterrows():
        K = row['strike']
        market_price = (row['bid'] + row['ask']) / 2 if (row['bid'] > 0 and row['ask'] > 0) else row['lastPrice']
        
        iv = implied_vol_solver(market_price, S, K, T, r, option_type)
        
        # Filter realistic IVs
        if 0.01 < iv < 3.0:
            smile_data.append({"strike": K, "market_price": market_price, "implied_vol": iv})
            
    return pd.DataFrame(smile_data)