"""
IDX Swing/Continuation Screener - Production Version
Daily screener for swing/continuation candidates with 1-5 day holding period
Based on VWMA edge with validated parameters (10B liquidity, 5-day hold)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
import sys
import config_swing as cfg

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

warnings.filterwarnings('ignore')

# ========================================
# UNIVERSE MANAGEMENT
# ========================================

def load_universe():
    """Load stock universe from idx_universe.txt"""
    try:
        with open('idx_universe.txt', 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        print(f"[OK] Loaded {len(tickers)} tickers from universe file")
        return tickers
    except FileNotFoundError:
        print("❌ idx_universe.txt not found. Please create it with stock tickers.")
        return []

# ========================================
# DATA FETCHING
# ========================================

def fetch_stock_data(ticker):
    """Fetch daily data for a single stock"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=cfg.FETCH_PERIOD, interval=cfg.FETCH_INTERVAL)
        
        if df.empty or len(df) < cfg.MIN_HISTORY_DAYS:
            return ticker, None
        
        # Add ticker column
        df['Ticker'] = ticker
        return ticker, df
    except Exception as e:
        return ticker, None

def fetch_all_data(tickers):
    """Fetch data for all tickers concurrently"""
    print(f"\n[INFO] Fetching data for {len(tickers)} stocks...")
    data_dict = {}
    failed = []
    
    with ThreadPoolExecutor(max_workers=cfg.MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_stock_data, ticker): ticker for ticker in tickers}
        
        for i, future in enumerate(as_completed(futures), 1):
            ticker, df = future.result()
            if df is not None:
                data_dict[ticker] = df
            else:
                failed.append(ticker)
            
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(tickers)} stocks processed...")
    
    print(f"[OK] Successfully fetched data for {len(data_dict)} stocks")
    if failed:
        print(f"[WARN] Failed to fetch {len(failed)} stocks: {', '.join(failed[:10])}{'...' if len(failed) > 10 else ''}")
    
    return data_dict

# ========================================
# TECHNICAL INDICATORS
# ========================================

def calculate_vwma(df, period=20):
    """Volume-Weighted Moving Average"""
    return (df['Close'] * df['Volume']).rolling(period).sum() / df['Volume'].rolling(period).sum()

def calculate_ema(series, period):
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()

def calculate_indicators(df):
    """Calculate all technical indicators for a stock"""
    df = df.copy()
    
    # Base indicators
    df['VWMA20'] = calculate_vwma(df, cfg.VWMA_PERIOD)
    df['EMA20'] = calculate_ema(df['Close'], cfg.EMA_FAST_PERIOD)
    df['EMA50'] = calculate_ema(df['Close'], cfg.EMA_SLOW_PERIOD)
    
    # Derived metrics
    df['VWMA_Dist_%'] = ((df['Close'] - df['VWMA20']) / df['VWMA20']) * 100
    df['Vol_SMA20'] = df['Volume'].rolling(cfg.VOL_SMA_PERIOD).mean()
    df['Rel_Vol'] = df['Volume'] / df['Vol_SMA20']
    
    # Liquidity (Average Daily Value in IDR, assuming Close is already in IDR)
    df['DailyValue'] = df['Close'] * df['Volume']
    df['AvgValue20D_IDR'] = df['DailyValue'].rolling(cfg.VALUE_SMA_PERIOD).mean()
    
    # Volatility (Average Daily Range %)
    df['DailyRange_%'] = ((df['High'] - df['Low']) / df['Close']) * 100
    df['ADR20_%'] = df['DailyRange_%'].rolling(cfg.ADR_PERIOD).mean()
    
    # Candle metrics
    candle_range = df['High'] - df['Low']
    df['CloseLocation'] = np.where(
        candle_range != 0,
        (df['Close'] - df['Low']) / candle_range,
        0.5  # Default if no range
    )
    df['BodyRatio'] = np.where(
        candle_range != 0,
        abs(df['Close'] - df['Open']) / candle_range,
        0.0
    )
    df['WickRatio'] = 1 - df['BodyRatio']
    
    # Trend confirmation
    df['TrendOK'] = (df['Close'] > df['EMA20']) & (df['EMA20'] > df['EMA50'])
    
    return df

# ========================================
# DECISION LOGIC
# ========================================

