import numpy as np
from scipy.stats import norm

def _d1_d2(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

def call_delta(S, K, T, r, sigma):
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return norm.cdf(d1)

def put_delta(S, K, T, r, sigma):
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return norm.cdf(d1) - 1

def gamma(S, K, T, r, sigma):
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

def vega(S, K, T, r, sigma):
    d1, _ = _d1_d2(S, K, T, r, sigma)
    return S * np.sqrt(T) * norm.pdf(d1) * 0.01  # Scaled for 1% change

def call_theta(S, K, T, r, sigma):
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
    return (term1 + term2) / 365.0  # Daily Theta

def put_theta(S, K, T, r, sigma):
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    term1 = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
    term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
    return (term1 + term2) / 365.0 # Daily Theta

def compute_all_greeks(S, K, T, r, sigma, option_type="call"):
    if option_type == "call":
        return {
            "Delta": call_delta(S, K, T, r, sigma),
            "Gamma": gamma(S, K, T, r, sigma),
            "Vega": vega(S, K, T, r, sigma),
            "Theta": call_theta(S, K, T, r, sigma)
        }
    else:
        return {
            "Delta": put_delta(S, K, T, r, sigma),
            "Gamma": gamma(S, K, T, r, sigma),
            "Vega": vega(S, K, T, r, sigma),
            "Theta": put_theta(S, K, T, r, sigma)
        }