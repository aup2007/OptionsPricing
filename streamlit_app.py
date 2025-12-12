import streamlit as st
import numpy as np
import pandas as pd
import time
import random


# Import our modules
from app.black_scholes import black_scholes_call, black_scholes_put
from app.greeks import compute_all_greeks
from app.data_utils import (
    fetch_underlying_price, fetch_historical_prices, 
    compute_historical_volatility, get_expirations, fetch_options_chain
)
from app.implied_vol import compute_iv_smile, implied_vol_solver
from app.monte_carlo import compare_mc_vs_bsm
from app.plots import plot_heatmap, plot_iv_smile

# --- Page Config ---
st.set_page_config(page_title="Options Analytics", page_icon="📈", layout="wide")

# Custom CSS for Apple-like style
st.markdown("""
<style>
    .stApp { background-color: #F5F5F7; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Options Pricing & Analytics Platform")

# --- Sidebar ---
with st.sidebar:
    # st.markdown("---")
    st.markdown("##### 👨‍💻 Created by **Atharv Uday Parab**")
    
    # Replace the '#' with your actual profile URLs
    st.markdown(
        """
        <div style="display: flex; gap: 10px;">
            <a href="https://www.linkedin.com/in/atharvparab17" target="_blank">
                <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" width="100" />
            </a>
            <a href="https://github.com/aup2007" target="_blank">
                <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" width="90" />
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.header("Parameters")
    ticker = st.text_input("Ticker", value="AAPL").upper()

    st.markdown("---")
    live_mode = st.toggle("Live Price Updates")
    refresh_rate = st.slider("Refresh Rate (seconds)", 1, 60, 5)
    
    # Fetch Data
    price = fetch_underlying_price(ticker)
    hist_prices = fetch_historical_prices(ticker)
    hist_vol = compute_historical_volatility(hist_prices)
    
    if price:
        noise = random.uniform(-5.0,5.0)
        price = price + noise


    if price:
        st.success(f"Current {ticker}: ${price:.2f}")
    else:
        st.error("Invalid Ticker")
        price = 100.0
        hist_vol = 0.2

    # Option Inputs
    option_type = st.selectbox("Option Type", ["Call", "Put"]).lower()
    
    # Expiry Selection
    expirations = get_expirations(ticker)
    if expirations:
        expiry = st.selectbox("Expiry", expirations)
        days_to_expiry = (pd.to_datetime(expiry) - pd.Timestamp.now()).days
        if days_to_expiry <= 0: days_to_expiry = 1
    else:
        expiry = "2024-01-01"
        days_to_expiry = 30
        
    T = days_to_expiry / 365.0
    
    strike = st.number_input("Strike Price", value=float(price))
    risk_free = st.number_input("Risk-Free Rate (%)", value=4.5) / 100
    
    vol_mode = st.radio("Volatility Mode", ["Manual", "Historical"])
    if vol_mode == "Manual":
        sigma = st.slider("Volatility (σ)", 0.01, 2.0, 0.2)
    else:
        sigma = st.number_input("Historical Vol (Annualized)", value=hist_vol, format="%.4f")
    
# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", "Greeks", "Implied Volatility", "Monte Carlo", "Heatmaps", "Sensitivity"
])

# --- Tab 1: Overview ---
with tab1:
    st.subheader("Pricing Overview")
    
    bsm_price = black_scholes_call(price, strike, T, risk_free, sigma) if option_type == 'call' else \
                black_scholes_put(price, strike, T, risk_free, sigma)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Underlying Price", f"${price:.2f}")
    col2.metric("Theoretical Option Price", f"${bsm_price:.2f}")
    col3.metric("Volatility Used", f"{sigma:.2%}")

