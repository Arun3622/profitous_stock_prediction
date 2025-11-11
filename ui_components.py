"""
UI Components Module
Contains reusable Streamlit UI components and styling functions
"""

import streamlit as st
import pandas as pd
import uuid
from typing import Optional
from config import FYERS_CLIENT_ID, FYERS_CLIENT_SECRET, FYERS_REDIRECT_URI
from fyers_client import FyersClient


def render_custom_css():
    """Render custom CSS styling"""
    from config import CUSTOM_CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar_auth():
    """Render authentication section in sidebar"""
    with st.sidebar:
        st.markdown("## 🔑 Fyers API Login")
        
        with st.expander("Connect API", expanded=False):
            client_id = st.text_input("Client ID", value=FYERS_CLIENT_ID)
            client_secret = st.text_input("Secret", value=FYERS_CLIENT_SECRET, type="password")
            redirect_uri = st.text_input("Redirect URI", value=FYERS_REDIRECT_URI)
            
            state_val = str(uuid.uuid4())
            
            if st.button("Generate Auth URL", use_container_width=True):
                if client_id and redirect_uri:
                    url = FyersClient.get_auth_url(client_id, redirect_uri, state_val)
                    st.markdown(f"[🔗 Open Login]({url})")
                else:
                    st.error("Provide credentials")
            
            auth_code_input = st.text_input("Paste auth_code")
            if st.button("Validate & Connect", use_container_width=True):
                if auth_code_input:
                    try:
                        client = FyersClient(client_id.strip(), client_secret.strip())
                        result = client.validate_auth_code(auth_code_input.strip())
                        if result.get("s") == "ok":
                            st.session_state["fyers_access_token"] = result.get("access_token")
                            st.session_state["fyers_client_id"] = client_id
                            st.success("✅ Connected!")
                            st.rerun()
                        else:
                            st.error(f"Failed: {result}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Paste auth_code")
            
            if st.session_state.get("fyers_access_token"):
                st.success("✅ Connected")
                if st.button("Disconnect", use_container_width=True):
                    st.session_state.pop("fyers_access_token", None)
                    st.session_state.pop("fyers_client_id", None)
                    st.rerun()
            else:
                st.warning("⚠️ Disconnected")


def render_sidebar_balance(client: Optional[FyersClient]):
    """Render account balance section in sidebar"""
    if not client:
        return
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("## 💰 Account Balance")
        
        funds_data = client.fetch_funds()
        
        if funds_data and funds_data.get("s") == "ok":
            fund_limit = funds_data.get("fund_limit", [{}])[0]
            st.metric("💵 Total", f"₹{fund_limit.get('equityAmount', 0):,.2f}")
            st.metric("✅ Available", f"₹{fund_limit.get('availablecash', 0):,.2f}")
            st.metric("📊 Used", f"₹{fund_limit.get('utilized_amount', 0):,.2f}")
            
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()


def render_live_indicator(text: str = "LIVE"):
    """Render live indicator with timestamp"""
    from utils import format_timestamp
    st.markdown(
        f"<span class='live-indicator'></span> **{text}** - {format_timestamp('%H:%M:%S')}",
        unsafe_allow_html=True
    )


def render_pnl_card(amount: float, title: str = "Total Profit/Loss"):
    """Render P&L card with styling"""
    pnl_class = "pnl-positive" if amount >= 0 else "pnl-negative"
    pnl_color = "#00cc96" if amount >= 0 else "#ef553b"
    pnl_icon = "📈" if amount >= 0 else "📉"
    
    st.markdown(f"""
    <div class="pnl-card {pnl_class}">
        <h2 style="margin: 0; color: {pnl_color};">{pnl_icon} ₹{amount:,.2f}</h2>
        <p style="margin: 5px 0 0 0; color: #a0aec0;">{title}</p>
    </div>
    """, unsafe_allow_html=True)


def render_styled_metric(label: str, value: float, color: str):
    """Render styled metric card"""
    st.markdown(f"""
    <div style="background: #1f2733; padding: 15px; border-radius: 8px; border-left: 3px solid {color};">
        <h4 style="margin: 0; color: {color};">₹{value:,.2f}</h4>
        <p style="margin: 5px 0 0 0; color: #a0aec0;">{label}</p>
    </div>
    """, unsafe_allow_html=True)


def render_dataframe_with_colors(df: pd.DataFrame, color_columns: list, 
                                 height: int = 400) -> None:
    """Render dataframe with colored columns"""
    def color_cell(val):
        try:
            v = float(val)
            if v > 0:
                return 'color: #00cc96; font-weight: bold'
            elif v < 0:
                return 'color: #ef553b; font-weight: bold'
            return 'color: white'
        except:
            return 'color: white'
    
    styled = df.style.applymap(color_cell, subset=color_columns)
    st.dataframe(styled, use_container_width=True, height=height)


def render_navigation():
    """Render page navigation"""
    return st.radio(
        "Select View",
        ('Watchlist', 'Bull/Bear Dashboard', 'Option Chain', 'Account Overview'),
        horizontal=True,
        key='page_nav'
    )


def render_footer():
    """Render footer"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); border-radius: 10px;'>
        <h4>📊 Professional Market Analysis Dashboard</h4>
        <p>Real-time breakout detection powered by Fyers API</p>
        <p style='font-size: 0.8em; color: #718096;'>
            Live Watchlist • Smart Bull/Bear Detection • Option Chain • Account P&L
        </p>
        <p style='font-size: 0.75em; color: #4a5568; margin-top: 10px;'>
            🔍 Advanced Logic: PWH/PWL Breakout + 2x Volume + 10% OI Change + Option Confirmation
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_search_suggestions(search_term: str, symbol_list: list, 
                              session_key: str = 'watchlist_symbols'):
    """Render search suggestions with add buttons"""
    from utils import search_symbols
    import time
    
    if not search_term:
        return
    
    suggestions = search_symbols(search_term, symbol_list)
    
    if suggestions:
        st.markdown("**💡 Suggestions:**")
        
        # Exact match stars
        exact_match = [s for s in symbol_list if s == search_term.upper().strip()]
        
        # Display in rows of 5
        for i in range(0, len(suggestions), 5):
            cols = st.columns(5)
            for idx, sug in enumerate(suggestions[i:i+5]):
                with cols[idx]:
                    display_name = f"⭐ {sug}" if sug in exact_match else sug
                    
                    if st.button(display_name, key=f"add_{sug}_{i}", use_container_width=True):
                        if sug not in st.session_state[session_key]:
                            st.session_state[session_key].append(sug)
                            st.success(f"✅ Added {sug}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.info(f"Already in watchlist")
    else:
        st.info("No matching stocks found")
