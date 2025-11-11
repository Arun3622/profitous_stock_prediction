"""
Account Overview Page Module
Handles account balance, holdings, positions, and P&L display
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from fyers_client import FyersClient
from data_processor import calculate_pnl_summary
from ui_components import render_live_indicator, render_pnl_card, render_styled_metric


def render_account_page(client: Optional[FyersClient]):
    """Render the account overview page"""
    st.header("💼 Account Overview")
    
    if not client:
        st.warning("🔌 Connect to Fyers API to view account")
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        render_live_indicator()
    with col2:
        if st.button("🔄 Refresh", type="primary", use_container_width=True):
            st.rerun()
    
    # Fetch account data
    with st.spinner("Loading account data..."):
        funds_data = client.fetch_funds()
        holdings_data = client.fetch_holdings()
        positions_data = client.fetch_positions()
    
    # Calculate P&L
    pnl_summary = calculate_pnl_summary(holdings_data, positions_data)
    
    # Render P&L summary
    render_pnl_summary(pnl_summary)
    
    st.markdown("---")
    
    # Render funds section
    render_funds_section(funds_data)
    
    st.markdown("---")
    
    # Render holdings section
    render_holdings_section(holdings_data, pnl_summary['holdings_pnl'])
    
    st.markdown("---")
    
    # Render positions section
    render_positions_section(positions_data, pnl_summary['positions_pnl'])


def render_pnl_summary(pnl_summary: dict):
    """Render P&L summary section"""
    st.markdown("### 💹 Live P&L Summary")
    
    total_pnl = pnl_summary['total_pnl']
    holdings_pnl = pnl_summary['holdings_pnl']
    positions_pnl = pnl_summary['positions_pnl']
    
    render_pnl_card(total_pnl, "Total Profit/Loss (Live)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        color1 = "#00cc96" if holdings_pnl >= 0 else "#ef553b"
        render_styled_metric("Holdings P&L", holdings_pnl, color1)
    
    with col2:
        color2 = "#00cc96" if positions_pnl >= 0 else "#ef553b"
        render_styled_metric("Positions P&L", positions_pnl, color2)


def render_funds_section(funds_data: dict):
    """Render account funds section"""
    st.subheader("💰 Account Funds")
    
    if funds_data and funds_data.get("s") == "ok":
        fund_limit = funds_data.get("fund_limit", [{}])[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💵 Total", f"₹{fund_limit.get('equityAmount', 0):,.2f}")
        with col2:
            st.metric("✅ Available", f"₹{fund_limit.get('availablecash', 0):,.2f}")
        with col3:
            margin = fund_limit.get('utilized_amount', 0)
            st.metric("📊 Used", f"₹{margin:,.2f}")
        with col4:
            st.metric("🔒 Collateral", f"₹{fund_limit.get('collateral', 0):,.2f}")
    else:
        st.info("No funds data available")


def render_holdings_section(holdings_data: dict, holdings_pnl: float):
    """Render holdings section"""
    st.subheader("📊 Holdings")
    
    if holdings_data and holdings_data.get("s") == "ok":
        holdings_list = holdings_data.get("holdings", [])
        
        if holdings_list:
            holdings_display = []
            for h in holdings_list:
                try:
                    symbol = h.get("symbol", "").split(":")[-1].replace("-EQ", "")
                    qty = float(h.get("quantity", 0) or 0)
                    avg = float(h.get("costPrice", 0) or 0)
                    ltp = float(h.get("ltp", 0) or 0)
                    pnl = (ltp - avg) * qty
                    pnl_pct = ((ltp - avg) / avg * 100) if avg > 0 else 0
                    
                    holdings_display.append({
                        "Symbol": symbol,
                        "Qty": int(qty),
                        "Avg": round(avg, 2),
                        "LTP": round(ltp, 2),
                        "P&L": round(pnl, 2),
                        "P&L %": round(pnl_pct, 2)
                    })
                except:
                    continue
            
            if holdings_display:
                df_h = pd.DataFrame(holdings_display)
                
                def color_pnl(val):
                    try:
                        v = float(val)
                        if v > 0:
                            return 'color: #00cc96; font-weight: bold'
                        elif v < 0:
                            return 'color: #ef553b; font-weight: bold'
                        else:
                            return 'color: white'
                    except:
                        return 'color: white'
                
                styled = df_h.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                st.dataframe(styled, use_container_width=True, height=350)
                st.success(f"✅ Total Holdings P&L: ₹{holdings_pnl:,.2f}")
            else:
                st.info("No holdings data")
        else:
            st.info("📭 No holdings")
    else:
        st.info("📭 No holdings data")


def render_positions_section(positions_data: dict, positions_pnl: float):
    """Render open positions section"""
    st.subheader("📈 Open Positions")
    
    if positions_data and positions_data.get("s") == "ok":
        pos_list = positions_data.get("netPositions", [])
        
        if pos_list:
            pos_display = []
            for p in pos_list:
                try:
                    symbol = p.get("symbol", "").split(":")[-1]
                    qty = float(p.get("qty", 0) or 0)
                    avg = float(p.get("avgPrice", 0) or 0)
                    ltp = float(p.get("ltp", 0) or 0)
                    
                    realized = float(p.get("realized_profit", 0) or 0)
                    unrealized = float(p.get("unrealized_profit", 0) or 0)
                    pnl = realized + unrealized
                    
                    pnl_pct = ((ltp - avg) / avg * 100) if avg > 0 else 0
                    
                    pos_display.append({
                        "Symbol": symbol,
                        "Qty": int(qty),
                        "Avg": round(avg, 2),
                        "LTP": round(ltp, 2),
                        "P&L": round(pnl, 2),
                        "P&L %": round(pnl_pct, 2)
                    })
                except:
                    continue
            
            if pos_display:
                df_p = pd.DataFrame(pos_display)
                
                def color_pnl(val):
                    try:
                        v = float(val)
                        if v > 0:
                            return 'color: #00cc96; font-weight: bold'
                        elif v < 0:
                            return 'color: #ef553b; font-weight: bold'
                        else:
                            return 'color: white'
                    except:
                        return 'color: white'
                
                styled = df_p.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                st.dataframe(styled, use_container_width=True, height=350)
                st.success(f"✅ Total Positions P&L: ₹{positions_pnl:,.2f}")
            else:
                st.info("No position data")
        else:
            st.info("📭 No open positions")
    else:
        st.info("📭 No position data")
