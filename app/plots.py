import plotly.graph_objects as go
import numpy as np
import pandas as pd

def plot_heatmap(x_values, y_values, z_values, x_label, y_label, title, color_scheme="RdBu"):
    """
    Generates a Plotly heatmap.
    If color_scheme is 'RdBu', it assumes a divergent scale (Red=Neg, White=0, Blue/Green=Pos).
    """
    
    # Custom Divergent Colorscale: Red -> White -> Green
    custom_scale = [
        [0.0, "red"],
        [0.5, "white"],
        [1.0, "green"]
    ]
    
    scale = custom_scale if color_scheme == "RedGreen" else "Viridis"
    
    # Force symmetry for Red/Green P&L charts so 0 is white
    z_min = np.min(z_values)
    z_max = np.max(z_values)
    
    if color_scheme == "RedGreen":
        limit = max(abs(z_min), abs(z_max))
        z_min, z_max = -limit, limit

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values,
        colorscale=scale,
        zmin=z_min, zmax=z_max,
        colorbar=dict(title="Value")
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500
    )
    return fig

def plot_iv_smile(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['strike'], y=df['implied_vol'], mode='lines+markers', name='IV'))
    fig.update_layout(
        title="Implied Volatility Smile",
        xaxis_title="Strike Price",
        yaxis_title="Implied Volatility",
        template="plotly_white"
    )
    return fig