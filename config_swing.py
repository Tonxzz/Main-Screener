"""
IDX Swing/Continuation Screener - Configuration File
Optimized parameters based on VWAP edge and 5-day hold period validation
"""

# ========================================
# HARD FILTERS
# ========================================
MIN_PRICE = 100  # Minimum stock price (avoid penny stocks)
MIN_LIQUIDITY_IDR = 10_000_000_000  # 10 Billion IDR minimum daily value (mandatory for stability)
MIN_HISTORY_DAYS = 60  # Minimum days of valid history required

# ========================================
# DECISION THRESHOLDS - READY
# ========================================
# A stock must meet ALL of these criteria to be marked as READY
READY_VWMA_ABOVE = True  # Close must be > VWMA20
READY_VWMA_DIST_MAX = 20.0  # Max % distance from VWMA20 (avoid overextension)
READY_REL_VOL_MIN = 1.2  # Minimum relative volume (1.2x = 20% above average)
READY_CLOSE_LOC_MIN = 0.60  # Minimum close location (close in upper 40% of range)
READY_BODY_RATIO_MIN = 0.45  # Minimum body ratio (solid candle, not doji)
READY_TREND_OK = True  # Must have TrendOK = True (Close > EMA20 > EMA50)

# ========================================
# DECISION THRESHOLDS - WAIT
# ========================================
# Stocks that show potential but don't meet all READY criteria
WAIT_REL_VOL_MIN = 0.8  # Minimum relative volume for WAIT candidates
WAIT_CLOSE_LOC_MIN = 0.40  # Minimum close location for WAIT candidates
WAIT_VWMA_DIST_MAX = 25.0  # Slightly looser than READY

# ========================================
# TRAP DETECTION
# ========================================
# Identify potential trap conditions (extended wicks, weak bodies)
TRAP_WICK_RATIO_MAX = 0.7  # If WickRatio > 0.7 (70% wick)
TRAP_BODY_RATIO_MAX = 0.3  # AND BodyRatio < 0.3 (30% body) = potential rejection

# ========================================
# SCORING SYSTEM
# ========================================
# Points awarded for meeting each criterion (total = 100)
SCORE_VWMA_ABOVE = 20  # Close > VWMA20
SCORE_REL_VOL = 20  # Rel_Vol >= 1.2
SCORE_CLOSE_LOC = 20  # CloseLocation >= 0.60
SCORE_BODY_RATIO = 20  # BodyRatio >= 0.45
SCORE_VWMA_TIGHT = 10  # VWMA_Dist <= 10% (bonus for tight price)
SCORE_TREND_OK = 10  # TrendOK = True

# ========================================
# BACKTEST PARAMETERS
# ========================================
BACKTEST_HOLD_DAYS = 5  # Hold period in trading days
BACKTEST_TOP_N = 5  # Number of top READY candidates to select daily
BACKTEST_COST_BPS = 30  # Transaction cost in basis points (0.30% round-trip)
BACKTEST_START_DATE = "2024-01-01"  # Default backtest start date
BACKTEST_END_DATE = "2024-12-31"  # Default backtest end date

# ========================================
# OUTPUT SETTINGS
# ========================================
OUTPUT_DIR = "."  # Directory for CSV outputs (current directory)
OUTPUT_PREFIX_SCREENER = "idx_vwap_daily"  # Prefix for daily screener output
OUTPUT_PREFIX_BACKTEST = "idx_backtest"  # Prefix for backtest results
CONSOLE_TOP_N = 5  # Number of top candidates to display in console

# ========================================
# DATA FETCHING
# ========================================
FETCH_PERIOD = "6mo"  # Yahoo Finance period (6 months to ensure 60+ trading days)
FETCH_INTERVAL = "1d"  # Daily data
MAX_WORKERS = 10  # Concurrent workers for data fetching

# ========================================
# TECHNICAL INDICATOR PERIODS
# ========================================
VWMA_PERIOD = 20
EMA_FAST_PERIOD = 20
EMA_SLOW_PERIOD = 50
VOL_SMA_PERIOD = 20
ADR_PERIOD = 20
VALUE_SMA_PERIOD = 20
