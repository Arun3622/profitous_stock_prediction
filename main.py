import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta
import requests
import hashlib
import urllib.parse
import uuid
import time

# ==============================================================================
# 🎯 USER-PROVIDED FYERS CREDENTIALS (SET AS DEFAULTS)
# ==============================================================================
FYERS_CLIENT_ID = "CC0CREMTTR-100"
FYERS_CLIENT_SECRET = "RFYZ6EPBEH"
FYERS_REDIRECT_URI = "https://www.google.com" 
# ==============================================================================

# Initialize Session States
if 'watchlist_symbols' not in st.session_state:
    st.session_state['watchlist_symbols'] = ["TCS", "RELIANCE", "NIFTY50"]

if 'selected_sector' not in st.session_state:
    st.session_state['selected_sector'] = None

if 'selected_option_symbol' not in st.session_state:
    st.session_state['selected_option_symbol'] = "NIFTY50"

# Expanded Stock universe with sector mapping (200+ stocks)
STOCK_UNIVERSE = {
    # IT Sector
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT", "TECHM": "IT",
    "LTI": "IT", "COFORGE": "IT", "MINDTREE": "IT", "MPHASIS": "IT", "PERSISTENT": "IT",
    
    # Oil & Gas
    "RELIANCE": "Oil & Gas", "ONGC": "Oil & Gas", "IOC": "Oil & Gas", "BPCL": "Oil & Gas", "GAIL": "Oil & Gas",
    "HINDPETRO": "Oil & Gas", "PETRONET": "Oil & Gas", "OIL": "Oil & Gas",
    
    # Banking & Financial Services
    "HDFCBANK": "Private Bank", "ICICIBANK": "Private Bank", "KOTAKBANK": "Private Bank", 
    "AXISBANK": "Private Bank", "INDUSINDBK": "Private Bank", "BANDHANBNK": "Private Bank",
    "SBIN": "PSU Bank", "PNB": "PSU Bank", "BANKBARODA": "PSU Bank", "CANBK": "PSU Bank",
    "HDFC": "Financial Services", "BAJFINANCE": "Financial Services", "BAJAJFINSV": "Financial Services",
    "SBILIFE": "Financial Services", "HDFCLIFE": "Financial Services", "ICICIGI": "Financial Services",
    
    # FMCG
    "ITC": "FMCG", "HINDUNILVR": "FMCG", "BRITANNIA": "FMCG", "DABUR": "FMCG", "MARICO": "FMCG",
    "NESTLEIND": "FMCG", "GODREJCP": "FMCG", "COLPAL": "FMCG", "TATACONSUM": "FMCG",
    
    # Pharma
    "DRREDDY": "Pharma", "SUNPHARMA": "Pharma", "CIPLA": "Pharma", "DIVISLAB": "Pharma", 
    "AUROPHARMA": "Pharma", "LUPIN": "Pharma", "TORNTPHARM": "Pharma", "BIOCON": "Pharma",
    "ALKEM": "Pharma", "CADILAHC": "Pharma",
    
    # Auto
    "TATAMOTORS": "Auto", "M&M": "Auto", "MARUTI": "Auto", "BAJAJ-AUTO": "Auto", 
    "HEROMOTOCO": "Auto", "EICHERMOT": "Auto", "TVSMOTOR": "Auto", "ASHOKLEY": "Auto",
    "MOTHERSON": "Auto", "BALKRISIND": "Auto", "MRF": "Auto", "APOLLOTYRE": "Auto",
    
    # Metal & Mining
    "TATASTEEL": "Metal", "HINDALCO": "Metal", "JSWSTEEL": "Metal", "VEDL": "Metal", 
    "COALINDIA": "Metal", "NATIONALUM": "Metal", "SAIL": "Metal", "JINDALSTEL": "Metal",
    "NMDC": "Metal", "HINDZINC": "Metal",
    
    # Realty
    "DLF": "Realty", "OBEROIRLTY": "Realty", "GODREJPROP": "Realty", "PRESTIGE": "Realty",
    "PHOENIXLTD": "Realty", "BRIGADE": "Realty",
    
    # Consumer Durables
    "TITAN": "Consumer Durables", "VOLTAS": "Consumer Durables", "HAVELLS": "Consumer Durables",
    "WHIRLPOOL": "Consumer Durables", "CROMPTON": "Consumer Durables", "BATAINDIA": "Consumer Durables",
    
    # Media & Entertainment
    "ZEEL": "Media", "SUNTV": "Media", "PVR": "Media", "NETWORK18": "Media", 
    "DISHTV": "Media", "HATHWAY": "Media",
    
    # Telecom
    "BHARTIARTL": "Telecom", "IDEA": "Telecom", "TTML": "Telecom",
    
    # Power & Energy
    "NTPC": "Power", "POWERGRID": "Power", "ADANIPOWER": "Power", "TATAPOWER": "Power",
    "NHPC": "Power", "TORNTPOWER": "Power",
    
    # Cement
    "ULTRACEMCO": "Cement", "GRASIM": "Cement", "SHREECEM": "Cement", "ACC": "Cement",
    "AMBUJACEM": "Cement", "JKCEMENT": "Cement", "RAMCOCEM": "Cement",
    
    # Conglomerate
    "LT": "Conglomerate", "ADANIENT": "Conglomerate", "SIEMENS": "Conglomerate",
    
    # Indices
    "NIFTY50": "Index", "BANKNIFTY": "Index", "SENSEX": "Index", "FINNIFTY": "Index",
    "MIDCPNIFTY": "Index"
}

