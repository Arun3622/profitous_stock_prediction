"""
Data Processing Module
Handles data transformation, classification logic, and analysis
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import STOCK_UNIVERSE
from fyers_client import FyersClient


def percent_change(old: float, new: float) -> float:
    """Calculate percentage change between two values"""
    try:
        if old == 0:
            return 0.0
        return (new - old) / abs(old) * 100.0
    except:
        return 0.0


def build_df_from_quotes(quotes_json: Dict, client: FyersClient) -> pd.DataFrame:
    """Build dataframe from Fyers quotes with historical data for volume analysis"""
    records = []
    
    # Get date range for historical data (last 30 days to get sufficient data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    date_from = int(start_date.timestamp())
    date_to = int(end_date.timestamp())
    
    for item in quotes_json.get("d", []):
        try:
            n = item.get("n") or item.get("symbol")
            v = item.get("v", {})
            short = n.split(":")[-1].replace("-EQ", "").replace("-INDEX", "") if n else None
            
            sector = STOCK_UNIVERSE.get(short, "Unknown")
            
            ltp = float(v.get("lp") or v.get("ltp") or 0)
            prev_close = float(v.get("prev_close_price", ltp) or ltp)
            current_vol = float(v.get("volume", 0) or 0)
            oi = float(v.get("open_interest", 0) or 0)
            prev_oi = float(v.get("prev_open_interest", oi) or oi)
            
            # Fetch historical data for this symbol
            hist_data = client.fetch_history(n, "5", str(date_from), str(date_to))
            
            # Calculate 20-period average volume from 5-minute candles
            vol_20_avg = 100000  # Default
            prev_week_high = prev_close * 1.05
            prev_week_low = prev_close * 0.95
            
            if hist_data and hist_data.get("s") == "ok" and hist_data.get("candles"):
                candles = hist_data.get("candles", [])
                if len(candles) >= 20:
                    # Get last 20 candles' volume
                    last_20_vols = [c[5] for c in candles[-20:]]  # Volume is at index 5
                    vol_20_avg = sum(last_20_vols) / 20
                    
                    # Get actual weekly high and low
                    last_week_highs = [c[2] for c in candles[-288:]]  # ~1 week of 5-min candles
                    last_week_lows = [c[3] for c in candles[-288:]]
                    if last_week_highs:
                        prev_week_high = max(last_week_highs)
                        prev_week_low = min(last_week_lows)
            
            records.append({
                "symbol": short or n,
                "name": v.get("description", short or n),
                "sector": sector,
                "current_close": ltp,
                "prev_close": prev_close,
                "prev_day_high": prev_close * 1.02,
                "prev_day_low": prev_close * 0.98,
                "prev_week_high": prev_week_high,
                "prev_week_low": prev_week_low,
                "oi_prev": prev_oi,
                "oi_current": oi,
                "iv_prev_high": 20.0,
                "iv_current": 22.0,
                "vol_20_avg": vol_20_avg,
                "vol_current": current_vol,
            })
        except Exception as e:
            continue
    
    return pd.DataFrame(records)


def check_resistance_weakening(row: pd.Series, option_data: Optional[Dict]) -> bool:
    """
    Check if resistance is weakening:
    - Put addition (long buildup) OR
    - Call unwinding (short covering)
    """
    if not option_data:
        return True
    
    try:
        ltp = row["current_close"]
        
        # Find strikes near current price (within 2%)
        nearby_strikes = []
        for opt in option_data.get("optionsChain", []):
            strike = opt.get("strike_price", 0)
            if abs(strike - ltp) / ltp <= 0.02:  # Within 2%
                nearby_strikes.append(opt)
        
        for strike_data in nearby_strikes:
            put_data = strike_data.get("put", {})
            call_data = strike_data.get("call", {})
            
            # Put OI increase (long buildup)
            put_oi_chg = percent_change(
                put_data.get("prev_oi", put_data.get("oi", 0)),
                put_data.get("oi", 0)
            )
            
            # Call OI decrease (unwinding)
            call_oi_chg = percent_change(
                call_data.get("prev_oi", call_data.get("oi", 0)),
                call_data.get("oi", 0)
            )
            
            if put_oi_chg > 10 or call_oi_chg < -10:
                return True
        
        return False
    except:
        return True  # Default to True if option data unavailable


def check_support_weakening(row: pd.Series, option_data: Optional[Dict]) -> bool:
    """
    Check if support is weakening:
    - Call addition (short buildup) OR
    - Put unwinding (long covering)
    """
    if not option_data:
        return True
    
    try:
        ltp = row["current_close"]
        
        # Find strikes near current price
        nearby_strikes = []
        for opt in option_data.get("optionsChain", []):
            strike = opt.get("strike_price", 0)
            if abs(strike - ltp) / ltp <= 0.02:
                nearby_strikes.append(opt)
        
        for strike_data in nearby_strikes:
            put_data = strike_data.get("put", {})
            call_data = strike_data.get("call", {})
            
            # Call OI increase (short buildup)
            call_oi_chg = percent_change(
                call_data.get("prev_oi", call_data.get("oi", 0)),
                call_data.get("oi", 0)
            )
            
            # Put OI decrease (unwinding)
            put_oi_chg = percent_change(
                put_data.get("prev_oi", put_data.get("oi", 0)),
                put_data.get("oi", 0)
            )
            
            if call_oi_chg > 10 or put_oi_chg < -10:
                return True
        
        return False
    except:
        return True


def classify_row_advanced(row: pd.Series, option_data: Optional[Dict] = None) -> Optional[str]:
    """
    Enhanced classification logic:
    
    BULLISH:
    1) Current price > Previous Week High
    2) Current 5-min volume > 2x (20-period average volume)
    3) OI change > 10%
    4) Put addition OR Call unwinding (resistance weakening)
    
    BEARISH:
    1) Current price < Previous Week Low
    2) Current 5-min volume > 2x (20-period average volume)
    3) OI change > 10%
    4) Call addition OR Put unwinding (support weakening)
    """
    try:
        ltp = row["current_close"]
        pwh = row["prev_week_high"]
        pwl = row["prev_week_low"]
        
        # Volume check: current volume should be 2x the 20-period average
        vol_ratio = row["vol_current"] / row["vol_20_avg"] if row["vol_20_avg"] > 0 else 0
        vol_condition = vol_ratio >= 2.0
        
        # OI change > 10%
        oi_pct = percent_change(row["oi_prev"], row["oi_current"])
        oi_condition = abs(oi_pct) > 10
        
        # Price conditions
        price_above_pwh = ltp > pwh
        price_below_pwl = ltp < pwl
        
        # Determine classification
        if price_above_pwh and vol_condition and oi_condition:
            # Check option confirmation if available
            if option_data:
                resistance_weakening = check_resistance_weakening(row, option_data)
                if resistance_weakening:
                    return "bull"
            else:
                # Without option data, use price + volume + OI
                return "bull"
        
        elif price_below_pwl and vol_condition and oi_condition:
            # Check option confirmation if available
            if option_data:
                support_weakening = check_support_weakening(row, option_data)
                if support_weakening:
                    return "bear"
            else:
                # Without option data, use price + volume + OI
                return "bear"
        
        return None
    except Exception as e:
        return None


def apply_filters(df: pd.DataFrame, sector_filter: List[str], 
                 min_volume_ratio: float) -> pd.DataFrame:
    """Apply sector and volume filters to dataframe"""
    # Apply sector filter
    if "All" not in sector_filter and sector_filter:
        df = df[df["sector"].isin(sector_filter)]
    
    # Apply volume filter
    df["vol_ratio"] = df["vol_current"] / df["vol_20_avg"]
    df = df[df["vol_ratio"] >= min_volume_ratio]
    
    return df


def calculate_pnl_summary(holdings_data: Dict, positions_data: Dict) -> Dict[str, float]:
    """Calculate P&L summary from holdings and positions"""
    holdings_pnl = 0.0
    positions_pnl = 0.0
    
    # Calculate holdings P&L
    if holdings_data and holdings_data.get("s") == "ok":
        holdings_list = holdings_data.get("holdings", [])
        for holding in holdings_list:
            try:
                qty = float(holding.get("quantity", 0) or 0)
                buy_price = float(holding.get("costPrice", 0) or 0)
                ltp = float(holding.get("ltp", 0) or 0)
                pnl = (ltp - buy_price) * qty
                holdings_pnl += pnl
            except:
                continue
    
    # Calculate positions P&L
    if positions_data and positions_data.get("s") == "ok":
        net_positions = positions_data.get("netPositions", [])
        for position in net_positions:
            try:
                realized_pl = float(position.get("realized_profit", 0) or 0)
                unrealized_pl = float(position.get("unrealized_profit", 0) or 0)
                pnl = realized_pl + unrealized_pl
                positions_pnl += pnl
            except:
                continue
    
    return {
        "total_pnl": holdings_pnl + positions_pnl,
        "holdings_pnl": holdings_pnl,
        "positions_pnl": positions_pnl
    }
