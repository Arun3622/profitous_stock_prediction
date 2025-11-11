"""
Watchlist Page Module
Handles live watchlist functionality with search and symbol management
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import Optional
from fyers_client import FyersClient
from config import STOCK_UNIVERSE
from ui_components import render_live_indicator, render_search_suggestions


def render_watchlist_page(client: Optional[FyersClient]):
    """Render the watchlist page"""
    st.header("📈 Live Watchlist")
    
    # Search with suggestions
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "🔍 Search & Add Stocks",
            placeholder="Type: TCS, RELIANCE, INFY...",
            key="search_stock"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Smart suggestions
    render_search_suggestions(search_term, list(STOCK_UNIVERSE.keys()))
    
    st.markdown("---")
    st.subheader("📋 Live Watchlist")
    
    if st.session_state.watchlist_symbols and client:
        watchlist_placeholder = st.empty()
        
        try:
            # Fetch quotes for watchlist symbols
            fyers_symbols = [f"NSE:{s}-EQ" for s in st.session_state.watchlist_symbols]
            resp = client.fetch_quotes(fyers_symbols)
            
            watchlist_data = []
            for item in resp.get("d", []):
                v = item.get("v", {})
                symbol = item.get("n", "").split(":")[-1].replace("-EQ", "")
                ltp = float(v.get("lp") or v.get("ltp") or 0)
                prev = float(v.get("prev_close_price", ltp) or ltp)
                chg = ltp - prev
                chg_pct = (chg / prev * 100) if prev > 0 else 0
                
                watchlist_data.append({
                    'Symbol': symbol,
                    'LTP': round(ltp, 2),
                    'Prev Close': round(prev, 2),
                    'Change': round(chg, 2),
                    'Change (%)': round(chg_pct, 2),
                    'Status': '🟢 Bull' if chg_pct > 1 else '🔴 Bear' if chg_pct < -1 else '⚪ Neutral'
                })
            
            if watchlist_data:
                df_watch = pd.DataFrame(watchlist_data)
                
                with watchlist_placeholder:
                    render_live_indicator()
                    
                    def color_chg(val):
                        try:
                            v = float(val)
                            color = '#00cc96' if v > 0 else '#ef553b' if v < 0 else 'white'
                            return f'color: {color}; font-weight: bold'
                        except:
                            return ''
                    
                    styled = df_watch.style.applymap(color_chg, subset=['Change', 'Change (%)'])
                    st.dataframe(styled, use_container_width=True, height=400)
        except Exception as e:
            st.error(f"Error loading watchlist: {e}")
    elif not client:
        st.warning("🔌 Connect to Fyers API to view live data")
    
    # Remove symbol section
    if st.session_state.watchlist_symbols:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            remove_sym = st.selectbox(
                "🗑️ Remove Symbol",
                [''] + st.session_state.watchlist_symbols
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if remove_sym and st.button("Remove", use_container_width=True, type="secondary"):
                st.session_state.watchlist_symbols.remove(remove_sym)
                st.success(f"Removed {remove_sym}")
                time.sleep(0.5)
                st.rerun()
