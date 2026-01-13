"""
Screener Wrapper Module
Runs screeners LIVE and returns DataFrame results
"""

import pandas as pd
import glob
import os
from datetime import datetime

def load_latest_csv(pattern):
    """Load the latest CSV file matching the pattern"""
    try:
        files = glob.glob(pattern)
        if not files:
            return pd.DataFrame()
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        if 'Score' in df.columns:
            df = df.sort_values('Score', ascending=False).reset_index(drop=True)
        return df
    except:
        return pd.DataFrame()

def run_intraday_momentum():
    """Run Intraday Momentum Screener LIVE"""
    try:
        from intraday_momentum_screener import run_intraday_screener
        df = run_intraday_screener()
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"Intraday error: {e}")
    return load_latest_csv("intraday_momentum_*.csv")

def run_bsjp():
    """Run BSJP Screener LIVE"""
    try:
        from bsjp_screener import run_screener
        df = run_screener()
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"BSJP error: {e}")
    return load_latest_csv("bsjp_results_*.csv")

def run_idx_swing():
    """Run IDX Swing Screener LIVE"""
    try:
        from idx_swing_screener import main
        main()
    except Exception as e:
        print(f"IDX Swing error: {e}")
    return load_latest_csv("idx_vwap_daily_*.csv")

def run_vwap_pro():
    """Run VWAP Pro Screener LIVE"""
    try:
        from vwap_screener_pro import run_daily_scan
        run_daily_scan()
    except Exception as e:
        print(f"VWAP Pro error: {e}")
    return load_latest_csv("idx_vwap_daily_*.csv")

def run_ultimate():
    """Run Ultimate Screener LIVE"""
    try:
        from ultimate_screener import run_ultimate as ultimate_main
        df = ultimate_main()
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"Ultimate error: {e}")
    return load_latest_csv("ultimate_results_*.csv")

def run_smart_money():
    """Run Smart Money Screener LIVE"""
    try:
        from smart_money_screener import run_screener
        df = run_screener()
        if df is not None and not df.empty:
            return df
    except Exception as e:
        print(f"Smart Money error: {e}")
    return load_latest_csv("smart_money_enhanced_*.csv")

SCREENER_FUNCTIONS = {
    'intraday_momentum': run_intraday_momentum,
    'bsjp': run_bsjp,
    'idx_swing': run_idx_swing,
    'vwap_pro': run_vwap_pro,
    'ultimate': run_ultimate,
    'smart_money': run_smart_money
}

def run_screener(screener_key):
    """Run any screener by key"""
    if screener_key not in SCREENER_FUNCTIONS:
        print(f"Unknown screener: {screener_key}")
        return pd.DataFrame()
    return SCREENER_FUNCTIONS[screener_key]()

def get_screener_status():
    """Check status of all screeners"""
    status = {}
    modules = [
        ('intraday_momentum_screener', 'Intraday Momentum'),
        ('bsjp_screener', 'BSJP'),
        ('idx_swing_screener', 'IDX Swing'),
        ('vwap_screener_pro', 'VWAP Pro'),
        ('ultimate_screener', 'Ultimate'),
        ('smart_money_screener', 'Smart Money')
    ]
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            status[display_name] = "[OK] Ready"
        except ImportError:
            status[display_name] = "[!] Not Found"
        except Exception as e:
            status[display_name] = f"[!] {str(e)[:20]}"
    return status

if __name__ == "__main__":
    print("Checking screener modules...")
    for k, v in get_screener_status().items():
        print(f"  {k}: {v}")
