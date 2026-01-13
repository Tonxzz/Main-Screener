"""
StockSense Pro - Reusable UI Components
Premium glassmorphism design components
"""

import streamlit as st
from datetime import datetime

def hero(title: str, subtitle: str = ""):
    """Render hero header section with gradient title"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 class="tx-h1">{title}</h1>
        {f'<p class="tx-sub">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def section(title: str, icon: str = ""):
    """Render section header with optional icon"""
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
    <div class="tx-h2">{icon_html}{title}</div>
    """, unsafe_allow_html=True)

def card(content: str, highlight: bool = False):
    """Render glass card with HTML content"""
    highlight_class = "tx-card-highlight" if highlight else ""
    st.markdown(f"""
    <div class="tx-card {highlight_class}">
        {content}
    </div>
    """, unsafe_allow_html=True)

def badge(text: str, variant: str = "default"):
    """
    Render a badge/pill component
    Variants: ready, watch, wait, avoid, online, default
    """
    variant_class = f"tx-badge-{variant}" if variant != "default" else ""
    return f'<span class="tx-badge {variant_class}">{text}</span>'

def quick_steps():
    """Render Quick Start Guide with 3 step cards"""
    st.markdown("""
    <div style="margin: 2rem 0;">
        <div class="tx-h2">🚀 Quick Start Guide</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="tx-step-card">
            <div class="tx-step-number">1</div>
            <div class="tx-step-title">Pilih Screener</div>
            <div class="tx-step-desc">Pilih jenis screener dari sidebar sesuai strategi trading Anda</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tx-step-card">
            <div class="tx-step-number">2</div>
            <div class="tx-step-title">Scan Market</div>
            <div class="tx-step-desc">Klik tombol SCAN MARKET untuk menganalisis 120+ saham liquid</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="tx-step-card">
            <div class="tx-step-number">3</div>
            <div class="tx-step-title">Review & Trade</div>
            <div class="tx-step-desc">Analisa kandidat terbaik, cek chart, dan eksekusi trade</div>
        </div>
        """, unsafe_allow_html=True)

def status_card(online: bool = True, engine_version: str = "2.0", 
                last_updated: str = None, data_source: str = "Yahoo Finance"):
    """Render status card for sidebar"""
    status_text = "ONLINE" if online else "OFFLINE"
    status_class = "tx-status-online" if online else ""
    
    if last_updated is None:
        last_updated = datetime.now().strftime("%H:%M WIB")
    
    st.markdown(f"""
    <div class="tx-card" style="padding: 1rem;">
        <div style="margin-bottom: 0.75rem;">
            <span class="tx-status-dot {status_class}"></span>
            <span class="tx-badge tx-badge-online">{status_text}</span>
        </div>
        <div style="font-size: 0.8rem; color: rgba(234, 240, 255, 0.6); line-height: 1.8;">
            <div><strong>Engine:</strong> v{engine_version}</div>
            <div><strong>Updated:</strong> {last_updated}</div>
            <div><strong>Source:</strong> {data_source}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def screener_categories():
    """Render Available Screeners section with category cards"""
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <div class="tx-h2">📊 Available Screeners</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="tx-screener-category">
            <div class="tx-category-icon">⚡</div>
            <div class="tx-category-title">Day Trading</div>
            <div class="tx-category-desc">Intraday Momentum, BSJP Pattern</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tx-screener-category">
            <div class="tx-category-icon">📈</div>
            <div class="tx-category-title">Swing Trading</div>
            <div class="tx-category-desc">IDX Swing, VWAP Power</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="tx-screener-category">
            <div class="tx-category-icon">🎯</div>
            <div class="tx-category-title">Strategic</div>
            <div class="tx-category-desc">Ultimate Hybrid, Smart Money</div>
        </div>
        """, unsafe_allow_html=True)

def sidebar_logo():
    """Render sidebar logo and app name"""
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.25rem;">📊</div>
        <div style="font-size: 1.25rem; font-weight: 700; 
                    background: linear-gradient(135deg, #2EA8FF, #A78BFA);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            StockSense Pro
        </div>
        <div style="font-size: 0.75rem; color: rgba(234, 240, 255, 0.5);">
            Multi-Screener Dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0 0 1rem 0; border-color: rgba(255,255,255,0.08);'>", 
                unsafe_allow_html=True)

def screener_form_card(title: str, description: str):
    """Render screener form wrapper card"""
    st.markdown(f"""
    <div class="tx-card tx-card-highlight">
        <div class="tx-h2" style="margin-bottom: 0.5rem;">{title}</div>
        <p style="color: rgba(234, 240, 255, 0.6); font-size: 0.9rem; margin-bottom: 1rem;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)

def results_header(count: int, status: str = "READY"):
    """Render results section header with count badge"""
    variant = "ready" if status == "READY" else "watch"
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0 1rem 0;">
        <div class="tx-h2" style="margin: 0;">📋 Hasil Screening</div>
        <span class="tx-badge tx-badge-{variant}">{count} Kandidat</span>
    </div>
    """, unsafe_allow_html=True)

def metric_row(metrics: list):
    """
    Render a row of metrics
    metrics: list of tuples (label, value, delta)
    """
    cols = st.columns(len(metrics))
    for i, (label, value, delta) in enumerate(metrics):
        with cols[i]:
            st.metric(label=label, value=value, delta=delta)

def empty_state(message: str = "Belum ada data", icon: str = "📭"):
    """Render empty state placeholder"""
    st.markdown(f"""
    <div class="tx-card" style="text-align: center; padding: 3rem;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="color: rgba(234, 240, 255, 0.6);">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def score_badge(score: int, max_score: int = 10):
    """
    Generate score badge with stars or color-coded pill
    """
    if score >= 7:
        variant = "ready"
        label = f"⭐ {score}"
    elif score >= 4:
        variant = "watch"
        label = f"● {score}"
    else:
        variant = "wait"
        label = f"○ {score}"
    
    return f'<span class="tx-badge tx-badge-{variant}">{label}</span>'

def decision_badge(decision: str):
    """Generate decision badge based on screener output"""
    decision_upper = decision.upper() if decision else ""
    
    if "READY" in decision_upper:
        return '<span class="tx-badge tx-badge-ready">✓ READY</span>'
    elif "WATCH" in decision_upper:
        return '<span class="tx-badge tx-badge-watch">● WATCH</span>'
    elif "AVOID" in decision_upper:
        return '<span class="tx-badge tx-badge-avoid">✗ AVOID</span>'
    else:
        return '<span class="tx-badge tx-badge-wait">○ WAIT</span>'

def info_box(text: str, icon: str = "ℹ️"):
    """Render an info box"""
    st.markdown(f"""
    <div class="tx-card" style="background: rgba(46, 168, 255, 0.1); border-color: rgba(46, 168, 255, 0.2);">
        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
            <span style="font-size: 1.25rem;">{icon}</span>
            <div style="color: rgba(234, 240, 255, 0.8); font-size: 0.9rem; line-height: 1.5;">
                {text}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def divider():
    """Render styled divider"""
    st.markdown("<hr>", unsafe_allow_html=True)
