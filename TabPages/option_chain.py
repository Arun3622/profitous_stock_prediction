"""
Option Chain Page Module
Handles option chain data display and analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from fyers_client import FyersClient
from utils import get_expiry_dates
from ui_components import render_live_indicator


def render_option_chain_page(client: Optional[FyersClient]):
    """Render the option chain page"""
    st.header("🎯 Live Option Chain")
    
    if not client:
        st.warning("🔌 Connect to Fyers API to view option chain")
        return
    
    # Controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        symbol = st.selectbox("Index", ["NIFTY50", "BANKNIFTY", "FINNIFTY"])
        st.session_state['selected_option_symbol'] = symbol
    
    with col2:
        expiries = get_expiry_dates(4)
        expiry = st.selectbox("Expiry", expiries)
    
    with col3:
        strike_count = st.selectbox("Strikes", [10, 20, 30, 40, 50], index=2)
    
    with col4:
        if st.button("🔄 Fetch Chain", type="primary", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Fetch and display option chain
    with st.spinner("Loading option chain..."):
        try:
            option_data = client.fetch_option_chain(symbol, expiry, strike_count)
            
            if option_data.get("s") == "ok":
                chain_data = option_data.get("data", {})
                options = chain_data.get("optionsChain", [])
                
                if options:
                    render_live_indicator()
                    
                    # Parse option data
                    calls, puts = parse_option_data(options, strike_count)
                    
                    # Display call and put tables
                    col_call, col_put = st.columns(2)
                    
                    with col_call:
                        st.markdown("### 📞 CALL Options")
                        df_calls = pd.DataFrame(calls)
                        st.dataframe(df_calls, use_container_width=True, height=600)
                    
                    with col_put:
                        st.markdown("### 📉 PUT Options")
                        df_puts = pd.DataFrame(puts)
                        st.dataframe(df_puts, use_container_width=True, height=600)
                    
                    # Display summary
                    render_option_summary(calls, puts)
                else:
                    st.warning("No option chain data available")
            else:
                st.error(f"❌ API Error: {option_data.get('message', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {e}")


def parse_option_data(options: list, strike_count: int) -> tuple:
    """Parse option chain data into calls and puts"""
    # Create a mapping strike -> {'call': {...}, 'put': {...}}
    strikes_map = {}

    for opt in options:
        strike = opt.get("strike_price")
        # Skip entries which are underlying or invalid
        if strike is None or (isinstance(strike, (int, float)) and strike <= 0):
            continue

        # Handle nested structure: opt contains 'call' and/or 'put'
        if "call" in opt or "put" in opt:
            call_data = opt.get("call") or {}
            put_data = opt.get("put") or {}
            if call_data:
                strikes_map.setdefault(strike, {})["call"] = {
                    "ltp": call_data.get("ltp", 0),
                    "oi": call_data.get("oi", 0),
                    "volume": call_data.get("volume", 0),
                    "iv": call_data.get("iv", 0),
                }
            if put_data:
                strikes_map.setdefault(strike, {})["put"] = {
                    "ltp": put_data.get("ltp", 0),
                    "oi": put_data.get("oi", 0),
                    "volume": put_data.get("volume", 0),
                    "iv": put_data.get("iv", 0),
                }
        else:
            # Flat structure: opt itself is an option with option_type
            opt_type = (opt.get("option_type") or "").upper()
            if opt_type == "CE":
                strikes_map.setdefault(strike, {})["call"] = {
                    "ltp": opt.get("ltp", 0),
                    "oi": opt.get("oi", 0),
                    "volume": opt.get("volume", 0),
                    "iv": opt.get("iv", 0),
                }
            elif opt_type == "PE":
                strikes_map.setdefault(strike, {})["put"] = {
                    "ltp": opt.get("ltp", 0),
                    "oi": opt.get("oi", 0),
                    "volume": opt.get("volume", 0),
                    "iv": opt.get("iv", 0),
                }
            else:
                # Unknown entry type - skip
                continue

    # Build paired lists for display (sorted by strike)
    calls = []
    puts = []

    strikes_sorted = sorted(strikes_map.keys())[:strike_count]
    for strike in strikes_sorted:
        data = strikes_map.get(strike, {})
        call = data.get("call", {})
        put = data.get("put", {})

        calls.append({
            "Strike": strike,
            "CE LTP": call.get("ltp", 0),
            "CE OI": call.get("oi", 0),
            "CE Volume": call.get("volume", 0),
            "CE IV": call.get("iv", 0),
        })

        puts.append({
            "Strike": strike,
            "PE LTP": put.get("ltp", 0),
            "PE OI": put.get("oi", 0),
            "PE Volume": put.get("volume", 0),
            "PE IV": put.get("iv", 0),
        })

    return calls, puts


def render_option_summary(calls: list, puts: list):
    """Render option chain summary metrics"""
    st.markdown("---")
    st.subheader("📊 Option Chain Summary")
    # Sum safely, tolerating None values
    total_call_oi = sum([ (c.get("CE OI") or 0) for c in calls ])
    total_put_oi = sum([ (p.get("PE OI") or 0) for p in puts ])
    pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Call OI", f"{total_call_oi:,.0f}")
    with col2:
        st.metric("Put OI", f"{total_put_oi:,.0f}")
    with col3:
        st.metric("PCR", f"{pcr:.2f}")
    with col4:
        sentiment = "🟢 Bullish" if pcr > 1.2 else "🔴 Bearish" if pcr < 0.8 else "⚪ Neutral"
        st.metric("Sentiment", sentiment)