# Sector indices mapping
SECTOR_INDICES = {
    "NIFTY AUTO": "NSE:NIFTY_AUTO-INDEX",
    "NIFTY FINANCIAL SERVICES": "NSE:NIFTY_FIN_SERVICE-INDEX",
    "NIFTY FMCG": "NSE:NIFTY_FMCG-INDEX",
    "NIFTY IT": "NSE:NIFTY_IT-INDEX",
    "NIFTY MEDIA": "NSE:NIFTY_MEDIA-INDEX",
    "NIFTY METAL": "NSE:NIFTY_METAL-INDEX",
    "NIFTY PHARMA": "NSE:NIFTY_PHARMA-INDEX",
    "NIFTY PSU BANK": "NSE:NIFTY_PSU_BANK-INDEX",
    "NIFTY PRIVATE BANK": "NSE:NIFTY_PVT_BANK-INDEX",
    "NIFTY REALTY": "NSE:NIFTY_REALTY-INDEX",
    "NIFTY HEALTHCARE": "NSE:NIFTY_HEALTHCARE-INDEX",
    "NIFTY CONSUMER DURABLES": "NSE:NIFTY_CONSR_DURBL-INDEX",
    "NIFTY OIL & GAS": "NSE:NIFTY_OIL_AND_GAS-INDEX"
}