def apply_decision_logic(row):
    """
    Apply 3-level decision logic (READY/WAIT/AVOID)
    Returns: (Decision, Score, ReasonCodes)
    """
    score = 0
    reasons = []
    
    # Hard filters check (AVOID conditions)
    if pd.isna(row['Close']) or pd.isna(row['VWMA20']):
        return 'AVOID_NODATA', 0, 'NODATA'
    
    if row['Close'] < cfg.MIN_PRICE:
        return 'AVOID_LOWPRICE', 0, 'LOWPRICE'
    
    if row['AvgValue20D_IDR'] < cfg.MIN_LIQUIDITY_IDR:
        return 'AVOID_LIQUIDITY', 0, 'LOWLIQ'
    
    # Trap detection (extended upper wick with weak body)
    if row['WickRatio'] > cfg.TRAP_WICK_RATIO_MAX and row['BodyRatio'] < cfg.TRAP_BODY_RATIO_MAX:
        return 'AVOID_TRAP', 0, 'TRAP'
    
    # Scoring system
    if row['Close'] > row['VWMA20']:
        score += cfg.SCORE_VWMA_ABOVE
        reasons.append('VWMA+')
    
    if row['Rel_Vol'] >= cfg.READY_REL_VOL_MIN:
        score += cfg.SCORE_REL_VOL
        reasons.append('VOL+')
    
    if row['CloseLocation'] >= cfg.READY_CLOSE_LOC_MIN:
        score += cfg.SCORE_CLOSE_LOC
        reasons.append('CLOC+')
    
    if row['BodyRatio'] >= cfg.READY_BODY_RATIO_MIN:
        score += cfg.SCORE_BODY_RATIO
        reasons.append('BODY+')
    
    if abs(row['VWMA_Dist_%']) <= 10.0:  # Tight to VWMA (bonus)
        score += cfg.SCORE_VWMA_TIGHT
        reasons.append('TIGHT+')
    
    if row['TrendOK']:
        score += cfg.SCORE_TREND_OK
        reasons.append('TREND+')
    
    # Decision classification
    is_ready = (
        row['Close'] > row['VWMA20'] and
        row['Rel_Vol'] >= cfg.READY_REL_VOL_MIN and
        row['CloseLocation'] >= cfg.READY_CLOSE_LOC_MIN and
        row['BodyRatio'] >= cfg.READY_BODY_RATIO_MIN and
        row['VWMA_Dist_%'] <= cfg.READY_VWMA_DIST_MAX and
        row['TrendOK']
    )
    
    if is_ready:
        decision = 'READY'
    else:
        # Categorize WAIT reasons
        wait_reasons = []
        if not row['TrendOK']:
            wait_reasons.append('TREND')
        if row['Rel_Vol'] < cfg.READY_REL_VOL_MIN:
            wait_reasons.append('VOL')
        if row['CloseLocation'] < cfg.READY_CLOSE_LOC_MIN:
            wait_reasons.append('CLOC')
        if row['BodyRatio'] < cfg.READY_BODY_RATIO_MIN:
            wait_reasons.append('BODY')
        if row['VWMA_Dist_%'] > cfg.READY_VWMA_DIST_MAX:
            wait_reasons.append('DIST')
        
        decision = f"WAIT_{'+'.join(wait_reasons)}" if wait_reasons else 'WAIT'
    
    reason_str = '|'.join(reasons) if reasons else 'NONE'
    return decision, score, reason_str

# ========================================
# MAIN SCREENING LOGIC
# ========================================

def screen_stocks(data_dict):
    """Screen all stocks and generate results DataFrame"""
    print(f"\n[INFO] Analyzing {len(data_dict)} stocks...")
    
    results = []
    
    for ticker, df in data_dict.items():
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Get latest row
        latest = df.iloc[-1]
        
        # Apply decision logic
        decision, score, reasons = apply_decision_logic(latest)
        
        # Build result row
        result = {
            'Date': latest.name.strftime('%Y-%m-%d'),
            'Ticker': ticker.replace('.JK', ''),
            'Close': round(latest['Close'], 2),
            'VWMA20': round(latest['VWMA20'], 2),
            'VWMA_Dist_%': round(latest['VWMA_Dist_%'], 2),
            'Rel_Vol': round(latest['Rel_Vol'], 2),
            'AvgValue20D_IDR': f"{latest['AvgValue20D_IDR']/1e9:.2f}B",
            'ADR20_%': round(latest['ADR20_%'], 2),
            'CloseLocation': round(latest['CloseLocation'], 3),
            'BodyRatio': round(latest['BodyRatio'], 3),
            'WickRatio': round(latest['WickRatio'], 3),
            'EMA20': round(latest['EMA20'], 2),
            'EMA50': round(latest['EMA50'], 2),
            'TrendOK': latest['TrendOK'],
            'Decision': decision,
            'Score': score,
            'ReasonCodes': reasons,
        }
        
        results.append(result)
    
    df_results = pd.DataFrame(results)
    
    # Add ranking for READY candidates
    df_results['Rank_READY'] = 0
    ready_mask = df_results['Decision'] == 'READY'
    if ready_mask.sum() > 0:
        df_results.loc[ready_mask, 'Rank_READY'] = (
            df_results.loc[ready_mask, 'Score']
            .rank(ascending=False, method='min')
            .astype(int)
        )
    
    # Sort: READY first (by score), then WAIT, then AVOID
    def sort_key(row):
        if row['Decision'] == 'READY':
            return (0, -row['Score'])
        elif row['Decision'].startswith('WAIT'):
            return (1, -row['Score'])
        else:
            return (2, 0)
    
    df_results['_sort'] = df_results.apply(sort_key, axis=1)
    df_results = df_results.sort_values('_sort').drop('_sort', axis=1).reset_index(drop=True)
    
    print(f"[OK] Screening complete!")
    return df_results

