"""
Utility Functions Module
Contains helper functions used across the application
"""

from datetime import datetime, timedelta
from typing import List


def get_expiry_dates(count: int = 4) -> List[str]:
    """
    Get next N Thursday expiry dates (weekly expiries for options)
    
    Args:
        count: Number of expiry dates to return
        
    Returns:
        List of expiry dates in YYYY-MM-DD format
    """
    today = datetime.now()
    expiries = []
    
    for i in range(28):  # Check next 28 days
        date = today + timedelta(days=i)
        if date.weekday() == 3:  # Thursday
            expiries.append(date.strftime("%Y-%m-%d"))
        if len(expiries) == count:
            break
    
    return expiries


def format_large_number(num: float) -> str:
    """Format large numbers with commas and 2 decimal places"""
    return f"{num:,.2f}"


def color_positive_negative(val: float) -> str:
    """Return color style for positive/negative values"""
    if val > 0:
        return 'color: #00cc96; font-weight: bold'
    elif val < 0:
        return 'color: #ef553b; font-weight: bold'
    return 'color: white'


def get_sentiment_indicator(value: float, thresholds: dict) -> str:
    """
    Get sentiment indicator based on value and thresholds
    
    Args:
        value: The value to evaluate
        thresholds: Dict with 'bullish' and 'bearish' threshold values
        
    Returns:
        Sentiment string with emoji
    """
    if value > thresholds.get('bullish', 0):
        return "🟢 Bullish"
    elif value < thresholds.get('bearish', 0):
        return "🔴 Bearish"
    return "⚪ Neutral"


def format_timestamp(format_str: str = '%H:%M:%S') -> str:
    """Get current timestamp in specified format"""
    return datetime.now().strftime(format_str)


def search_symbols(search_term: str, symbol_list: List[str], max_results: int = 10) -> List[str]:
    """
    Smart symbol search with exact match priority
    
    Args:
        search_term: Search string
        symbol_list: List of available symbols
        max_results: Maximum results to return
        
    Returns:
        Sorted list of matching symbols (exact, starts_with, contains)
    """
    if not search_term:
        return []
    
    search_upper = search_term.upper().strip()
    
    # Find exact match first
    exact_match = [s for s in symbol_list if s == search_upper]
    
    # Find related matches (starts with or contains)
    starts_with = [s for s in symbol_list if s.startswith(search_upper) and s not in exact_match]
    contains = [s for s in symbol_list if search_upper in s and s not in exact_match and s not in starts_with]
    
    # Combine: exact first, then starts_with, then contains
    return (exact_match + starts_with + contains)[:max_results]
