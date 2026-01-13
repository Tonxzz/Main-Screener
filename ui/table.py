"""
StockSense Pro - Table Rendering Components
Styled dataframe wrappers for premium look
"""

import streamlit as st
import pandas as pd

def render_table_basic(df: pd.DataFrame, height: int = 400):
    """
    Render dataframe with glass card wrapper
    Basic version using st.dataframe
    """
    if df is None or df.empty:
        st.markdown("""
        <div class="tx-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
            <div style="color: rgba(234, 240, 255, 0.5);">No results found</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Wrap table in styled container
    st.markdown('<div class="tx-table-wrap">', unsafe_allow_html=True)
    
    # Configure column display
    column_config = {}
    
    # Score column with progress bar
    if 'Score' in df.columns:
        max_score = df['Score'].max() if df['Score'].max() > 0 else 10
        column_config['Score'] = st.column_config.ProgressColumn(
            "Score",
            help="Scoring berdasarkan multiple criteria",
            min_value=0,
            max_value=max_score,
            format="%d"
        )
    
    # Validation column with progress
    if 'Validation' in df.columns:
        column_config['Validation'] = st.column_config.ProgressColumn(
            "Valid %",
            help="Validation score (0-100)",
            min_value=0,
            max_value=100,
            format="%d%%"
        )
    
    # Decision column styling
    if 'Decision' in df.columns:
        column_config['Decision'] = st.column_config.TextColumn(
            "Decision",
            help="Keputusan screener"
        )
    
    # Price columns
    for col in ['Close', 'StopLoss', 'Target']:
        if col in df.columns:
            column_config[col] = st.column_config.NumberColumn(
                col,
                format="%.0f"
            )
    
    # Percentage columns
    for col in ['Change%', 'Gap%', 'VWAP_Dist%']:
        if col in df.columns:
            column_config[col] = st.column_config.NumberColumn(
                col,
                format="%.2f%%"
            )
    
    # Render dataframe
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        column_config=column_config,
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_table_styled(df: pd.DataFrame, height: int = 400):
    """
    Render styled table with custom HTML for badges
    More visual but less interactive
    """
    if df is None or df.empty:
        st.markdown("""
        <div class="tx-card" style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📭</div>
            <div style="color: rgba(234, 240, 255, 0.5);">No results found</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Process dataframe for display
    display_df = df.copy()
    
    # Convert Decision to badge HTML
    if 'Decision' in display_df.columns:
        def decision_to_badge(val):
            if pd.isna(val):
                return val
            val_str = str(val).upper()
            if 'READY' in val_str:
                return '🟢 READY'
            elif 'WATCH' in val_str:
                return '🟡 WATCH'
            elif 'AVOID' in val_str:
                return '🔴 AVOID'
            else:
                return '⚪ WAIT'
        display_df['Decision'] = display_df['Decision'].apply(decision_to_badge)
    
    # Format Score with stars
    if 'Score' in display_df.columns:
        def score_to_stars(val):
            if pd.isna(val):
                return val
            score = int(val)
            if score >= 7:
                return f"⭐ {score}"
            elif score >= 4:
                return f"● {score}"
            else:
                return f"○ {score}"
        display_df['Score'] = display_df['Score'].apply(score_to_stars)
    
    # Render with basic wrapper
    st.markdown('<div class="tx-table-wrap">', unsafe_allow_html=True)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=height,
        hide_index=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

def render_top_picks(df: pd.DataFrame, top_n: int = 5):
    """
    Render top picks as cards (for homepage or summary)
    """
    if df is None or df.empty:
        return
    
    # Get top N by score
    if 'Score' in df.columns:
        top_df = df.nlargest(top_n, 'Score')
    else:
        top_df = df.head(top_n)
    
    st.markdown("""
    <div style="margin: 1rem 0;">
        <div class="tx-h2">🏆 Top Picks</div>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(min(len(top_df), 5))
    
    for i, (_, row) in enumerate(top_df.iterrows()):
        if i >= 5:
            break
        with cols[i]:
            ticker = row.get('Ticker', 'N/A')
            score = row.get('Score', 0)
            close = row.get('Close', 0)
            
            # Determine badge color
            if score >= 7:
                badge_style = "background: rgba(16, 185, 129, 0.2); border-color: rgba(16, 185, 129, 0.3);"
            elif score >= 4:
                badge_style = "background: rgba(251, 191, 36, 0.2); border-color: rgba(251, 191, 36, 0.3);"
            else:
                badge_style = "background: rgba(156, 163, 175, 0.2); border-color: rgba(156, 163, 175, 0.3);"
            
            st.markdown(f"""
            <div class="tx-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.1rem; font-weight: 700; color: #2EA8FF; margin-bottom: 0.25rem;">
                    {ticker}
                </div>
                <div style="font-size: 0.85rem; color: rgba(234, 240, 255, 0.6); margin-bottom: 0.5rem;">
                    Rp {close:,.0f}
                </div>
                <div class="tx-badge" style="{badge_style}">
                    ⭐ Score: {score}
                </div>
            </div>
            """, unsafe_allow_html=True)

def download_button(df: pd.DataFrame, filename: str = "results.csv"):
    """Render styled download button"""
    if df is None or df.empty:
        return
    
    csv = df.to_csv(index=False)
    
    st.markdown('<div class="tx-btn-secondary">', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
