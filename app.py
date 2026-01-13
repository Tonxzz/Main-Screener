"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    STOCKSENSE PRO - Stock Screener Dashboard                  ║
║                    Modern UI | 6 Powerful Screeners | IDX Focus               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Page Configuration - MUST BE FIRST
st.set_page_config(
    page_title="StockSense Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS - Modern Dark Theme
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --bg-primary: #0A0E17;
        --bg-secondary: #141B2D;
        --bg-card: #1A2238;
        --accent-blue: #3B82F6;
        --accent-cyan: #06B6D4;
        --accent-green: #10B981;
        --accent-orange: #F97316;
        --accent-red: #EF4444;
        --accent-purple: #8B5CF6;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --border-color: #2D3748;
    }
    
    /* Main Container */
    .main {
        background: linear-gradient(180deg, #0A0E17 0%, #141B2D 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #0A0E17 0%, #141B2D 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141B2D 0%, #1A2238 100%);
        border-right: 1px solid #2D3748;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #F8FAFC !important;
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(90deg, #3B82F6, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    
    /* Text */
    p, span, label {
        color: #CBD5E1 !important;
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(145deg, #1A2238, #141B2D);
        border: 1px solid #2D3748;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .screener-card {
        background: linear-gradient(145deg, #1A2238, #141B2D);
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .screener-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 32px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] > div {
        background: #1A2238 !important;
        border-radius: 12px;
    }
    
    /* Score Badges */
    .score-excellent {
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .score-good {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .score-medium {
        background: linear-gradient(135deg, #F97316, #EA580C);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .score-low {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Dividers */
    hr {
        border-color: #2D3748 !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: #1A2238 !important;
        border-color: #2D3748 !important;
        color: #F8FAFC !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: transparent;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1A2238 !important;
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #1A2238, #141B2D);
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 16px;
    }
    
    [data-testid="metric-container"] label {
        color: #94A3B8 !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #141B2D;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #06B6D4) !important;
        color: white !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: #1A2238 !important;
        border: 1px solid #2D3748 !important;
        border-radius: 12px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #3B82F6 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENER CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

SCREENER_CONFIG = {
    "day_trading": {
        "icon": "⚡",
        "title": "Day Trading / Scalping",
        "subtitle": "Cuan Cepat",
        "screeners": {
            "intraday_momentum": {
                "name": "Intraday Momentum",
                "icon": "🌅",
                "description": "Golden Window (09:00-09:30). Gap Up + Volume Flash. Real-time institutional flow.",
                "logic": """
                **Kenapa Dipilih:**
                - Fokus pada waktu emas pembukaan market
                - Menangkap Gap Up saham dengan Volume Spike
                - Deteksi institutional order flow secara real-time
                - Best setup untuk day trader agresif
                """,
                "metrics": ["Score", "Decision", "RVOL", "Gap%", "VWAP_Dist%"],
                "score_col": "Score",
                "module": "intraday_momentum_screener",
                "function": "run_intraday_screener"
            },
            "bsjp": {
                "name": "BSJP - Beli Saham Jangan Panik",
                "icon": "🚀",
                "description": "Volatility Expansion. Mencari saham 'meledak' (RelVol > 1.2 & Price > 1.5%). Ride the wave.",
                "logic": """
                **Kenapa Dipilih:**
                - Logika Volatility Expansion yang agresif
                - Mencari saham dengan volume ledakan (RelVol > 1.2)
                - Filter gain minimal +1.5% per hari
                - Cocok untuk ride the momentum
                """,
                "metrics": ["Score", "Close", "Change%", "Rel_Vol", "Wick_Ratio"],
                "score_col": "Score",
                "module": "bsjp_screener",
                "function": "run_screener"
            }
        }
    },
    "swing_trading": {
        "icon": "🌊",
        "title": "Swing Trading",
        "subtitle": "Santai 1-5 Hari",
        "screeners": {
            "idx_swing": {
                "name": "IDX Swing Continuation",
                "icon": "📈",
                "description": "Validated Backtest. Menggunakan VWMA & CLV > 0.7. Saham ditutup kuat, anti-guyuran.",
                "logic": """
                **Kenapa Dipilih:**
                - Parameter sudah di-backtest dan tervalidasi
                - Menggunakan VWMA (Volume Weighted MA) yang lebih akurat
                - Close Location Value > 0.7 = Close di top 30% candle
                - Saham dengan demand kuat, anti-guyuran
                """,
                "metrics": ["Score", "Decision", "Close", "VWMA_Dist_%", "Rel_Vol", "CloseLocation"],
                "score_col": "Score",
                "module": "idx_swing_screener",
                "function": "main"
            },
            "vwap_pro": {
                "name": "VWAP Power Swing Pro",
                "icon": "💎",
                "description": "High Liquidity (>10B IDR). Filter ketat untuk menghindari saham gorengan berisiko.",
                "logic": """
                **Kenapa Dipilih:**
                - Filter likuiditas ketat (>10B IDR)
                - Menghindari saham gorengan yang tidak bisa di-exit
                - Cocok untuk modal besar yang butuh keamanan likuiditas
                - Setup swing 3-5 hari holding
                """,
                "metrics": ["Score", "Decision", "Close", "VWMA_Dist_%", "Rel_Vol"],
                "score_col": "Score",
                "module": "vwap_screener_pro",
                "function": "run_daily_scan"
            }
        }
    },
    "strategic": {
        "icon": "💰",
        "title": "Strategic & Big Money",
        "subtitle": "Trend Follower",
        "screeners": {
            "ultimate": {
                "name": "Ultimate Hybrid Screener",
                "icon": "🏆",
                "description": "The All-Rounder. Minervini Trend + RSI Momentum + Money Flow. Grade A Setup (Score > 80).",
                "logic": """
                **Kenapa Dipilih:**
                - Kombinasi 3 elemen: Trend (Minervini) + Momentum (RSI) + Flow
                - Sistem scoring paling komprehensif (0-100)
                - Score > 80 = Grade A Setup dengan struktur sempurna
                - Cocok untuk hold mingguan dengan conviction tinggi
                """,
                "metrics": ["Score", "Validation", "Close", "RS_Rating", "CMF", "Rel_Vol", "Reasons"],
                "score_col": "Score",
                "module": "ultimate_screener",
                "function": "run_ultimate"
            },
            "smart_money": {
                "name": "Smart Money Hunter",
                "icon": "🦈",
                "description": "Bandar Detector. Fokus pada Akumulasi (CMF & MFI). Deteksi uang masuk sebelum harga terbang.",
                "logic": """
                **Kenapa Dipilih:**
                - Detektor akumulasi institusional
                - Menggunakan CMF (Chaikin Money Flow) dan MFI
                - Mendeteksi UANG MASUK sebelum harga naik
                - Cocok untuk buy on weakness
                """,
                "metrics": ["Score", "Validation_Score", "Close", "CMF", "MFI", "RS_Rating", "Reasons"],
                "score_col": "Score",
                "module": "smart_money_screener",
                "function": "run_screener"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_score_badge(score, max_score=100):
    """Return colored badge based on score percentage"""
    if pd.isna(score):
        return "N/A"
    
    pct = (score / max_score) * 100 if max_score > 10 else score * 10
    
    if pct >= 80:
        return f'<span class="score-excellent">★ {score}</span>'
    elif pct >= 60:
        return f'<span class="score-good">● {score}</span>'
    elif pct >= 40:
        return f'<span class="score-medium">○ {score}</span>'
    else:
        return f'<span class="score-low">○ {score}</span>'

def format_dataframe(df, score_col="Score"):
    """Format dataframe with proper styling"""
    if df is None or df.empty:
        return df
    
    # Sort by score descending
    if score_col in df.columns:
        df = df.sort_values(by=score_col, ascending=False).reset_index(drop=True)
        df.insert(0, 'Rank', range(1, len(df) + 1))
    
    return df

def run_screener_safely(module_name, function_name):
    """Run screener with error handling using wrapper module"""
    try:
        # Import the unified wrapper
        from screener_wrappers import run_screener, load_latest_csv
        
        # Map module name to screener key
        key_mapping = {
            'intraday_momentum_screener': 'intraday_momentum',
            'bsjp_screener': 'bsjp',
            'idx_swing_screener': 'idx_swing',
            'vwap_screener_pro': 'vwap_pro',
            'ultimate_screener': 'ultimate',
            'smart_money_screener': 'smart_money'
        }
        
        screener_key = key_mapping.get(module_name)
        
        if screener_key:
            result = run_screener(screener_key)
            if result is not None and not result.empty:
                return result, None
            return pd.DataFrame(), "No results found"
        
        # Fallback: Direct module import
        module = __import__(module_name)
        func = getattr(module, function_name)
        result = func()
        
        if result is not None and isinstance(result, pd.DataFrame):
            return result, None
        else:
            # Try to load from CSV
            import glob
            pattern = f"{module_name.replace('_screener', '')}*.csv"
            files = glob.glob(pattern)
            if files:
                latest = max(files, key=lambda x: x)
                return pd.read_csv(latest), None
            return pd.DataFrame(), "No results found"
    except Exception as e:
        return pd.DataFrame(), str(e)

def display_score_interpretation():
    """Display score interpretation guide"""
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1A2238, #141B2D); border: 1px solid #2D3748; border-radius: 12px; padding: 20px; margin: 20px 0;">
        <h4 style="color: #F8FAFC; margin-bottom: 16px;">📊 Score Interpretation</h4>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div><span class="score-excellent">★ 80-100</span> <span style="color: #CBD5E1;">Excellent - High conviction setup</span></div>
            <div><span class="score-good">● 60-79</span> <span style="color: #CBD5E1;">Good - Worth watching</span></div>
            <div><span class="score-medium">○ 40-59</span> <span style="color: #CBD5E1;">Fair - Need confirmation</span></div>
            <div><span class="score-low">○ 0-39</span> <span style="color: #CBD5E1;">Weak - Skip or wait</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_home_page():
    """Render the home/guide page"""
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">🎯 StockSense Pro</h1>
        <p style="font-size: 1.2rem; color: #94A3B8; max-width: 600px; margin: 0 auto;">
            Professional Stock Screening Dashboard untuk IDX Market.
            6 Screener Tervalidasi dalam Satu Platform.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("### 🚀 Quick Start Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="screener-card">
            <h4 style="color: #3B82F6;">1️⃣ Pilih Kategori</h4>
            <p style="color: #94A3B8;">Gunakan sidebar untuk memilih kategori trading: Day Trading, Swing, atau Strategic.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="screener-card">
            <h4 style="color: #06B6D4;">2️⃣ Pilih Screener</h4>
            <p style="color: #94A3B8;">Setiap kategori memiliki 2 screener dengan fokus berbeda. Baca deskripsi sebelum memilih.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="screener-card">
            <h4 style="color: #10B981;">3️⃣ Scan & Analyze</h4>
            <p style="color: #94A3B8;">Klik "Scan Market Now" dan analisis hasil berdasarkan Score & Ranking.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Available Screeners Overview
    st.markdown("### 📋 Available Screeners")
    
    for cat_key, category in SCREENER_CONFIG.items():
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1A2238, #141B2D); border: 1px solid #2D3748; border-radius: 12px; padding: 20px; margin: 15px 0;">
            <h4 style="color: #F8FAFC; margin-bottom: 12px;">
                {category['icon']} {category['title']} <span style="color: #94A3B8; font-weight: 400;">({category['subtitle']})</span>
            </h4>
        """, unsafe_allow_html=True)
        
        for scr_key, screener in category['screeners'].items():
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #2D3748;">
                <span style="font-size: 1.5rem; margin-right: 12px;">{screener['icon']}</span>
                <div>
                    <strong style="color: #F8FAFC;">{screener['name']}</strong>
                    <p style="color: #94A3B8; margin: 4px 0 0 0; font-size: 0.9rem;">{screener['description']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Usage Tips
    st.markdown("### 💡 Tips Penggunaan")
    
    with st.expander("🌅 Kapan Menggunakan Day Trading Screener?"):
        st.markdown("""
        - **Intraday Momentum**: Jalankan antara 09:00 - 09:30 WIB
        - **BSJP**: Jalankan setelah jam 10:00 untuk menangkap saham yang sudah breakout
        - Fokus pada saham dengan Score tinggi dan RVOL > 1.5
        """)
    
    with st.expander("🌊 Kapan Menggunakan Swing Screener?"):
        st.markdown("""
        - **IDX Swing & VWAP Pro**: Jalankan setelah market close (16:00+)
        - Analisis malam hari untuk setup esok hari
        - Fokus pada Decision = READY dan CloseLocation > 0.7
        """)
    
    with st.expander("💰 Kapan Menggunakan Strategic Screener?"):
        st.markdown("""
        - **Ultimate & Smart Money**: Jalankan weekend untuk analisis mingguan
        - Cocok untuk membangun watchlist dan analisis mendalam
        - Fokus pada CMF > 0.05 dan RS Rating > 0
        """)

def render_screener_page(category_key, screener_key):
    """Render individual screener page"""
    
    category = SCREENER_CONFIG[category_key]
    screener = category['screeners'][screener_key]
    
    # Header
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <p style="color: #94A3B8; margin: 0;">{category['icon']} {category['title']}</p>
        <h1 style="margin: 5px 0;">{screener['icon']} {screener['name']}</h1>
        <p style="color: #CBD5E1; font-size: 1.1rem;">{screener['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logic Explanation Card
    with st.expander("📖 Kenapa Screener Ini Dipilih?", expanded=True):
        st.markdown(screener['logic'])
    
    # Score Interpretation
    display_score_interpretation()
    
    st.markdown("---")
    
    # Scan Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        scan_button = st.button(
            "🔍 Scan Market Now",
            key=f"scan_{screener_key}",
            use_container_width=True
        )
    
    # Results Section
    if scan_button:
        with st.spinner(f"Scanning {screener['name']}... Mohon tunggu."):
            start_time = time.time()
            
            df, error = run_screener_safely(screener['module'], screener['function'])
            
            elapsed = time.time() - start_time
            
            if error:
                st.error(f"❌ Error: {error}")
                st.info("💡 Pastikan koneksi internet stabil dan coba lagi.")
            elif df.empty:
                st.warning("⚠️ Tidak ada hasil yang memenuhi kriteria screener.")
            else:
                st.success(f"✅ Scan selesai dalam {elapsed:.1f} detik. Ditemukan {len(df)} kandidat.")
                
                # Format and display
                df_display = format_dataframe(df, screener['score_col'])
                
                # Metrics Summary
                st.markdown("### 📊 Summary")
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Total Kandidat", len(df))
                with m2:
                    if screener['score_col'] in df.columns:
                        avg_score = df[screener['score_col']].mean()
                        st.metric("Avg Score", f"{avg_score:.1f}")
                with m3:
                    if 'Ticker' in df.columns:
                        st.metric("Top Pick", df.iloc[0]['Ticker'])
                with m4:
                    if 'Decision' in df.columns:
                        ready_count = len(df[df['Decision'].str.contains('READY', na=False)])
                        st.metric("READY Count", ready_count)
                
                st.markdown("---")
                
                # Results Table
                st.markdown("### 📋 Hasil Screener (Sorted by Score)")
                
                # Filter columns if specified
                display_cols = ['Rank', 'Ticker'] + [c for c in screener['metrics'] if c in df_display.columns]
                if 'Rank' in df_display.columns:
                    df_final = df_display[[c for c in display_cols if c in df_display.columns]]
                else:
                    df_final = df_display
                
                st.dataframe(
                    df_final,
                    use_container_width=True,
                    height=500
                )
                
                # Download Button
                csv = df_display.to_csv(index=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"{screener_key}_results_{timestamp}.csv",
                    mime="text/csv"
                )
                
                # Interpretation Guide
                st.markdown("---")
                st.markdown("### 🎯 Cara Baca Hasil")
                
                if screener_key == "intraday_momentum":
                    st.info("""
                    **Fokus pada:**
                    - **READY** = Siap entry, semua kondisi terpenuhi
                    - **RVOL > 1.5** = Volume sangat kuat
                    - **Gap% > 0** = Gap up dari close kemarin
                    - **Top 5 Score** = Prioritas utama untuk dieksekusi
                    """)
                elif screener_key == "bsjp":
                    st.info("""
                    **Fokus pada:**
                    - **Change% > 3%** = Momentum sangat kuat
                    - **Rel_Vol > 2.0** = Volume explosion
                    - **Wick_Ratio < 0.3** = Close di area high (strong demand)
                    - **EMA_Flow** = Trending positif
                    """)
                elif screener_key in ["idx_swing", "vwap_pro"]:
                    st.info("""
                    **Fokus pada:**
                    - **Decision = READY** = Semua kriteria swing terpenuhi
                    - **CloseLocation > 0.7** = Tutup kuat di upper range
                    - **Rel_Vol > 1.2** = Ada partisipasi volume
                    - **TrendOK = True** = Struktur uptrend valid
                    """)
                elif screener_key == "ultimate":
                    st.info("""
                    **Fokus pada:**
                    - **Score > 80** = Grade A Setup (highest conviction)
                    - **Validation > 70** = Fundamental + Technical selaras
                    - **Reasons: "Uptrend, Accum, MomoBlast"** = Perfect combo
                    - **RS_Rating > 0** = Outperform IHSG
                    """)
                elif screener_key == "smart_money":
                    st.info("""
                    **Fokus pada:**
                    - **CMF > 0.10** = Strong accumulation
                    - **MFI > 60** = Money flow sangat positif
                    - **RS_Rating > 0** = Outperform market
                    - **Reasons: "high_Accum"** = Institusi sedang mengumpulkan
                    """)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h2 style="margin: 0;">🎯 StockSense Pro</h2>
            <p style="color: #94A3B8; font-size: 0.9rem;">IDX Stock Screener</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        nav_options = ["🏠 Home & Guide"]
        
        for cat_key, category in SCREENER_CONFIG.items():
            nav_options.append(f"{category['icon']} {category['title']}")
        
        selected_nav = st.radio(
            "Navigation",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Screener Selection (if category selected)
        selected_screener = None
        selected_category = None
        
        for cat_key, category in SCREENER_CONFIG.items():
            if f"{category['icon']} {category['title']}" == selected_nav:
                selected_category = cat_key
                st.markdown(f"### {category['subtitle']}")
                
                screener_options = {
                    f"{s['icon']} {s['name']}": k 
                    for k, s in category['screeners'].items()
                }
                
                selected_label = st.selectbox(
                    "Pilih Screener",
                    list(screener_options.keys()),
                    label_visibility="collapsed"
                )
                
                selected_screener = screener_options[selected_label]
                break
        
        st.markdown("---")
        
        # Footer
        st.markdown(f"""
        <div style="text-align: center; color: #64748B; font-size: 0.8rem;">
            <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Data: Yahoo Finance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content
    if selected_nav == "🏠 Home & Guide":
        render_home_page()
    elif selected_category and selected_screener:
        render_screener_page(selected_category, selected_screener)

if __name__ == "__main__":
    main()
