"""
Market Regime & Risk Management Module
Shared utilities for all screeners
"""

import yfinance as yf
import pandas as pd
import numpy as np

def get_market_regime():
    """
    Determine current market regime based on IHSG (^JKSE) position vs 200 EMA
    Returns: dict with regime info
    """
    try:
        ihsg = yf.download("^JKSE", period="1y", interval="1d", progress=False)
        if ihsg.empty or len(ihsg) < 200:
            return {"regime": "UNKNOWN", "ema200": 0, "current": 0, "dist_pct": 0}
        
        if isinstance(ihsg.columns, pd.MultiIndex):
            ihsg.columns = [c[0] for c in ihsg.columns]
        
        # Calculate EMA 200
        ema200 = ihsg['Close'].ewm(span=200, adjust=False).mean().iloc[-1]
        current = ihsg['Close'].iloc[-1]
        dist_pct = (current - ema200) / ema200 * 100
        
        # Determine regime
        if current > ema200 * 1.05:
            regime = "BULL"  # Strong uptrend
        elif current > ema200:
            regime = "BULL_WEAK"  # Weak uptrend
        elif current > ema200 * 0.95:
            regime = "BEAR_WEAK"  # Weak downtrend
        else:
            regime = "BEAR"  # Strong downtrend
        
        return {
            "regime": regime,
            "ema200": round(ema200, 2),
            "current": round(current, 2),
            "dist_pct": round(dist_pct, 2)
        }
    except:
        return {"regime": "UNKNOWN", "ema200": 0, "current": 0, "dist_pct": 0}

def calculate_atr_stop_loss(df, atr_multiplier=2.0):
    """
    Calculate ATR-based stop loss suggestion
    
    Args:
        df: DataFrame with OHLC data
        atr_multiplier: Multiplier for ATR (default 2.0)
    
    Returns:
        dict with stop loss price and percentage
    """
    try:
        # Calculate ATR (14 periods)
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        
        current_price = df['Close'].iloc[-1]
        stop_loss_price = current_price - (atr * atr_multiplier)
        stop_loss_pct = (stop_loss_price - current_price) / current_price * 100
        
        # Target (Risk:Reward = 1:2)
        target_price = current_price + (atr * atr_multiplier * 2)
        target_pct = (target_price - current_price) / current_price * 100
        
        return {
            "atr": round(atr, 2),
            "stop_loss": round(stop_loss_price, 0),
            "stop_loss_pct": round(stop_loss_pct, 2),
            "target": round(target_price, 0),
            "target_pct": round(target_pct, 2),
            "risk_reward": "1:2"
        }
    except:
        return {
            "atr": 0,
            "stop_loss": 0,
            "stop_loss_pct": 0,
            "target": 0,
            "target_pct": 0,
            "risk_reward": "N/A"
        }

def apply_regime_adjustment(score, regime_info):
    """
    Adjust score based on market regime
    
    Bull market: Boost momentum/trend strategies
    Bear market: Boost defensive/value strategies
    """
    regime = regime_info["regime"]
    
    if regime == "BULL":
        return score * 1.1  # 10% boost in bull market
    elif regime == "BULL_WEAK":
        return score * 1.05  # 5% boost
    elif regime == "BEAR_WEAK":
        return score * 0.95  # 5% penalty
    elif regime == "BEAR":
        return score * 0.85  # 15% penalty in bear market
    else:
        return score  # No adjustment if unknown

# Cache for market regime (avoid fetching IHSG multiple times)
_market_regime_cache = None
_cache_timestamp = None

def get_cached_market_regime():
    """Get market regime with caching (valid for 1 day)"""
    global _market_regime_cache, _cache_timestamp
    import time
    from datetime import datetime
    
    now = time.time()
    
    # Refresh cache if stale (> 1 day old) or doesn't exist
    if _market_regime_cache is None or _cache_timestamp is None or (now - _cache_timestamp) > 86400:
        _market_regime_cache = get_market_regime()
        _cache_timestamp = now
    
    return _market_regime_cache

if __name__ == "__main__":
    # Test
    regime = get_market_regime()
    print(f"Market Regime: {regime['regime']}")
    print(f"IHSG: {regime['current']} (EMA200: {regime['ema200']})")
    print(f"Distance: {regime['dist_pct']}%")
