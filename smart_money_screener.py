import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime

from stock_universe import EXPANDED_UNIVERSE as STOCK_UNIVERSE
from market_utils import get_cached_market_regime, calculate_atr_stop_loss

MIN_PRICE = 50

def calculate_mfi(df, length=14):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    money_flow = typical_price * df['Volume']
    
    positive_flow = np.where(typical_price > typical_price.shift(1), money_flow, 0)
    negative_flow = np.where(typical_price < typical_price.shift(1), money_flow, 0)
    
    positive_flow = pd.Series(positive_flow, index=df.index)
    negative_flow = pd.Series(negative_flow, index=df.index)
    
    positive_flow_sum = positive_flow.rolling(window=length).sum()
    negative_flow_sum = negative_flow.rolling(window=length).sum()
    
    mfi = 100 - (100 / (1 + positive_flow_sum / (negative_flow_sum + 0.0001)))
    return mfi

def calculate_cmf(df, length=20):
    denom = df['High'] - df['Low']
    denom = denom.replace(0, 0.0001)
    mf_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / denom
    mf_volume = mf_multiplier * df['Volume']
    cmf = mf_volume.rolling(window=length).sum() / df['Volume'].rolling(window=length).sum()
    return cmf

def calculate_obv(df):
    """Calculate On-Balance Volume (OBV) - institutional accumulation indicator"""
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)

def detect_obv_divergence(df):
    """Detect bullish divergence: Price down, OBV up (accumulation)"""
    try:
        price_slope = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10]
        obv_slope = (df['OBV'].iloc[-1] - df['OBV'].iloc[-10]) / abs(df['OBV'].iloc[-10] + 1)
        
        # Bullish divergence: price down/flat, OBV up
        if price_slope < 0.02 and obv_slope > 0.05:
            return "BULLISH"
        # Regular accumulation: both up
        elif price_slope > 0 and obv_slope > 0:
            return "ACCUMULATION"
        else:
            return "NEUTRAL"
    except:
        return "NEUTRAL"

def analyze_ticker(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(df) < 30: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]

        # Real-time
        try:
            df_today = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df_today.empty:
                if isinstance(df_today.columns, pd.MultiIndex): 
                    df_today.columns = [c[0] for c in df_today.columns]
                current_price = df_today.iloc[-1]['Close']
            else:
                current_price = df.iloc[-1]['Close']
        except:
             current_price = df.iloc[-1]['Close']
             
        if current_price < MIN_PRICE: return None
        
        # Indicators (ENHANCED with OBV)
        df['CMF'] = calculate_cmf(df, 20)
        df['MFI'] = calculate_mfi(df, 14)
        df['OBV'] = calculate_obv(df)
        
        # ATR Stop Loss (NEW FEATURE)
        risk_mgmt = calculate_atr_stop_loss(df, atr_multiplier=2.0)
        
        # OBV trend analysis
        obv_divergence = detect_obv_divergence(df)
        obv_trend_up = df['OBV'].iloc[-1] > df['OBV'].iloc[-5]
        
        # Volume spike detection
        avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
        vol_spike = df['Volume'].iloc[-1] > (avg_volume * 2) if avg_volume > 0 else False
        
        row = df.iloc[-1]
        
        # Scoring (ENHANCED with OBV)
        score = 0
        reasons = []
        
        if row['CMF'] > 0.10:
            score += 3
            reasons.append("StrongAccum")
        elif row['CMF'] > 0.05:
            score += 2
            reasons.append("Accum")
        elif row['CMF'] > 0:
            score += 1
            reasons.append("MoneyIn")
            
        if row['MFI'] > 60:
            score += 2
            reasons.append("MFI_Strong")
        elif row['MFI'] > 50:
            score += 1
            reasons.append("MFI+")
        
        # NEW: OBV divergence bonus
        if obv_divergence == "BULLISH":
            score += 3
            reasons.append("OBV_Divergence")
        elif obv_divergence == "ACCUMULATION":
            score += 2
            reasons.append("OBV_Accum")
        elif obv_trend_up:
            score += 1
            reasons.append("OBV+")
        
        # NEW: Volume spike bonus
        if vol_spike:
            score += 2
            reasons.append("VolSpike")
            
        # Return ALL with score >= 1
        if score >= 1:
            return {
                'Ticker': ticker,
                'Close': current_price,
                'Score': score,
                'Validation_Score': score * 15,
                'CMF': round(row['CMF'], 3),
                'MFI': round(row['MFI'], 1),
                'OBV_Signal': obv_divergence,
                'StopLoss': risk_mgmt['stop_loss'],  # NEW
                'Target': risk_mgmt['target'],  # NEW
                'Reasons': ", ".join(reasons) if reasons else "Baseline"
            }
    except:
        return None
    return None

def run_screener():
    print(f"Running Smart Money Screener...")
    print(f"Universe: {len(STOCK_UNIVERSE)} stocks")
    
    # Get market regime
    regime_info = get_cached_market_regime()
    print(f"Market Regime: {regime_info['regime']}")
    
    results = []
    
    start_t = time.time()
    for i, ticker in enumerate(STOCK_UNIVERSE):
        print(f"[{i+1}/{len(STOCK_UNIVERSE)}] Scanning {ticker}...", end='\r')
        res = analyze_ticker(ticker)
        if res:
            results.append(res)
    
    elapsed = time.time() - start_t
    print(f"\nScan completed in {elapsed:.1f}s")
            
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Score', ascending=False)
        fname = f"smart_money_enhanced_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(fname, index=False)
        print(f"Found {len(df)} candidates. Saved to {fname}")
        return df
    print("No candidates found.")
    return pd.DataFrame()

if __name__ == "__main__":
    run_screener()
