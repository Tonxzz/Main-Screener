import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import os
import time

# --- Configuration (OPTIMIZED) ---
# Hard Filters
MIN_PRICE = 100
MIN_LIQUIDITY_IDR = 10_000_000_000  # Optimized: 10 Billion IDR
MIN_HISTORY_DAYS = 60

# Strategy Parameters
VWMA_WINDOW = 20
PCT_FROM_VWMA_LIMIT = 20  # Max distance %
REL_VOL_THRESHOLD = 1.2
CLOSE_LOCATION_THRESHOLD = 0.60  # Default (0.60) worked well with H=5
BODY_RATIO_READY = 0.45
WICK_RATIO_TRAP = 0.55
REL_VOL_TRAP = 1.5

# Files
OUTPUT_DIR = "screener_output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 1. Data Loading ---
def get_all_tickers():
    """Returns the universe of tickers to scan."""
    try:
        from stock_universe import EXPANDED_UNIVERSE
        return list(set(EXPANDED_UNIVERSE))
    except ImportError:
        # Fallback if file missing
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "ASII.JK"]

def fetch_data(ticker, period="1y"):
    """Fetches daily data from Yahoo Finance."""
    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
        return df
    except:
        return None

# --- 2. Feature Engineering ---
def compute_features(df):
    df = df.copy()
    
    # 1. VWMA 20
    df['PV'] = df['Close'] * df['Volume']
    df['VolSum20'] = df['Volume'].rolling(VWMA_WINDOW).sum()
    df['VWMA20'] = df['PV'].rolling(VWMA_WINDOW).sum() / df['VolSum20']
    
    # 2. VWMA Dist %
    df['VWMA_Dist_%'] = (df['Close'] / df['VWMA20'] - 1) * 100
    
    # 3. Relative Volume (SMA20)
    df['VolSMA20'] = df['Volume'].rolling(20).mean()
    df['Rel_Vol'] = df['Volume'] / df['VolSMA20']
    
    # 4. Avg Value (Liquidity)
    df['Value'] = df['Close'] * df['Volume']
    df['AvgValue20D_IDR'] = df['Value'].rolling(20).mean()
    
    # 5. ADR & Range
    df['Range'] = df['High'] - df['Low']
    df['DailyRangePct'] = (df['Range'] / df['Close']) * 100
    df['ADR20_%'] = df['DailyRangePct'].rolling(20).mean()
    
    
    # 6. Candle Metrics (FIXED: Safe division for Range=0)
    df['Range'] = df['High'] - df['Low']
    df['Range'] = df['Range'].replace(0, 0.0001)  # Prevent division by zero
    df['CloseLocation'] = (df['Close'] - df['Low']) / df['Range']
    df['BodyRatio'] = abs(df['Close'] - df['Open']) / df['Range']
    df['WickRatio'] = 1.0 - df['BodyRatio']
    
    
    # 7. Trend
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['TrendOK'] = (df['Close'] > df['EMA20']) & (df['EMA20'] > df['EMA50'])
    
    return df