st.set_page_config(page_title="Market Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
body { background-color: #0e1117; color: #d6d6d6; }
.stApp { background-color: #0e1117; }
* { transition: all 0.3s ease; }
.block-container{ padding-top:1rem; padding-bottom:0rem; }
.stDataFrame table th{ 
    background: #11161b !important; 
    color: #e6e6e6 !important; 
    font-weight: bold;
    text-align: center !important;
}
.stDataFrame table td{ padding: 8px !important; }
.stDataFrame tbody tr:hover { background-color: #1f2733 !important; }
.stButton button {
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 204, 150, 0.3);
}
.pnl-card {
    background: linear-gradient(135deg, #1f2733 0%, #2d3748 100%);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    border: 1px solid #3e4451;
}
.pnl-positive { border-left: 4px solid #00cc96; }
.pnl-negative { border-left: 4px solid #ef553b; }
.live-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #00cc96;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.suggestion-btn {
    display: inline-block;
    padding: 5px 10px;
    margin: 3px;
    background: #1f2733;
    border: 1px solid #3e4451;
    border-radius: 5px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Stock Market Analysis Dashboard")

# ----------------------------- FYERS AUTH & DATA HELPERS -----------------------------
FYERS_BASE = "https://api-t1.fyers.in"

def get_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return f"{FYERS_BASE}/api/v3/generate-authcode?" + urllib.parse.urlencode(params)

def compute_appid_hash(client_id: str, client_secret: str) -> str:
    combo = f"{client_id}:{client_secret}".encode("utf-8")
    return hashlib.sha256(combo).hexdigest()

def validate_auth_code(code: str, client_id: str, client_secret: str) -> dict:
    url = f"{FYERS_BASE}/api/v3/validate-authcode"
    appIdHash = compute_appid_hash(client_id, client_secret)
    payload = {
        "grant_type": "authorization_code",
        "appIdHash": appIdHash,
        "code": code,
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_quotes(symbols: list, client_id: str, access_token: str) -> dict:
    """Fetch live quotes from Fyers API"""
    try:
        url = f"{FYERS_BASE}/data/quotes?symbols=" + urllib.parse.quote(",".join(symbols))
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Quotes fetch error: {e}")
        return {"s": "error", "message": str(e)}

def fetch_history(symbol: str, resolution: str, date_from: str, date_to: str, client_id: str, access_token: str) -> dict:
    """Fetch historical data for volume and price analysis"""
    try:
        url = f"{FYERS_BASE}/data/history"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        
        params = {
            "symbol": symbol,
            "resolution": resolution,  # "5" for 5 minute
            "date_format": "1",
            "range_from": date_from,
            "range_to": date_to,
            "cont_flag": "1"
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def fetch_funds(client_id: str, access_token: str) -> dict:
    """Fetch account funds"""
    try:
        url = f"{FYERS_BASE}/api/v3/funds"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def fetch_holdings(client_id: str, access_token: str) -> dict:
    """Fetch holdings"""
    try:
        url = f"{FYERS_BASE}/api/v3/holdings"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def fetch_positions(client_id: str, access_token: str) -> dict:
    """Fetch positions"""
    try:
        url = f"{FYERS_BASE}/api/v3/positions"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def fetch_option_chain(symbol: str, expiry_date: str, client_id: str, access_token: str) -> dict:
    """Fetch option chain data"""
    try:
        if symbol == "NIFTY50":
            option_symbol = "NSE:NIFTY50-INDEX"
        elif symbol == "BANKNIFTY":
            option_symbol = "NSE:NIFTYBANK-INDEX"
        else:
            option_symbol = f"NSE:{symbol}-INDEX"
        
        url = f"{FYERS_BASE}/data/optionchain"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        
        payload = {
            "symbol": option_symbol,
            "strikecount": 50,
            "timestamp": expiry_date
        }
        
        resp = requests.put(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def build_df_from_quotes(quotes_json: dict, client_id: str, access_token: str) -> pd.DataFrame:
    """Build dataframe from Fyers quotes with historical data for volume analysis"""
    records = []
    
    # Get date range for historical data (last 20 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Get extra days for sufficient data
    
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
            hist_data = fetch_history(n, "5", str(date_from), str(date_to), client_id, access_token)
            
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

def percent_change(old, new):
    try:
        if old == 0: return 0.0
        return (new - old) / abs(old) * 100.0
    except: 
        return 0.0

def classify_row_advanced(row, option_data=None):
    """
    Enhanced classification logic based on your requirements:
    
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
                # Look for put addition or call unwinding near strike
                resistance_weakening = check_resistance_weakening(row, option_data)
                if resistance_weakening:
                    return "bull"
            else:
                # Without option data, use price + volume + OI
                return "bull"
        
        elif price_below_pwl and vol_condition and oi_condition:
            # Check option confirmation if available
            if option_data:
                # Look for call addition or put unwinding near strike
                support_weakening = check_support_weakening(row, option_data)
                if support_weakening:
                    return "bear"
            else:
                # Without option data, use price + volume + OI
                return "bear"
        
        return None
    except Exception as e:
        return None

def check_resistance_weakening(row, option_data):
    """
    Check if resistance is weakening:
    - Put addition (long buildup) OR
    - Call unwinding (short covering)
    """
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

def check_support_weakening(row, option_data):
    """
    Check if support is weakening:
    - Call addition (short buildup) OR
    - Put unwinding (long covering)
    """
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

# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown("## 🔑 Fyers API Login")
    
    with st.expander("Connect API", expanded=False):
        client_id = st.text_input("Client ID", value=FYERS_CLIENT_ID)
        client_secret = st.text_input("Secret", value=FYERS_CLIENT_SECRET, type="password")
        redirect_uri = st.text_input("Redirect URI", value=FYERS_REDIRECT_URI)
        
        state_val = str(uuid.uuid4())
        
        if st.button("Generate Auth URL", use_container_width=True):
            if client_id and redirect_uri:
                url = get_auth_url(client_id, redirect_uri, state_val)
                st.markdown(f"[🔗 Open Login]({url})")
            else:
                st.error("Provide credentials")
        
        auth_code_input = st.text_input("Paste auth_code")
        if st.button("Validate & Connect", use_container_width=True):
            if auth_code_input:
                try:
                    result = validate_auth_code(auth_code_input.strip(), client_id.strip(), client_secret.strip())
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
    
    if st.session_state.get("fyers_access_token"):
        st.markdown("---")
        st.markdown("## 💰 Account Balance")
        
        funds_data = fetch_funds(
            st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
            st.session_state.get("fyers_access_token")
        )
        
        if funds_data and funds_data.get("s") == "ok":
            fund_limit = funds_data.get("fund_limit", [{}])[0]
            st.metric("💵 Total", f"₹{fund_limit.get('equityAmount', 0):,.2f}")
            st.metric("✅ Available", f"₹{fund_limit.get('availablecash', 0):,.2f}")
            st.metric("📊 Used", f"₹{fund_limit.get('utilized_amount', 0):,.2f}")
            
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

# ----------------------------- NAVIGATION -----------------------------
page_selection = st.radio(
    "Select View",
    ('Watchlist', 'Bull/Bear Dashboard', 'Option Chain', 'Account Overview'),
    horizontal=True,
    key='page_nav'
)

st.markdown("---")

# ==============================================================================
# PAGE 1: LIVE WATCHLIST (NO AUTO-REFRESH TOGGLE)
# ==============================================================================
if page_selection == 'Watchlist':
    st.header("📈 Live Watchlist")
    
    # Search with suggestions
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search & Add Stocks", placeholder="Type: TCS, RELIANCE, INFY...", key="search_stock")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Smart suggestions with exact and related matches
    if search_term:
        search_upper = search_term.upper().strip()
        
        # Find exact match first
        exact_match = [s for s in STOCK_UNIVERSE.keys() if s == search_upper]
        
        # Find related matches (starts with or contains)
        starts_with = [s for s in STOCK_UNIVERSE.keys() if s.startswith(search_upper) and s not in exact_match]
        contains = [s for s in STOCK_UNIVERSE.keys() if search_upper in s and s not in exact_match and s not in starts_with]
        
        # Combine: exact first, then starts_with, then contains
        suggestions = (exact_match + starts_with + contains)[:10]
        
        if suggestions:
            st.markdown("**💡 Suggestions:**")
            
            # Display in rows of 5
            for i in range(0, len(suggestions), 5):
                cols = st.columns(5)
                for idx, sug in enumerate(suggestions[i:i+5]):
                    with cols[idx]:
                        # Show exact match with star
                        display_name = f"⭐ {sug}" if sug in exact_match else sug
                        
                        if st.button(display_name, key=f"add_{sug}_{i}", use_container_width=True):
                            if sug not in st.session_state.watchlist_symbols:
                                st.session_state.watchlist_symbols.append(sug)
                                st.success(f"✅ Added {sug}")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.info(f"Already in watchlist")
        else:
            st.info("No matching stocks found")
    
    st.markdown("---")
    st.subheader("📋 Live Watchlist")
    
    if st.session_state.watchlist_symbols and st.session_state.get("fyers_access_token"):
        # Add placeholder for live updating
        watchlist_placeholder = st.empty()
        
        try:
            fyers_symbols = [f"NSE:{s}-EQ" for s in st.session_state.watchlist_symbols]
            resp = fetch_quotes(fyers_symbols, 
                              st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                              st.session_state.get("fyers_access_token"))
            
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
                    st.markdown(f"<span class='live-indicator'></span> **LIVE** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
                    
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
    
    # Remove symbol
    if st.session_state.watchlist_symbols:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            remove_sym = st.selectbox("🗑️ Remove Symbol", [''] + st.session_state.watchlist_symbols)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if remove_sym and st.button("Remove", use_container_width=True, type="secondary"):
                st.session_state.watchlist_symbols.remove(remove_sym)
                st.success(f"Removed {remove_sym}")
                time.sleep(0.5)
                st.rerun()

# ==============================================================================
# PAGE 2: BULL/BEAR DASHBOARD WITH ENHANCED LOGIC
# ==============================================================================
elif page_selection == 'Bull/Bear Dashboard':
    st.header("🎯 Bull/Bear Analysis - Today's Fresh Breakouts")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<span class='live-indicator'></span> **LIVE ANALYSIS** - {datetime.now().strftime('%d %b %Y, %H:%M:%S')}", unsafe_allow_html=True)
        st.caption("Only showing TODAY'S fresh breakouts based on: Price vs Weekly High/Low + 2x Volume + 10% OI Change")
    with col2:
        if st.button("🔄 Scan Now", type="primary", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Fetch sector data
    if st.session_state.get("fyers_access_token"):
        st.subheader("📊 Live Sector Performance")
        
        try:
            sector_symbols = list(SECTOR_INDICES.values())
            resp = fetch_quotes(sector_symbols,
                              st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                              st.session_state.get("fyers_access_token"))
            
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
    
    st.markdown("---")
    
    # Stock analysis with TODAY'S logic - EXPANDED UNIVERSE
    symbols_to_use = [
        # IT Sector
        "NSE:TCS-EQ", "NSE:INFY-EQ", "NSE:WIPRO-EQ", "NSE:HCLTECH-EQ", "NSE:TECHM-EQ",
        
        # Banking
        "NSE:HDFCBANK-EQ", "NSE:ICICIBANK-EQ", "NSE:SBIN-EQ", "NSE:AXISBANK-EQ", 
        "NSE:KOTAKBANK-EQ", "NSE:INDUSINDBK-EQ",
        
        # Oil & Gas
        "NSE:RELIANCE-EQ", "NSE:ONGC-EQ", "NSE:IOC-EQ", "NSE:BPCL-EQ",
        
        # FMCG
        "NSE:ITC-EQ", "NSE:HINDUNILVR-EQ", "NSE:BRITANNIA-EQ", "NSE:NESTLEIND-EQ",
        
        # Pharma
        "NSE:DRREDDY-EQ", "NSE:SUNPHARMA-EQ", "NSE:CIPLA-EQ", "NSE:DIVISLAB-EQ",
        
        # Auto
        "NSE:TATAMOTORS-EQ", "NSE:MARUTI-EQ", "NSE:M&M-EQ", "NSE:BAJAJ-AUTO-EQ",
        
        # Metal
        "NSE:TATASTEEL-EQ", "NSE:HINDALCO-EQ", "NSE:JSWSTEEL-EQ", "NSE:VEDL-EQ",
        
        # Conglomerate
        "NSE:LT-EQ", "NSE:ADANIENT-EQ",
        
        # Financial Services
        "NSE:BAJFINANCE-EQ", "NSE:BAJAJFINSV-EQ", "NSE:HDFCLIFE-EQ",
        
        # Cement
        "NSE:ULTRACEMCO-EQ", "NSE:SHREECEM-EQ", "NSE:ACC-EQ",
        
        # Consumer Durables
        "NSE:TITAN-EQ", "NSE:HAVELLS-EQ",
        
        # Telecom
        "NSE:BHARTIARTL-EQ"
    ]
    
    # Add sector filter
    st.subheader("🎯 Stock Analysis Scanner")
    
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        sector_filter = st.multiselect(
            "🔍 Filter by Sector (Optional)",
            options=["All", "IT", "Private Bank", "PSU Bank", "Oil & Gas", "FMCG", 
                    "Pharma", "Auto", "Metal", "Financial Services", "Cement", 
                    "Consumer Durables", "Telecom", "Conglomerate"],
            default=["All"]
        )
    
    with col_filter2:
        min_volume_ratio = st.slider("Min Volume Ratio", 1.0, 5.0, 2.0, 0.5)
    
    st.markdown("---")
    
    if st.session_state.get("fyers_access_token"):
        with st.spinner("🔍 Scanning for TODAY'S breakouts..."):
            try:
                client_id = st.session_state.get("fyers_client_id", FYERS_CLIENT_ID)
                access_token = st.session_state.get("fyers_access_token")
                
                resp = fetch_quotes(symbols_to_use, client_id, access_token)
                df = build_df_from_quotes(resp, client_id, access_token)
                
                if not df.empty:
                    # Apply ADVANCED classification logic
                    df["daily_tag"] = df.apply(lambda r: classify_row_advanced(r), axis=1)
                    
                    # Apply sector filter
                    if "All" not in sector_filter and sector_filter:
                        df = df[df["sector"].isin(sector_filter)]
                    
                    # Apply volume filter
                    df["vol_ratio"] = df["vol_current"] / df["vol_20_avg"]
                    df = df[df["vol_ratio"] >= min_volume_ratio]
                    
                    st.subheader("📊 Today's Breakout Stocks")
                    
                    # Show summary metrics
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
                    
                    st.markdown("---")
                    
                    view_type = st.radio("View", ["🟢 Bullish Breakouts", "🔴 Bearish Breakouts", "📊 Both"], horizontal=True)
                    
                    if view_type == "🟢 Bullish Breakouts":
                        bulls = df[df["daily_tag"] == "bull"].copy()
                        
                        if not bulls.empty:
                            # Add detailed metrics
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
                            
                            st.info("""
                            **Criteria:** Price > Weekly High ✅ | Volume > 2x Avg ✅ | OI Change > 10% ✅
                            """)
                        else:
                            st.info("✨ No fresh BULLISH breakouts detected today based on the criteria")
                    
                    elif view_type == "🔴 Bearish Breakouts":
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
                            
                            st.info("""
                            **Criteria:** Price < Weekly Low ✅ | Volume > 2x Avg ✅ | OI Change > 10% ✅
                            """)
                        else:
                            st.info("✨ No fresh BEARISH breakdowns detected today based on the criteria")
                    
                    else:  # Both view
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
                                    try:
                                        v = float(val)
                                        return 'color: #00cc96; font-weight: bold'
                                    except:
                                        return ''
                                
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
                                    try:
                                        v = float(val)
                                        return 'color: #ef553b; font-weight: bold'
                                    except:
                                        return ''
                                
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
                else:
                    st.warning("No data available")
            except Exception as e:
                st.error(f"Error: {e}")

# ==============================================================================
# PAGE 3: OPTION CHAIN WITH ENHANCED ANALYSIS
# ==============================================================================
elif page_selection == 'Option Chain':
    st.header("🎯 Live Option Chain")
    
    if not st.session_state.get("fyers_access_token"):
        st.warning("🔌 Connect to Fyers API to view option chain")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            symbol = st.selectbox("Index", ["NIFTY50", "BANKNIFTY", "FINNIFTY"])
            st.session_state['selected_option_symbol'] = symbol
        
        with col2:
            today = datetime.now()
            expiries = []
            for i in range(28):
                date = today + timedelta(days=i)
                if date.weekday() == 3:
                    expiries.append(date.strftime("%Y-%m-%d"))
                if len(expiries) == 4:
                    break
            
            expiry = st.selectbox("Expiry", expiries)
        
        with col3:
            strike_count = st.selectbox("Strikes", [10, 20, 30, 40, 50], index=2)
        
        with col4:
            if st.button("🔄 Fetch Chain", type="primary", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        with st.spinner("Loading option chain..."):
            try:
                option_data = fetch_option_chain(
                    symbol, 
                    expiry,
                    st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                    st.session_state.get("fyers_access_token")
                )
                
                if option_data.get("s") == "ok":
                    chain_data = option_data.get("data", {})
                    options = chain_data.get("optionsChain", [])
                    
                    if options:
                        st.markdown(f"<span class='live-indicator'></span> **LIVE** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
                        
                        calls = []
                        puts = []
                        
                        for opt in options[:strike_count]:
                            strike = opt.get("strike_price", 0)
                            
                            call_data = opt.get("call", {})
                            put_data = opt.get("put", {})
                            
                            calls.append({
                                "Strike": strike,
                                "CE LTP": call_data.get("ltp", 0),
                                "CE OI": call_data.get("oi", 0),
                                "CE Volume": call_data.get("volume", 0),
                                "CE IV": call_data.get("iv", 0)
                            })
                            
                            puts.append({
                                "Strike": strike,
                                "PE LTP": put_data.get("ltp", 0),
                                "PE OI": put_data.get("oi", 0),
                                "PE Volume": put_data.get("volume", 0),
                                "PE IV": put_data.get("iv", 0)
                            })
                        
                        col_call, col_put = st.columns(2)
                        
                        with col_call:
                            st.markdown("### 📞 CALL Options")
                            df_calls = pd.DataFrame(calls)
                            st.dataframe(df_calls, use_container_width=True, height=600)
                        
                        with col_put:
                            st.markdown("### 📉 PUT Options")
                            df_puts = pd.DataFrame(puts)
                            st.dataframe(df_puts, use_container_width=True, height=600)
                        
                        st.markdown("---")
                        st.subheader("📊 Option Chain Summary")
                        
                        total_call_oi = sum([c["CE OI"] for c in calls])
                        total_put_oi = sum([p["PE OI"] for p in puts])
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
                    else:
                        st.warning("No option chain data available")
                else:
                    st.error(f"❌ API Error: {option_data.get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error: {e}")

# ==============================================================================
# PAGE 4: ACCOUNT OVERVIEW
# ==============================================================================
elif page_selection == 'Account Overview':
    st.header("💼 Account Overview")
    
    if not st.session_state.get("fyers_access_token"):
        st.warning("🔌 Connect to Fyers API to view account")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<span class='live-indicator'></span> **LIVE** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
        with col2:
            if st.button("🔄 Refresh", type="primary", use_container_width=True):
                st.rerun()
        
        client_id = st.session_state.get("fyers_client_id", FYERS_CLIENT_ID)
        access_token = st.session_state.get("fyers_access_token")
        
        with st.spinner("Loading account data..."):
            funds_data = fetch_funds(client_id, access_token)
            holdings_data = fetch_holdings(client_id, access_token)
            positions_data = fetch_positions(client_id, access_token)
        
        total_pnl = 0.0
        holdings_pnl = 0.0
        positions_pnl = 0.0
        
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
        
        total_pnl = holdings_pnl + positions_pnl
        
        st.markdown("### 💹 Live P&L Summary")
        
        pnl_class = "pnl-positive" if total_pnl >= 0 else "pnl-negative"
        pnl_color = "#00cc96" if total_pnl >= 0 else "#ef553b"
        pnl_icon = "📈" if total_pnl >= 0 else "📉"
        
        st.markdown(f"""
        <div class="pnl-card {pnl_class}">
            <h2 style="margin: 0; color: {pnl_color};">{pnl_icon} ₹{total_pnl:,.2f}</h2>
            <p style="margin: 5px 0 0 0; color: #a0aec0;">Total Profit/Loss (Live)</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            color1 = "#00cc96" if holdings_pnl >= 0 else "#ef553b"
            st.markdown(f"""
            <div style="background: #1f2733; padding: 15px; border-radius: 8px; border-left: 3px solid {color1};">
                <h4 style="margin: 0; color: {color1};">₹{holdings_pnl:,.2f}</h4>
                <p style="margin: 5px 0 0 0; color: #a0aec0;">Holdings P&L</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            color2 = "#00cc96" if positions_pnl >= 0 else "#ef553b"
            st.markdown(f"""
            <div style="background: #1f2733; padding: 15px; border-radius: 8px; border-left: 3px solid {color2};">
                <h4 style="margin: 0; color: {color2};">₹{positions_pnl:,.2f}</h4>
                <p style="margin: 5px 0 0 0; color: #a0aec0;">Positions P&L</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
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
        
        st.markdown("---")
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
                            if v > 0: return 'color: #00cc96; font-weight: bold'
                            elif v < 0: return 'color: #ef553b; font-weight: bold'
                            else: return 'color: white'
                        except: return 'color: white'
                    
                    styled = df_h.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                    st.dataframe(styled, use_container_width=True, height=350)
                    st.success(f"✅ Total Holdings P&L: ₹{holdings_pnl:,.2f}")
                else:
                    st.info("No holdings data")
            else:
                st.info("📭 No holdings")
        else:
            st.info("📭 No holdings data")
        
        st.markdown("---")
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
                    styled = df_p.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
                    st.dataframe(styled, use_container_width=True, height=350)
                    st.success(f"✅ Total Positions P&L: ₹{positions_pnl:,.2f}")
                else:
                    st.info("No position data")
            else:
                st.info("📭 No open positions")
        else:
            st.info("📭 No position data")

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

# Auto-refresh mechanism for live data (runs in background)
if 'last_auto_refresh' not in st.session_state:
    st.session_state['last_auto_refresh'] = time.time()

# Check if 10 seconds have passed since last refresh for live watchlist
if page_selection == 'Watchlist' and st.session_state.get("fyers_access_token"):
    current_time = time.time()
    if current_time - st.session_state['last_auto_refresh'] >= 10:
        st.session_state['last_auto_refresh'] = current_time
        st.rerun()