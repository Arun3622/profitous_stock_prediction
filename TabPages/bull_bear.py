"""
Bull/Bear Dashboard Page Module
Handles sector analysis and bull/bear stock screening
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from fyers_client import FyersClient
from config import SECTOR_INDICES, SCAN_SYMBOLS, AVAILABLE_SECTORS
from data_processor import build_df_from_quotes, classify_row_advanced, apply_filters
from ui_components import render_live_indicator


def render_sector_performance(client: FyersClient):
    """Render sector performance section"""
    st.subheader("📊 Live Sector Performance")
    
    try:
        sector_symbols = list(SECTOR_INDICES.values())
        resp = client.fetch_quotes(sector_symbols)
        
        sector_data = []
        for item in resp.get("d", []):
            v = item.get("v", {})
            symbol = item.get("n", "")
            
            sector_name = None
            for name, sym in SECTOR_INDICES.items():
                if sym in symbol:
                    sector_name = name
                    break
            
            if sector_name:
                ltp = float(v.get("lp") or v.get("ltp") or 0)
                prev = float(v.get("prev_close_price", ltp) or ltp)
                chg = ltp - prev
                chg_pct = (chg / prev * 100) if prev > 0 else 0
                
                sector_data.append({
                    'Sector': sector_name,
                    'Last': round(ltp, 2),
                    'Change': round(chg, 2),
                    'Change %': round(chg_pct, 2),
                    'Status': '🟢 Bullish' if chg_pct > 0.5 else '🔴 Bearish' if chg_pct < -0.5 else '⚪ Neutral'
                })
        
        if sector_data:
            df_sectors = pd.DataFrame(sector_data)
            df_sectors = df_sectors.sort_values('Change %', ascending=False)
            
            def color_sector(val):
                try:
                    v = float(val)
                    color = '#00cc96' if v > 0 else '#ef553b' if v < 0 else 'white'
                    return f'color: {color}; font-weight: bold'
                except:
                    return ''
            
            styled = df_sectors.style.applymap(color_sector, subset=['Change', 'Change %'])
            st.dataframe(styled, use_container_width=True, height=400)
    except Exception as e:
        st.error(f"Sector data error: {e}")


def render_stock_scanner(client: FyersClient):
    """Render stock scanner section"""
    st.subheader("🎯 Stock Analysis Scanner")
    
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        sector_filter = st.multiselect(
            "🔍 Filter by Sector (Optional)",
            options=AVAILABLE_SECTORS,
            default=["All"]
        )
    
    with col_filter2:
        min_volume_ratio = st.slider("Min Volume Ratio", 1.0, 5.0, 2.0, 0.5)
    
    st.markdown("---")
    
    with st.spinner("🔍 Scanning for TODAY'S breakouts..."):
        try:
            resp = client.fetch_quotes(SCAN_SYMBOLS)
            df = build_df_from_quotes(resp, client)
            
            if not df.empty:
                # Apply classification logic
                df["daily_tag"] = df.apply(lambda r: classify_row_advanced(r), axis=1)
                
                # Apply filters
                df = apply_filters(df, sector_filter, min_volume_ratio)
                
                # Show summary metrics
                render_summary_metrics(df)
                
                st.markdown("---")
                
                # View selector
                view_type = st.radio(
                    "View",
                    ["🟢 Bullish Breakouts", "🔴 Bearish Breakouts", "📊 Both"],
                    horizontal=True
                )
                
                if view_type == "🟢 Bullish Breakouts":
                    render_bullish_stocks(df)
                elif view_type == "🔴 Bearish Breakouts":
                    render_bearish_stocks(df)
                else:
                    render_both_views(df)
            else:
                st.warning("No data available")
        except Exception as e:
            st.error(f"Error: {e}")


def render_summary_metrics(df: pd.DataFrame):
    """Render summary metrics"""
    st.subheader("📊 Today's Breakout Stocks")
    
    total_bulls = len(df[df["daily_tag"] == "bull"])
    total_bears = len(df[df["daily_tag"] == "bear"])
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("🟢 Bullish Breakouts", total_bulls)
    with metric_col2:
        st.metric("🔴 Bearish Breakouts", total_bears)
    with metric_col3:
        st.metric("📊 Total Scanned", len(df))
    with metric_col4:
        sentiment_ratio = total_bulls / (total_bulls + total_bears) if (total_bulls + total_bears) > 0 else 0.5
        market_mood = "🟢 Bullish" if sentiment_ratio > 0.6 else "🔴 Bearish" if sentiment_ratio < 0.4 else "⚪ Neutral"
        st.metric("Market Mood", market_mood)


def render_bullish_stocks(df: pd.DataFrame):
    """Render bullish stocks table"""
    bulls = df[df["daily_tag"] == "bull"].copy()
    
    if not bulls.empty:
        bulls['Price Change %'] = ((bulls["current_close"] - bulls["prev_close"]) / bulls["prev_close"] * 100).round(2)
        bulls['Vol Ratio'] = (bulls["vol_current"] / bulls["vol_20_avg"]).round(2)
        bulls['OI Change %'] = ((bulls["oi_current"] - bulls["oi_prev"]) / bulls["oi_prev"] * 100).round(2)
        bulls['Above PWH'] = (bulls["current_close"] > bulls["prev_week_high"])
        
        bulls_display = bulls[["symbol", "name", "sector", "current_close", "prev_week_high", 
                              "Price Change %", "Vol Ratio", "OI Change %", "Above PWH"]]
        bulls_display.columns = ["Symbol", "Name", "Sector", "LTP", "Prev Week High", 
                                "Price Chg %", "Vol (x Avg)", "OI Chg %", "Breakout"]
        
        st.success(f"✅ {len(bulls)} Fresh BULLISH Breakouts Today")
        
        def color_bull(val):
            try:
                if isinstance(val, bool):
                    return 'color: #00cc96; font-weight: bold' if val else ''
                v = float(val)
                return 'color: #00cc96; font-weight: bold' if v > 0 else ''
            except:
                return ''
        
        styled = bulls_display.style.applymap(color_bull, subset=['Price Chg %', 'Vol (x Avg)', 'OI Chg %', 'Breakout'])
        st.dataframe(styled, use_container_width=True, height=500)
        
        # Export option
        csv = bulls_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Bullish Stocks (CSV)",
            data=csv,
            file_name=f"bullish_breakouts_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info("**Criteria:** Price > Weekly High ✅ | Volume > 2x Avg ✅ | OI Change > 10% ✅")
    else:
        st.info("✨ No fresh BULLISH breakouts detected today based on the criteria")


def render_bearish_stocks(df: pd.DataFrame):
    """Render bearish stocks table"""
    bears = df[df["daily_tag"] == "bear"].copy()
    
    if not bears.empty:
        bears['Price Change %'] = ((bears["current_close"] - bears["prev_close"]) / bears["prev_close"] * 100).round(2)
        bears['Vol Ratio'] = (bears["vol_current"] / bears["vol_20_avg"]).round(2)
        bears['OI Change %'] = ((bears["oi_current"] - bears["oi_prev"]) / bears["oi_prev"] * 100).round(2)
        bears['Below PWL'] = (bears["current_close"] < bears["prev_week_low"])
        
        bears_display = bears[["symbol", "name", "sector", "current_close", "prev_week_low",
                              "Price Change %", "Vol Ratio", "OI Change %", "Below PWL"]]
        bears_display.columns = ["Symbol", "Name", "Sector", "LTP", "Prev Week Low",
                               "Price Chg %", "Vol (x Avg)", "OI Chg %", "Breakdown"]
        
        st.error(f"⚠️ {len(bears)} Fresh BEARISH Breakdowns Today")
        
        def color_bear(val):
            try:
                if isinstance(val, bool):
                    return 'color: #ef553b; font-weight: bold' if val else ''
                v = float(val)
                return 'color: #ef553b; font-weight: bold' if v < 0 else ''
            except:
                return ''
        
        styled = bears_display.style.applymap(color_bear, subset=['Price Chg %', 'Vol (x Avg)', 'OI Chg %', 'Breakdown'])
        st.dataframe(styled, use_container_width=True, height=500)
        
        # Export option
        csv = bears_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Bearish Stocks (CSV)",
            data=csv,
            file_name=f"bearish_breakouts_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info("**Criteria:** Price < Weekly Low ✅ | Volume > 2x Avg ✅ | OI Change > 10% ✅")
    else:
        st.info("✨ No fresh BEARISH breakdowns detected today based on the criteria")


def render_both_views(df: pd.DataFrame):
    """Render both bullish and bearish views side by side"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🟢 Bullish Breakouts")
        bulls = df[df["daily_tag"] == "bull"].copy()
        
        if not bulls.empty:
            bulls['Chg %'] = ((bulls["current_close"] - bulls["prev_close"]) / bulls["prev_close"] * 100).round(2)
            bulls['Vol'] = (bulls["vol_current"] / bulls["vol_20_avg"]).round(1)
            
            bulls_display = bulls[["symbol", "current_close", "Chg %", "Vol"]].copy()
            bulls_display.columns = ["Symbol", "LTP", "Chg %", "Vol x"]
            
            st.success(f"✅ {len(bulls)} stocks")
            
            def color_pos(val):
                return 'color: #00cc96; font-weight: bold'
            
            styled = bulls_display.style.applymap(color_pos, subset=['Chg %', 'Vol x'])
            st.dataframe(styled, use_container_width=True, height=450)
        else:
            st.info("No bullish breakouts today")
    
    with col2:
        st.markdown("#### 🔴 Bearish Breakouts")
        bears = df[df["daily_tag"] == "bear"].copy()
        
        if not bears.empty:
            bears['Chg %'] = ((bears["current_close"] - bears["prev_close"]) / bears["prev_close"] * 100).round(2)
            bears['Vol'] = (bears["vol_current"] / bears["vol_20_avg"]).round(1)
            
            bears_display = bears[["symbol", "current_close", "Chg %", "Vol"]].copy()
            bears_display.columns = ["Symbol", "LTP", "Chg %", "Vol x"]
            
            st.error(f"⚠️ {len(bears)} stocks")
            
            def color_neg(val):
                return 'color: #ef553b; font-weight: bold'
            
            styled = bears_display.style.applymap(color_neg, subset=['Chg %', 'Vol x'])
            st.dataframe(styled, use_container_width=True, height=450)
        else:
            st.info("No bearish breakouts today")
    
    st.markdown("---")
    st.info("""
    **📋 Detection Criteria:**
    - **Bullish:** Current > Weekly High + Volume > 2x Avg + OI Change > 10%
    - **Bearish:** Current < Weekly Low + Volume > 2x Avg + OI Change > 10%
    """)


def render_bull_bear_page(client: Optional[FyersClient]):
    """Main function to render bull/bear dashboard page"""
    st.header("🎯 Bull/Bear Analysis - Today's Fresh Breakouts")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        render_live_indicator("LIVE ANALYSIS")
        st.caption("Only showing TODAY'S fresh breakouts based on: Price vs Weekly High/Low + 2x Volume + 10% OI Change")
    with col2:
        if st.button("🔄 Scan Now", type="primary", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    if not client:
        st.warning("🔌 Connect to Fyers API to view analysis")
        return
    
    # Render sector performance
    render_sector_performance(client)
    
    st.markdown("---")
    
    # Render stock scanner
    render_stock_scanner(client)
