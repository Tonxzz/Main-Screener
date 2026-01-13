"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    STOCKSENSE PRO - Stock Screener Dashboard                  ║
║            Premium UI | Glassmorphism | 6 Powerful Screeners | IDX Focus      ║
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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import UI components
from ui import (
    inject_global_css,
    hero,
    section,
    card,
    quick_steps,
    status_card,
    screener_categories,
    sidebar_logo,
    screener_form_card,
    results_header,
    empty_state,
    info_box,
    divider,
    render_table_basic,
    render_top_picks,
    download_button
)

# Inject global CSS FIRST
inject_global_css()

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENER CONFIGURATIONS (UNCHANGED)
# ═══════════════════════════════════════════════════════════════════════════════

SCREENER_CONFIG = {
    "day_trading": {
        "icon": "⚡",
        "title": "Day Trading / Scalping",
        "subtitle": "Cuan Cepat",
        "color": "#EF4444",
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
                "metrics": ["Score", "Decision", "RVOL", "Gap%", "VWAP_Dist%", "RSI"],
                "score_col": "Score",
                "module": "intraday_momentum_screener",
                "function": "run_intraday_screener"
            },
            "bsjp": {
                "name": "BSJP - Beli Saham Jangan Panik",
                "icon": "🚀",
                "description": "Volatility Expansion. Mencari saham 'meledak' (RelVol > 1.2 & Price > 1.5%).",
                "logic": """
                **Kenapa Dipilih:**
                - Logika Volatility Expansion yang agresif
                - Mencari saham dengan volume ledakan (RelVol > 1.2)
                - Deteksi Hammer Pattern (sinyal reversal)
                - Cocok untuk ride the momentum
                """,
                "metrics": ["Score", "Close", "Change%", "Rel_Vol", "Wick_Ratio", "Reasons"],
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
        "color": "#3B82F6",
        "screeners": {
            "idx_swing": {
                "name": "IDX Swing Continuation",
                "icon": "📈",
                "description": "Validated Backtest. VWMA & CLV > 0.7. Saham ditutup kuat, anti-guyuran.",
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
                "description": "High Liquidity (>10B IDR). Filter ketat untuk menghindari saham gorengan.",
                "logic": """
                **Kenapa Dipilih:**
                - Filter likuiditas ketat (>10B IDR)
                - Menghindari saham gorengan yang tidak bisa di-exit
                - Cocok untuk modal besar yang butuh keamanan likuiditas
                - Setup swing 3-5 hari holding
                """,
                "metrics": ["Score", "Decision", "Close", "VWMA_Dist_%", "Rel_Vol", "ReasonCodes"],
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
        "color": "#10B981",
        "screeners": {
            "ultimate": {
                "name": "Ultimate Hybrid Screener",
                "icon": "🏆",
                "description": "All-Rounder. Minervini Trend + RSI + Money Flow + RS Rating vs IHSG.",
                "logic": """
                **Kenapa Dipilih:**
                - Kombinasi 3 elemen: Trend + Momentum + Flow
                - **RS Rating**: Performa vs IHSG (>100 = outperform)
                - **ATR Stop Loss**: Rekomendasi exit otomatis
                - Cocok untuk hold mingguan dengan conviction tinggi
                """,
                "metrics": ["Score", "Validation", "RS_Rating", "Close", "StopLoss", "Target", "Reasons"],
                "score_col": "Score",
                "module": "ultimate_screener",
                "function": "run_ultimate"
            },
            "smart_money": {
                "name": "Smart Money Hunter",
                "icon": "🦈",
                "description": "Bandar Detector. OBV Divergence + CMF + MFI. Deteksi akumulasi tersembunyi.",
                "logic": """
                **Kenapa Dipilih:**
                - **OBV Divergence**: Deteksi akumulasi tersembunyi
                - CMF (Chaikin Money Flow) dan MFI untuk konfirmasi
                - Volume Spike detection untuk institutional activity
                - Cocok untuk buy on weakness sebelum breakout
                """,
                "metrics": ["Score", "Validation_Score", "Close", "CMF", "MFI", "OBV_Signal", "StopLoss"],
                "score_col": "Score",
                "module": "smart_money_screener",
                "function": "run_screener"
            }
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (UNCHANGED LOGIC)
# ═══════════════════════════════════════════════════════════════════════════════

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
        from screener_wrappers import run_screener
        
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
        
        module = __import__(module_name)
        func = getattr(module, function_name)
        result = func()
        
        if result is not None and isinstance(result, pd.DataFrame):
            return result, None
        else:
            import glob
            pattern = f"{module_name.replace('_screener', '')}*.csv"
            files = glob.glob(pattern)
            if files:
                latest = max(files, key=lambda x: x)
                return pd.read_csv(latest), None
            return pd.DataFrame(), "No results found"
    except Exception as e:
        return pd.DataFrame(), str(e)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE COMPONENTS (REFACTORED WITH NEW UI)
# ═══════════════════════════════════════════════════════════════════════════════

def render_home_page():
    """Render the home/guide page with premium UI"""
    
    # Hero Section
    hero(
        title="📊 StockSense Pro",
        subtitle="Professional Stock Screening Dashboard untuk IDX Market. 6 Screener Tervalidasi dalam Satu Platform."
    )
    
    # Quick Start Guide
    quick_steps()
    
    divider()
    
    # Available Screeners
    screener_categories()
    
    # Screener Cards per Category
    for cat_key, category in SCREENER_CONFIG.items():
        st.markdown(f"""
        <div class="tx-card" style="margin-top: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">{category['icon']}</span>
                <div>
                    <div style="font-size: 1.1rem; font-weight: 600; color: #EAF0FF;">{category['title']}</div>
                    <div style="font-size: 0.8rem; color: rgba(234, 240, 255, 0.5);">{category['subtitle']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        for scr_key, screener in category['screeners'].items():
            st.markdown(f"""
            <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.75rem 0; 
                        border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 1.25rem;">{screener['icon']}</span>
                <div>
                    <div style="font-weight: 600; color: #EAF0FF;">{screener['name']}</div>
                    <div style="font-size: 0.85rem; color: rgba(234, 240, 255, 0.5); line-height: 1.4;">
                        {screener['description']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    divider()
    
    # Usage Tips
    section("Tips Penggunaan", "💡")
    
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
        - Fokus pada RS_Rating > 100 dan OBV_Signal = BULLISH/ACCUMULATION
        """)

def render_screener_page(category_key, screener_key):
    """Render individual screener page with premium UI"""
    
    category = SCREENER_CONFIG[category_key]
    screener = category['screeners'][screener_key]
    
    # Header with category breadcrumb
    st.markdown(f"""
    <div style="margin-bottom: 0.5rem;">
        <span style="color: rgba(234, 240, 255, 0.5); font-size: 0.85rem;">
            {category['icon']} {category['title']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    hero(
        title=f"{screener['icon']} {screener['name']}",
        subtitle=screener['description']
    )
    
    # Screener Form Card
    st.markdown("""
    <div class="tx-card tx-card-highlight">
    """, unsafe_allow_html=True)
    
    # Logic Explanation
    with st.expander("📖 Kenapa Screener Ini Dipilih?", expanded=True):
        st.markdown(screener['logic'])
    
    # Score Interpretation
    st.markdown("""
    <div style="margin: 1rem 0;">
        <div style="font-size: 0.9rem; font-weight: 600; color: #EAF0FF; margin-bottom: 0.5rem;">
            📊 Score Interpretation
        </div>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.8rem;">
            <span><span class="tx-badge tx-badge-ready">⭐ 7-10</span> Excellent</span>
            <span><span class="tx-badge tx-badge-watch">● 4-6</span> Good</span>
            <span><span class="tx-badge tx-badge-wait">○ 1-3</span> Wait</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Scan Button
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        scan_button = st.button(
            "🔍 SCAN MARKET",
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
                info_box("Pastikan koneksi internet stabil dan coba lagi.", "💡")
            elif df.empty:
                empty_state("Tidak ada hasil yang memenuhi kriteria screener.", "📭")
            else:
                # Success message
                st.markdown(f"""
                <div class="tx-badge tx-badge-ready" style="margin: 1rem 0;">
                    ✓ Scan selesai dalam {elapsed:.1f}s • {len(df)} kandidat ditemukan
                </div>
                """, unsafe_allow_html=True)
                
                # Format dataframe
                df_display = format_dataframe(df, screener['score_col'])
                
                # Metrics Summary
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
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
                        ready_count = len(df[df['Decision'].astype(str).str.contains('READY', na=False)])
                        st.metric("READY", ready_count)
                
                divider()
                
                # Top Picks
                render_top_picks(df, top_n=5)
                
                # Results Table
                results_header(len(df), "READY")
                
                # Filter columns
                display_cols = ['Rank', 'Ticker'] + [c for c in screener['metrics'] if c in df_display.columns]
                if 'Rank' in df_display.columns:
                    df_final = df_display[[c for c in display_cols if c in df_display.columns]]
                else:
                    df_final = df_display
                
                render_table_basic(df_final, height=450)
                
                # Download Button
                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                download_button(df_display, f"{screener_key}_results_{timestamp}.csv")
                
                divider()
                
                # Interpretation Guide
                section("Cara Baca Hasil", "🎯")
                
                if screener_key == "intraday_momentum":
                    info_box("""
                    <strong>Fokus pada:</strong><br>
                    • <strong>READY</strong> = Siap entry, semua kondisi terpenuhi<br>
                    • <strong>RVOL > 1.5</strong> = Volume sangat kuat<br>
                    • <strong>RSI < 80</strong> = Belum overbought<br>
                    • <strong>Top 5 Score</strong> = Prioritas utama untuk dieksekusi
                    """, "📌")
                elif screener_key == "bsjp":
                    info_box("""
                    <strong>Fokus pada:</strong><br>
                    • <strong>Change% > 3%</strong> = Momentum sangat kuat<br>
                    • <strong>Rel_Vol > 2.0</strong> = Volume explosion<br>
                    • <strong>Hammer</strong> = Sinyal reversal bullish<br>
                    • <strong>EMA_Flow</strong> = Trending positif
                    """, "📌")
                elif screener_key in ["idx_swing", "vwap_pro"]:
                    info_box("""
                    <strong>Fokus pada:</strong><br>
                    • <strong>Decision = READY</strong> = Semua kriteria terpenuhi<br>
                    • <strong>CloseLocation > 0.7</strong> = Tutup kuat di upper range<br>
                    • <strong>Rel_Vol > 1.2</strong> = Ada partisipasi volume<br>
                    • <strong>TrendOK = True</strong> = Struktur uptrend valid
                    """, "📌")
                elif screener_key == "ultimate":
                    info_box("""
                    <strong>Fokus pada:</strong><br>
                    • <strong>RS_Rating > 100</strong> = Outperform IHSG<br>
                    • <strong>StopLoss & Target</strong> = Risk management otomatis<br>
                    • <strong>Uptrend + MoneyIn</strong> di Reasons = Setup ideal<br>
                    • <strong>Validation > 70</strong> = High conviction
                    """, "📌")
                elif screener_key == "smart_money":
                    info_box("""
                    <strong>Fokus pada:</strong><br>
                    • <strong>OBV_Signal = BULLISH</strong> = Divergence terdeteksi<br>
                    • <strong>CMF > 0.10</strong> = Strong accumulation<br>
                    • <strong>VolSpike</strong> di Reasons = Institutional buying<br>
                    • <strong>StopLoss</strong> = Gunakan untuk risk management
                    """, "📌")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Sidebar Navigation
    with st.sidebar:
        # Logo
        sidebar_logo()
        
        # Navigation
        nav_options = ["🏠 Home & Guide"]
        
        for cat_key, category in SCREENER_CONFIG.items():
            nav_options.append(f"{category['icon']} {category['title']}")
        
        selected_nav = st.radio(
            "Navigation",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='margin: 1rem 0; border-color: rgba(255,255,255,0.08);'>", 
                    unsafe_allow_html=True)
        
        # Screener Selection (if category selected)
        selected_screener = None
        selected_category = None
        
        for cat_key, category in SCREENER_CONFIG.items():
            if f"{category['icon']} {category['title']}" == selected_nav:
                selected_category = cat_key
                
                st.markdown(f"""
                <div style="font-size: 0.8rem; color: rgba(234, 240, 255, 0.5); 
                            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                    {category['subtitle']}
                </div>
                """, unsafe_allow_html=True)
                
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
        
        st.markdown("<hr style='margin: 1rem 0; border-color: rgba(255,255,255,0.08);'>", 
                    unsafe_allow_html=True)
        
        # Status Card
        status_card(
            online=True,
            engine_version="2.1",
            last_updated=datetime.now().strftime("%H:%M WIB"),
            data_source="Yahoo Finance"
        )
    
    # Main Content
    if selected_nav == "🏠 Home & Guide":
        render_home_page()
    elif selected_category and selected_screener:
        render_screener_page(selected_category, selected_screener)

if __name__ == "__main__":
    main()
