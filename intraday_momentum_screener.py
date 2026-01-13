import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
from stock_universe import EXPANDED_UNIVERSE as STOCK_UNIVERSE

# --- Settings ---
MIN_PRICE = 50          # Lowered from 60

# --- Helper Functions ---
def calculate_rsi(series, length=14):
    """Calculate RSI indicator"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / (loss + 0.0001)
    return 100 - (100 / (1 + rs))

# --- Analysis Logic ---
def analyze_intraday(ticker):
    try:
        # Fetch Intraday Data (1m) - Real Time
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 5: return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        # Fetch Daily Data (for Prev Close & Avg Vol)
        df_daily = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if len(df_daily) < 5: return None
        if isinstance(df_daily.columns, pd.MultiIndex):
            df_daily.columns = [c[0] for c in df_daily.columns]

        # --- Metrics ---
        current_price = df.iloc[-1]['Close']
        prev_close = df_daily.iloc[-2]['Close']
        
        # 1. Price Filter (relaxed)
        if current_price < MIN_PRICE: return None
        
        # 2. Gap Calculation
        open_price = df.iloc[0]['Open']
        gap_pct = (open_price - prev_close) / prev_close * 100
        
        # NEW: Skip dangerous gap downs
        if gap_pct < -2.0:
            return None  # Skip gap down > 2%
        
        # 3. Intraday Change (from open to current)
        intraday_change = (current_price - open_price) / open_price * 100
        
        
        # 4. Volume Check (FIXED: Handle NaN safely)
        current_vol = df['Volume'].sum()
        avg_vol_20 = df_daily['Volume'].iloc[:-1].rolling(20).mean().iloc[-1]
        
        # Estimate daily volume projection
        minutes_elapsed = len(df)
        if minutes_elapsed == 0: return None
        projected_vol = (current_vol / minutes_elapsed) * 240
        
        # Safe RVOL calculation
        if pd.isna(avg_vol_20) or avg_vol_20 == 0:
            rvol = projected_vol / df_daily['Volume'].mean() if df_daily['Volume'].mean() > 0 else 1.0
        else:
            rvol = projected_vol / avg_vol_20
        
        # 5. VWAP
        df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['TPV'] = df['TP'] * df['Volume']
        total_vol = df['Volume'].sum()
        vwap = df['TPV'].sum() / total_vol if total_vol > 0 else current_price
        vwap_dist_pct = (current_price - vwap) / vwap * 100 if vwap > 0 else 0
        
        # 6. RSI (NEW: Overbought filter)
        df_daily['RSI'] = calculate_rsi(df_daily['Close'], 14)
        rsi = df_daily['RSI'].iloc[-1]
        rsi_overbought = rsi > 80
        
        # 7. Scoring (ENHANCED with RSI filter)
        score = 0
        decision = "WAIT"
        reasons = []
        
        # Gap bonus
        if gap_pct > 0.5:
            score += 2
            reasons.append(f"GapUp")
        elif gap_pct > 0:
            score += 1
            reasons.append(f"Flat")
            
        # Volume bonus
        if rvol > 2.0:
            score += 3
            reasons.append(f"VolSpike")
        elif rvol > 1.2:
            score += 2
            reasons.append(f"VolUp")
        elif rvol > 0.8:
            score += 1
            
        # VWAP position
        if current_price > vwap:
            score += 2
            reasons.append("AboveVWAP")
            
        # Intraday momentum
        if intraday_change > 1.0:
            score += 2
            reasons.append("Momo+")
        elif intraday_change > 0:
            score += 1
        
        # NEW: RSI overbought penalty
        if rsi_overbought:
            score -= 2
            reasons.append("OVERBOUGHT")
            
        # Decision
        if score >= 7:
            decision = "READY"
        elif score >= 4:
            decision = "WATCH"
        else:
            decision = "WAIT"
            
        # RETURN ALL with score >= 1 (relaxed to show results)
        if score >= 1:
            return {
                'Ticker': ticker,
                'Time': datetime.now().strftime("%H:%M"),
                'Close': current_price,
                'Change%': round(intraday_change, 2),
                'Gap%': round(gap_pct, 2),
                'RVOL': round(rvol, 2),
                'VWAP_Dist%': round(vwap_dist_pct, 2),
                'RSI': round(rsi, 1) if not pd.isna(rsi) else 50,  # NEW
                'Score': score,
                'Decision': decision,
                'Reasons': ", ".join(reasons) if reasons else "Baseline"
            }
            
    except Exception as e:
        return None
    return None

def run_intraday_screener():
    print(f"Running Intraday Momentum Screener...")
    print(f"Universe: {len(STOCK_UNIVERSE)} stocks")
    
    results = []
    start_t = time.time()
    
    for i, ticker in enumerate(STOCK_UNIVERSE):
        print(f"[{i+1}/{len(STOCK_UNIVERSE)}] Scanning {ticker}...", end='\r')
        res = analyze_intraday(ticker)
        if res:
            results.append(res)
            
    elapsed = time.time() - start_t
    print(f"\nScan completed in {elapsed:.1f}s")
    
    # Save & Show
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Score', ascending=False)
        
        fname = f"intraday_momentum_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(fname, index=False)
        print(f"Found {len(df)} candidates. Saved to {fname}")
        print(df.head(10).to_string(index=False))
        return df
    else:
        print("No candidates found.")
        return pd.DataFrame()

if __name__ == "__main__":
    run_intraday_screener()
