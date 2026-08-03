"""
CyberGuard Enterprise SOC UI Styling & Glassmorphic Dashboard Components
"""
import streamlit as st

def apply_soc_theme():
    """Apply CrowdStrike / Sentinel inspired dark glassmorphism styling."""
    st.markdown("""
    <style>
        /* Dark SOC Background */
        .stApp {
            background-color: #090d16;
            color: #f1f5f9;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Metric Glass Card Styling */
        div[data-testid="stMetric"] {
            background: rgba(18, 24, 41, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.5);
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            color: #38bdf8 !important;
            font-size: 1.8rem;
        }
        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0d1322 !important;
            border-right: 1px solid #1e293b;
        }

        /* Headings */
        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            letter-spacing: -0.5px;
        }
        
        .soc-header {
            background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }

        /* Status Badge CSS */
        .badge-critical {
            background-color: #7f1d1d;
            color: #fca5a5;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
        .badge-high {
            background-color: #991b1b;
            color: #fecaca;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
        .badge-medium {
            background-color: #854d0e;
            color: #fef08a;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
        .badge-low {
            background-color: #14532d;
            color: #bbf7d0;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render top enterprise brand header."""
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 0px; border-bottom: 1px solid #1e293b; margin-bottom: 20px;">
        <div>
            <h1 class="soc-header" style="margin: 0; font-size: 2.2rem;">🛡️ CYBERGUARD SOC ENTERPRISE</h1>
            <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 0.95rem;">
                Real-Time AI Authentication Behavioral Threat Analytics & Risk Engine
            </p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                ● LIVE MONITORING
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
