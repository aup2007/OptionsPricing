import numpy as np
from app.black_scholes import black_scholes_call, black_scholes_put

def monte_carlo_price(S, K, T, r, sigma, option_type='call', n_paths=10000, n_steps=252):
    dt = T / n_steps
    
    # 1. Simulate paths (Vectorized)
    Z = np.random.standard_normal((n_paths, n_steps))
    drift = (r - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt) * Z
    
    # Sum of log returns -> Cumsum
    log_returns = np.cumsum(drift + diffusion, axis=1)
    
    # Final prices
    ST = S * np.exp(log_returns[:, -1])
    
    # 2. Payoff
    if option_type == 'call':
        payoffs = np.maximum(ST - K, 0)
    else:
        payoffs = np.maximum(K - ST, 0)
        
    # 3. Discount
    price = np.exp(-r * T) * np.mean(payoffs)
    std_error = np.std(payoffs) / np.sqrt(n_paths)
    
    return price, std_error

def compare_mc_vs_bsm(S, K, T, r, sigma, option_type='call', n_paths=10000):
    mc_price, mc_err = monte_carlo_price(S, K, T, r, sigma, option_type, n_paths)
    
    if option_type == 'call':
        bsm_price = black_scholes_call(S, K, T, r, sigma)
    else:
        bsm_price = black_scholes_put(S, K, T, r, sigma)
        
    error = mc_price - bsm_price
    return bsm_price, mc_price, error