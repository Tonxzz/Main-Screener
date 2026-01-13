"""
StockSense Pro - Global Theme & CSS Injector
Premium dark glassmorphism design system
"""

import streamlit as st

def inject_global_css():
    """Inject global CSS for premium dark theme with glassmorphism"""
    st.markdown("""
    <style>
    /* ============================================
       GLOBAL APP BACKGROUND
       ============================================ */
    .stApp {
        background: linear-gradient(135deg, #0B1020 0%, #0D1428 50%, #0B1020 100%);
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(46, 168, 255, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 60%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* ============================================
       MAIN CONTAINER
       ============================================ */
    .block-container {
        max-width: 1280px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* ============================================
       SIDEBAR STYLING
       ============================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1428 0%, #111A33 100%) !important;
        border-right: 1px solid rgba(46, 168, 255, 0.15) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    
    /* Sidebar navigation radio buttons */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(46, 168, 255, 0.1) !important;
        border-color: rgba(46, 168, 255, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: rgba(46, 168, 255, 0.15) !important;
        border-color: rgba(46, 168, 255, 0.5) !important;
    }
    
    /* ============================================
       GLASS CARD COMPONENT
       ============================================ */
    .tx-card {
        background: rgba(17, 26, 51, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 
            0 4px 24px rgba(0, 0, 0, 0.3),
            0 1px 2px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        margin-bottom: 1rem !important;
    }
    
    .tx-card-highlight {
        background: rgba(46, 168, 255, 0.08) !important;
        border-color: rgba(46, 168, 255, 0.2) !important;
    }
    
    /* ============================================
       TYPOGRAPHY
       ============================================ */
    .tx-h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #FFFFFF 0%, #A0C4FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .tx-h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #EAF0FF !important;
        margin-bottom: 1rem !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tx-sub {
        font-size: 1.1rem !important;
        color: rgba(234, 240, 255, 0.7) !important;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    
    .tx-label {
        font-size: 0.85rem;
        color: rgba(234, 240, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    
    /* ============================================
       BADGES / PILLS
       ============================================ */
    .tx-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .tx-badge-ready {
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .tx-badge-watch {
        background: rgba(251, 191, 36, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    
    .tx-badge-wait {
        background: rgba(156, 163, 175, 0.2);
        color: #9CA3AF;
        border: 1px solid rgba(156, 163, 175, 0.3);
    }
    
    .tx-badge-avoid {
        background: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .tx-badge-online {
        background: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.4) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.5) !important;
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary button style */
    .tx-btn-secondary button {
        background: rgba(46, 168, 255, 0.15) !important;
        border: 1px solid rgba(46, 168, 255, 0.3) !important;
        box-shadow: none !important;
    }
    
    .tx-btn-secondary button:hover {
        background: rgba(46, 168, 255, 0.25) !important;
        box-shadow: 0 4px 14px rgba(46, 168, 255, 0.2) !important;
    }
    
    /* ============================================
       INPUTS
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #EAF0FF !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(46, 168, 255, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(46, 168, 255, 0.15) !important;
    }
    
    /* ============================================
       TABLE WRAPPER
       ============================================ */
    .tx-table-wrap {
        background: rgba(17, 26, 51, 0.5) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        overflow: hidden;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] > div {
        background: transparent !important;
    }
    
    /* ============================================
       METRICS
       ============================================ */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #2EA8FF !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(234, 240, 255, 0.6) !important;
    }
    
    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ============================================
       DIVIDER
       ============================================ */
    hr {
        border-color: rgba(255, 255, 255, 0.08) !important;
        margin: 2rem 0 !important;
    }
    
    /* ============================================
       SCROLLBAR
       ============================================ */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(46, 168, 255, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(46, 168, 255, 0.5);
    }
    
    /* ============================================
       STEP CARDS
       ============================================ */
    .tx-step-card {
        background: rgba(17, 26, 51, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        height: 100%;
    }
    
    .tx-step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #2EA8FF 0%, #1E90FF 100%);
        border-radius: 50%;
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
        margin-bottom: 0.75rem;
    }
    
    .tx-step-title {
        font-size: 1rem;
        font-weight: 600;
        color: #EAF0FF;
        margin-bottom: 0.5rem;
    }
    
    .tx-step-desc {
        font-size: 0.85rem;
        color: rgba(234, 240, 255, 0.6);
        line-height: 1.4;
    }
    
    /* ============================================
       SCREENER CATEGORY CARDS
       ============================================ */
    .tx-screener-category {
        background: rgba(17, 26, 51, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .tx-category-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tx-category-title {
        font-size: 1rem;
        font-weight: 600;
        color: #EAF0FF;
        margin-bottom: 0.25rem;
    }
    
    .tx-category-desc {
        font-size: 0.8rem;
        color: rgba(234, 240, 255, 0.5);
    }
    
    /* ============================================
       STATUS INDICATOR
       ============================================ */
    .tx-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    
    .tx-status-online {
        background: #10B981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ============================================
       HIDE STREAMLIT BRANDING
       ============================================ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)