# --- 3. Decision Logic ---
def evaluate_decision(row):
    reasons = []
    
    # Validation
    if pd.isna(row['VWMA20']) or pd.isna(row['Rel_Vol']): return "AVOID", "NoData", 0
    if row['Close'] < MIN_PRICE: return "AVOID", "LowPrice", 0
    if row['AvgValue20D_IDR'] < MIN_LIQUIDITY_IDR: return "WAIT", "LowLiq", 0
    
    # Logic
    status = "WAIT"
    score = 0
    
    dist_pct = row['VWMA_Dist_%']
    wick = row['WickRatio']
    rel_vol = row['Rel_Vol']
    
    # Filters
    if dist_pct > PCT_FROM_VWMA_LIMIT: return "WAIT", "WAIT_OVEREXT", 0
    if row['CloseLocation'] < CLOSE_LOCATION_THRESHOLD: reasons.append("WAIT_WEAK_CLOSE")
    if wick > WICK_RATIO_TRAP and rel_vol > REL_VOL_TRAP: return "AVOID", "AVOID_TRAP", 0
    
    # READY Check
    is_ready = (
        row['Close'] > row['VWMA20'] and
        rel_vol >= REL_VOL_THRESHOLD and
        row['CloseLocation'] >= 0.70 and
        row['BodyRatio'] >= BODY_RATIO_READY and
        dist_pct <= PCT_FROM_VWMA_LIMIT
    )
    
    if is_ready:
        if row['TrendOK']:
            status = "READY"
            reasons.append("OK")
        else:
            status = "WAIT"
            reasons.append("WAIT_TREND")
    else:
        # Why not ready?
        if row['Close'] <= row['VWMA20']: reasons.append("WAIT_BELOW_VWMA")
        if rel_vol < REL_VOL_THRESHOLD: reasons.append("WAIT_LOW_RVOL")
        
    # Score
    score = compute_score(row, status)
    
    return status, "|".join(reasons) if reasons else "WAIT", int(score)

def compute_score(row, status):
    if status == "AVOID": return 0
    
    s = 0
    # Vol Component (0-30)
    s += 30 * np.tanh(max(row['Rel_Vol'] - 1, 0))
    # Candle Component (0-40)
    s += 25 * row['CloseLocation'] + 15 * min(1.0, row['BodyRatio'])
    # Trend (0-15)
    if row['TrendOK']: s += 15
    # VWAP (0-15)
    if row['Close'] > row['VWMA20']: s += 15
    
    return max(0, min(100, s))

# --- Main Runner ---
def run_daily_scan():
    print("Running VWAP Production Screener...")
    tickers = get_all_tickers()
    results = []
    
    print(f"Scanning {len(tickers)} tickers...")
    
    for t in tickers:
        df = fetch_data(t, period="6mo") # Live scan needs less data
        if df is None or len(df) < MIN_HISTORY_DAYS: continue
        
        df = compute_features(df)
        row = df.iloc[-1]
        
        dec, reason, score = evaluate_decision(row)
        
        results.append({
            'Date': row.name.strftime("%Y-%m-%d"),
            'Ticker': t,
            'Close': row['Close'],
            'VWMA20': round(row['VWMA20'], 0),
            'VWMA_Dist_%': round(row['VWMA_Dist_%'], 2),
            'Rel_Vol': round(row['Rel_Vol'], 2),
            'AvgValue20D_IDR': round(row['AvgValue20D_IDR'], 0),
            'ADR20_%': round(row['ADR20_%'], 2),
            'CloseLocation': round(row['CloseLocation'], 2),
            'BodyRatio': round(row['BodyRatio'], 2),
            'TrendOK': row['TrendOK'],
            'Decision': dec,
            'Score': score,
            'ReasonCodes': reason
        })
        
    if results:
        df_res = pd.DataFrame(results)
        
        # Rank: Sort by Decision (READY first) then Score (Desc)
        df_res['DecPriority'] = df_res['Decision'].map({'READY': 0, 'WAIT': 1, 'AVOID': 2})
        df_res = df_res.sort_values(by=['DecPriority', 'Score'], ascending=[True, False])
        
        # Add Rank
        df_res['Rank_ALL'] = range(1, len(df_res) + 1)
        df_res['Rank_READY'] = np.where(df_res['Decision']=='READY', df_res.groupby('Decision').cumcount() + 1, '')
        
        # Save
        today = datetime.datetime.now().strftime("%Y%m%d")
        fname = f"{OUTPUT_DIR}/idx_vwap_daily_{today}.csv"
        df_res.to_csv(fname, index=False)
        print(f"\nSaved Daily Report to {fname}")
        
        # Preview
        print("\n=== TOP READY CANDIDATES ===")
        print(df_res[df_res['Decision'] == 'READY'][['Ticker', 'Close', 'Score', 'Rel_Vol', 'ReasonCodes']].head(10))
    else:
        print("No results found.")

if __name__ == "__main__":
    run_daily_scan()