# --- Tab 2: Greeks & Hedging ---
with tab2:
    st.subheader("Greeks & Hedging Scenarios")
    greeks = compute_all_greeks(price, strike, T, risk_free, sigma, option_type)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Delta (Δ)", f"{greeks['Delta']:.4f}")
    c2.metric("Gamma (Γ)", f"{greeks['Gamma']:.4f}")
    c3.metric("Vega (ν)", f"{greeks['Vega']:.4f}")
    c4.metric("Theta (Θ)", f"{greeks['Theta']:.4f}")
    
    st.markdown("#### 'What-If' Hedging Analysis")
    st.caption("Estimated P&L if stock moves ±5%")
    
    S_up = price * 1.05
    S_down = price * 0.95
    dS_up = S_up - price
    dS_down = S_down - price
    
    # Taylor Series Approximation
    pnl_up = greeks['Delta'] * dS_up + 0.5 * greeks['Gamma'] * (dS_up ** 2)
    pnl_down = greeks['Delta'] * dS_down + 0.5 * greeks['Gamma'] * (dS_down ** 2)
    
    h_col1, h_col2 = st.columns(2)
    h_col1.metric("Stock +5%", f"${S_up:.2f}", delta=f"${pnl_up:.2f} P&L")
    h_col2.metric("Stock -5%", f"${S_down:.2f}", delta=f"${pnl_down:.2f} P&L")

# --- Tab 3: Implied Volatility ---
with tab3:
    st.subheader("Implied Volatility Smile")
    
    if st.button("Compute Smile"):
        with st.spinner("Fetching chain data..."):
            smile_df = compute_iv_smile(ticker, expiry, price, risk_free, option_type)
            
        if not smile_df.empty:
            fig_iv = plot_iv_smile(smile_df)
            st.plotly_chart(fig_iv, use_container_width=True)
            
            # Find specific option IV
            specific_iv = implied_vol_solver(bsm_price, price, strike, T, risk_free, option_type)
            st.info(f"IV for selected strike (${strike}): {specific_iv:.2%}")
        else:
            st.warning("No data found for this expiry.")

# --- Tab 4: Monte Carlo ---
with tab4:
    st.subheader("Monte Carlo Validation")
    n_paths = st.slider("Number of Paths", 1000, 50000, 5000)
    
    if st.button("Run Simulation"):
        bsm, mc, err = compare_mc_vs_bsm(price, strike, T, risk_free, sigma, option_type, n_paths)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("BSM Price", f"${bsm:.2f}")
        m2.metric("MC Price", f"${mc:.2f}")
        m3.metric("Pricing Error", f"${err:.4f}", delta_color="inverse")

# --- Tab 5: Heatmaps ---
with tab5:
    st.subheader("Interactive Heatmaps")
    
    # Define ranges
    spot_range = np.linspace(price * 0.8, price * 1.2, 20)
    vol_range = np.linspace(sigma * 0.5, sigma * 1.5, 20)
    
    # PnL Heatmap
    z_pnl = np.zeros((len(vol_range), len(spot_range)))
    base_price = bsm_price
    
    for i, v in enumerate(vol_range):
        for j, s in enumerate(spot_range):
            if option_type == 'call':
                sim_price = black_scholes_call(s, strike, T, risk_free, v)
            else:
                sim_price = black_scholes_put(s, strike, T, risk_free, v)
            z_pnl[i, j] = sim_price - base_price
            
    fig_heat = plot_heatmap(spot_range, vol_range, z_pnl, "Spot Price", "Volatility", "P&L Heatmap", "RedGreen")
    st.plotly_chart(fig_heat, use_container_width=True)

# --- Tab 6: Sensitivity ---
with tab6:
    st.subheader("Sensitivity Analysis")
    
    # Slider for Vol Range
    vol_min, vol_max = st.slider("Volatility Range", 0.05, 1.0, (0.1, 0.5))
    vol_steps = np.linspace(vol_min, vol_max, 50)
    
    prices = []
    for v in vol_steps:
        if option_type == 'call':
            prices.append(black_scholes_call(price, strike, T, risk_free, v))
        else:
            prices.append(black_scholes_put(price, strike, T, risk_free, v))
            
    import plotly.express as px
    fig_sens = px.line(x=vol_steps, y=prices, labels={'x':'Volatility', 'y':'Option Price'}, title="Price vs Volatility")
    st.plotly_chart(fig_sens, use_container_width=True)

if live_mode:
    time.sleep(refresh_rate)
    st.rerun()