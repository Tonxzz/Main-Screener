import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

from stock_universe import EXPANDED_UNIVERSE as STOCK_UNIVERSE
from market_utils import get_cached_market_regime, calculate_atr_stop_loss, apply_regime_adjustment

# Settings (RELAXED)
MIN_PRICE = 50
MIN_LIQUIDITY = 1_000_000_000  # 1B
EMA_FAST = 20
EMA_SLOW = 50

def calculate_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

def calculate_rsi(series, length):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / (loss + 0.0001)  # FIXED: Prevent division by zero
    return 100 - (100 / (1 + rs))

def calculate_cmf(df, length=20):
    denom = df['High'] - df['Low']
    denom = denom.replace(0, 0.0001)
    mf_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / denom
    mf_volume = mf_multiplier * df['Volume']
    cmf = mf_volume.rolling(window=length).sum() / df['Volume'].rolling(window=length).sum()
    return cmf

def calculate_rs_rating(ticker, df):
    """Calculate Relative Strength Rating vs IHSG benchmark"""
    try:
        # Fetch IHSG data
        ihsg = yf.download("^JKSE", period="6mo", interval="1d", progress=False)
        if ihsg.empty or len(ihsg) < 60:
            return 50  # Neutral if IHSG data unavailable
        
        if isinstance(ihsg.columns, pd.MultiIndex):
            ihsg.columns = [c[0] for c in ihsg.columns]
        
        # Calculate 60-day returns
        stock_return = (df['Close'].iloc[-1] - df['Close'].iloc[-60]) / df['Close'].iloc[-60] * 100
        ihsg_return = (ihsg['Close'].iloc[-1] - ihsg['Close'].iloc[-60]) / ihsg['Close'].iloc[-60] * 100
        
        # RS Rating: >100 = outperform, <100 = underperform
        if ihsg_return == 0:
            return 100 if stock_return > 0 else 50
        rs_rating = max(0, min(200, (stock_return / ihsg_return) * 100))
        return int(rs_rating)
    except:
        return 50  # Neutral on error

def analyze_ultimate(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(df) < 60: return None  # Need 60 days for RS Rating
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]

        # Real-time price
        try:
            df_today = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df_today.empty:
                if isinstance(df_today.columns, pd.MultiIndex): 
                    df_today.columns = [c[0] for c in df_today.columns]
                current_price = df_today.iloc[-1]['Close']
                current_volume = df_today['Volume'].sum()
            else:
                current_price = df.iloc[-1]['Close']
                current_volume = df.iloc[-1]['Volume']
        except:
            current_price = df.iloc[-1]['Close']
            current_volume = df.iloc[-1]['Volume']

        if current_price < MIN_PRICE: return None
        value = current_price * current_volume
        if value < MIN_LIQUIDITY: return None

        # Indicators
        df['EMA20'] = calculate_ema(df['Close'], EMA_FAST)
        df['EMA50'] = calculate_ema(df['Close'], EMA_SLOW)
        df['RSI'] = calculate_rsi(df['Close'], 14)
        df['CMF'] = calculate_cmf(df, 20)
        
        # ATR Stop Loss (NEW FEATURE)
        risk_mgmt = calculate_atr_stop_loss(df, atr_multiplier=2.0)
        
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        rel_vol = current_volume / vol_avg if vol_avg > 0 else 0

        last_hist = df.iloc[-1]
        
        # Trend
        trend_ok = (current_price > last_hist['EMA20']) and (last_hist['EMA20'] > last_hist['EMA50'])
        trend_weak = current_price > last_hist['EMA50']
        
        # RS Rating calculation (NEW FEATURE)
        rs_rating = calculate_rs_rating(ticker, df)
        
        # Momentum
        rsi_bull = last_hist['RSI'] > 50
        rsi_overbought = last_hist['RSI'] > 75  # NEW: Overbought filter
        vol_spike = rel_vol > 1.2
        money_in = last_hist['CMF'] > 0.05  # ENHANCED: Stricter threshold
        
        # Scoring (ENHANCED)
        score = 0
        reasons = []
        
        if trend_ok: 
            score += 3
            reasons.append("Uptrend")
        elif trend_weak:
            score += 1
            reasons.append("AboveEMA50")
        if money_in: 
            score += 2
            reasons.append("MoneyIn")
        if rsi_bull:
            score += 1
            reasons.append("RSI+")
        if vol_spike:
            score += 2
            reasons.append("VolSpike")
        # NEW: RS Rating bonus
        if rs_rating > 120:
            score += 2
            reasons.append("Outperform")
        elif rs_rating > 100:
            score += 1
            reasons.append("RS+")
        # NEW: Overbought penalty
        if rsi_overbought:
            score -= 1
            reasons.append("Overbought")

        validation = score * 10
        if trend_ok and money_in: validation += 20
        if rs_rating > 120: validation += 15
            
        # Return ALL with score >= 1
        if score >= 1:
            return {
                'Ticker': ticker,
                'Close': current_price,
                'Score': int(score),
                'Validation': min(validation, 100),
                'RS_Rating': rs_rating,
                'Rel_Vol': round(rel_vol, 2),
                'CMF': round(last_hist['CMF'], 3),
                'RSI': round(last_hist['RSI'], 1),
                'StopLoss': risk_mgmt['stop_loss'],  # NEW
                'Target': risk_mgmt['target'],  # NEW
                'RR': risk_mgmt['risk_reward'],  # NEW
                'Reasons': ", ".join(reasons) if reasons else "Baseline"
            }

    except Exception as e:
        return None
    return None

def run_ultimate():
    print(f"Running Ultimate Hybrid Screener...")
    print(f"Universe: {len(STOCK_UNIVERSE)} stocks")
    
    # Get market regime (NEW FEATURE)
    regime_info = get_cached_market_regime()
    print(f"Market Regime: {regime_info['regime']} (IHSG: {regime_info['current']}, Dist: {regime_info['dist_pct']}%)")
    
    results = []
    
    start_t = time.time()
    for i, ticker in enumerate(STOCK_UNIVERSE):
        print(f"[{i+1}/{len(STOCK_UNIVERSE)}] Scanning {ticker}...", end='\r')
        res = analyze_ultimate(ticker)
        if res:
            results.append(res)
    
    elapsed = time.time() - start_t
    print(f"\nScan completed in {elapsed:.1f}s")
            
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Score', ascending=False)
        fname = f"ultimate_results_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(fname, index=False)
        print(f"Found {len(df)} candidates. Saved to {fname}")
        return df
    print("No candidates found.")
    return pd.DataFrame()

if __name__ == "__main__":
    run_ultimate()
