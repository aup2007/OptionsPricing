# import streamlit as st

# def apply_style():
#     st.markdown("""
# <style>
#     /* Main Background */
#     .stApp {
#         background-color: #ffffff;
#     }
    
#     /* Header Gradient Text */
#     h1 {
#         background: -webkit-linear-gradient(45deg, #4f46e5, #06b6d4);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         font-weight: 800;
#     }
    
#     /* Metric Cards - Floating Shadow */
#     div[data-testid="stMetric"] {
#         background-color: #ffffff;
#         border: 1px solid #f3f4f6;
#         border-radius: 16px;
#         padding: 20px;
#         box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
#     }
    
#     /* Metric Labels */
#     div[data-testid="stMetricLabel"] {
#         color: #6b7280;
#         text-transform: uppercase;
#         font-size: 0.8rem;
#         letter-spacing: 1px;
#     }
    
#     /* Metric Values */
#     div[data-testid="stMetricValue"] {
#         color: #111827;
#         font-weight: 800;
#     }
    
#     /* Sidebar */
#     section[data-testid="stSidebar"] {
#         background-color: #f9fafb;
#     }
    
#     /* Tabs */
#     button[data-baseweb="tab"] {
#         background-color: transparent;
#         color: #4b5563;
#         font-weight: 600;
#     }
# </style>
# """, unsafe_allow_html=True)