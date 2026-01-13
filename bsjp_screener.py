import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

from stock_universe import EXPANDED_UNIVERSE as STOCK_UNIVERSE

# Settings (RELAXED)
MIN_PRICE = 50
MIN_VALUE_IDR = 1_000_000_000  # 1B (lowered from 5B)

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def analyze_bsjp(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if len(df) < 20: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        # Real-time price from intraday
        try:
            df_today = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df_today.empty:
                if isinstance(df_today.columns, pd.MultiIndex):
                    df_today.columns = [c[0] for c in df_today.columns]
                current_price = df_today.iloc[-1]['Close']
                current_volume = df_today['Volume'].sum()
                current_high = df_today['High'].max()
                current_low = df_today['Low'].min()
            else:
                current_price = df.iloc[-1]['Close']
                current_volume = df.iloc[-1]['Volume']
                current_high = df.iloc[-1]['High']
                current_low = df.iloc[-1]['Low']
        except:
            current_price = df.iloc[-1]['Close']
            current_volume = df.iloc[-1]['Volume']
            current_high = df.iloc[-1]['High']
            current_low = df.iloc[-1]['Low']

        prev_row = df.iloc[-2]
        
        if current_price < MIN_PRICE: return None
        
        value = current_price * current_volume
        if value < MIN_VALUE_IDR: return None
        
        # Change vs yesterday
        change_pct = (current_price - prev_row['Close']) / prev_row['Close'] * 100
        
        # Volume ratio
        avg_vol_5 = df['Volume'].rolling(5).mean().iloc[-1]
        rel_vol = current_volume / avg_vol_5 if avg_vol_5 > 0 else 0
        
        
        # Candle structure (FIXED: Correct wick calculation for both red/green candles)
        range_len = current_high - current_low
        if range_len == 0: 
            wick_ratio = 0
            lower_wick_ratio = 0
        else:
            body_top = max(current_price, df.iloc[0]['Open'] if len(df) > 0 else current_price)
            body_bottom = min(current_price, df.iloc[0]['Open'] if len(df) > 0 else current_price)
            upper_wick = current_high - body_top
            lower_wick = body_bottom - current_low
            wick_ratio = upper_wick / range_len
            lower_wick_ratio = lower_wick / range_len
        
        # Trend
        ema5 = calculate_ema(df['Close'], 5).iloc[-1]
        ema20 = calculate_ema(df['Close'], 20).iloc[-1]
        trend_aligned = (current_price > ema5) and (ema5 > ema20)
        
        # Scoring (ENHANCED)
        score = 0
        reasons = []
        
        if trend_aligned: 
            score += 2
            reasons.append("EMA_Flow")
        if rel_vol > 1.5:
            score += 2
            reasons.append("VolUp")
        elif rel_vol > 1.0:
            score += 1
        if change_pct > 1.0:
            score += 2
            reasons.append("Green")
        elif change_pct > 0:
            score += 1
        if wick_ratio < 0.3:
            score += 1
            reasons.append("StrongClose")
        # NEW: Hammer pattern bonus (long lower wick)
        if lower_wick_ratio > 0.5 and change_pct > 0:
            score += 2
            reasons.append("Hammer")
            
        # Return ALL with score >= 1
        if score >= 1:
            return {
                'Ticker': ticker,
                'Close': current_price,
                'Change%': round(change_pct, 2),
                'Volume_B': round(value / 1_000_000_000, 2),
                'Rel_Vol': round(rel_vol, 2),
                'Wick_Ratio': round(wick_ratio, 2),
                'Score': score,
                'Reasons': ", ".join(reasons) if reasons else "Baseline"
            }
        
    except Exception as e:
        return None
    return None

def run_screener():
    print(f"Running BSJP Screener...")
    print(f"Universe: {len(STOCK_UNIVERSE)} stocks")
    results = []
    
    start_t = time.time()
    for i, ticker in enumerate(STOCK_UNIVERSE):
        print(f"[{i+1}/{len(STOCK_UNIVERSE)}] Scanning {ticker}...", end='\r')
        res = analyze_bsjp(ticker)
        if res:
            results.append(res)
    
    elapsed = time.time() - start_t
    print(f"\nScan completed in {elapsed:.1f}s")
            
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Score', ascending=False)
        fname = f"bsjp_results_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(fname, index=False)
        print(f"Found {len(df)} candidates. Saved to {fname}")
        return df
    print("No candidates found.")
    return pd.DataFrame()

if __name__ == "__main__":
    run_screener()
