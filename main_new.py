"""
Stock Market Analysis Dashboard - Main Entry Point
Professional market analysis tool with real-time data from Fyers API

Architecture:
- config.py: Configuration, constants, and credentials
- fyers_client.py: API client for Fyers integration
- data_processor.py: Data transformation and classification logic
- utils.py: Utility functions
- ui_components.py: Reusable UI components
- pages/: Individual page modules
  - watchlist.py: Live watchlist functionality
  - bull_bear.py: Bull/Bear analysis and sector performance
  - option_chain.py: Option chain data and analysis
  - account.py: Account overview, holdings, positions
"""

import streamlit as st
import time
from fyers_client import get_fyers_client
from ui_components import (
    render_custom_css,
    render_sidebar_auth,
    render_sidebar_balance,
    render_navigation,
    render_footer
)
from TabPages.watchlist import render_watchlist_page
from TabPages.bull_bear import render_bull_bear_page
from TabPages.option_chain import render_option_chain_page
from TabPages.account import render_account_page


def initialize_session_state():
    """Initialize session state variables"""
    if 'watchlist_symbols' not in st.session_state:
        st.session_state['watchlist_symbols'] = ["TCS", "RELIANCE", "NIFTY50"]
    
    if 'selected_sector' not in st.session_state:
        st.session_state['selected_sector'] = None
    
    if 'selected_option_symbol' not in st.session_state:
        st.session_state['selected_option_symbol'] = "NIFTY50"
    
    if 'last_auto_refresh' not in st.session_state:
        st.session_state['last_auto_refresh'] = time.time()


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Market Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Apply custom CSS
    render_custom_css()
    
    # Title
    st.title("📊 Stock Market Analysis Dashboard")
    
    # Sidebar: Authentication and Balance
    render_sidebar_auth()
    
    # Get Fyers client if authenticated
    client = get_fyers_client()
    
    if client:
        render_sidebar_balance(client)
    
    # Navigation
    page_selection = render_navigation()
    
    st.markdown("---")
    
    # Route to appropriate page
    if page_selection == 'Watchlist':
        render_watchlist_page(client)
    elif page_selection == 'Bull/Bear Dashboard':
        render_bull_bear_page(client)
    elif page_selection == 'Option Chain':
        render_option_chain_page(client)
    elif page_selection == 'Account Overview':
        render_account_page(client)
    
    # Footer
    render_footer()
    
    # Auto-refresh for watchlist page
    if page_selection == 'Watchlist' and client:
        current_time = time.time()
        if current_time - st.session_state['last_auto_refresh'] >= 10:
            st.session_state['last_auto_refresh'] = current_time
            st.rerun()


if __name__ == "__main__":
    main()