# ========================================
# OUTPUT & REPORTING
# ========================================

def save_results(df_results):
    """Save results to CSV"""
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{cfg.OUTPUT_PREFIX_SCREENER}_{date_str}.csv"
    filepath = f"{cfg.OUTPUT_DIR}/{filename}"
    
    df_results.to_csv(filepath, index=False)
    print(f"\n[SAVED] Results saved to: {filename}")
    return filename

def print_summary(df_results):
    """Print console summary"""
    total = len(df_results)
    ready = (df_results['Decision'] == 'READY').sum()
    wait = df_results['Decision'].str.startswith('WAIT').sum()
    avoid = total - ready - wait
    
    print(f"\n{'='*80}")
    print(f"IDX SWING/CONTINUATION SCREENER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")
    print(f"Total Scanned:  {total:>4}")
    print(f"READY:          {ready:>4} ({ready/total*100:>5.1f}%)")
    print(f"WAIT:           {wait:>4} ({wait/total*100:>5.1f}%)")
    print(f"AVOID:          {avoid:>4} ({avoid/total*100:>5.1f}%)")
    print(f"{'-'*80}")
    
    # Top READY candidates
    top_ready = df_results[df_results['Decision'] == 'READY'].head(cfg.CONSOLE_TOP_N)
    
    if len(top_ready) > 0:
        print(f"\n>> TOP {len(top_ready)} READY CANDIDATES:")
        print(f"{'-'*80}")
        print(f"{'#':<3} {'Ticker':<8} {'Close':>8} {'VWMA%':>7} {'RVol':>6} {'CLoc':>6} {'Body':>6} {'Score':>6}")
        print(f"{'-'*80}")
        
        for i, row in top_ready.iterrows():
            print(f"{int(row['Rank_READY']):<3} {row['Ticker']:<8} {row['Close']:>8.0f} "
                  f"{row['VWMA_Dist_%']:>7.2f} {row['Rel_Vol']:>6.2f} "
                  f"{row['CloseLocation']:>6.3f} {row['BodyRatio']:>6.3f} {row['Score']:>6.0f}")
    else:
        print(f"\n[WARN] No READY candidates found today.")
        
        # Show top WAIT candidates as alternative
        top_wait = df_results[df_results['Decision'].str.startswith('WAIT')].head(5)
        if len(top_wait) > 0:
            print(f"\n[INFO] Top 5 WAIT Candidates (for watchlist):")
            for i, row in top_wait.iterrows():
                print(f"  {row['Ticker']:<8} {row['Close']:>8.0f}  ({row['Decision']})")
    
    print(f"{'='*80}\n")

# ========================================
# MAIN EXECUTION
# ========================================

def main():
    """Main execution function"""
    print(f"\n{'='*80}")
    print(f"IDX SWING/CONTINUATION SCREENER v1.0")
    print(f"Optimized for 1-5 day hold period | Liquidity >= 10B IDR")
    print(f"{'='*80}")
    
    # Load universe
    tickers = load_universe()
    if not tickers:
        return
    
    # Fetch data
    data_dict = fetch_all_data(tickers)
    if not data_dict:
        print("[ERROR] No data fetched. Exiting.")
        return
    
    # Screen stocks
    df_results = screen_stocks(data_dict)
    
    # Output results
    filename = save_results(df_results)
    print_summary(df_results)
    
    print(f"[DONE] Screening complete! Review top candidates in chart before entry.")
    print(f"[FILE] Full results: {filename}\n")

if __name__ == "__main__":
    main()
