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

if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = time.time()

if 'selected_sector' not in st.session_state:
    st.session_state['selected_sector'] = None

if 'auto_refresh_watchlist' not in st.session_state:
    st.session_state['auto_refresh_watchlist'] = False

if 'auto_refresh_account' not in st.session_state:
    st.session_state['auto_refresh_account'] = False

if 'selected_option_symbol' not in st.session_state:
    st.session_state['selected_option_symbol'] = "NIFTY50"

# Stock universe with sector mapping
STOCK_UNIVERSE = {
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT", "TECHM": "IT",
    "RELIANCE": "Oil & Gas", "ONGC": "Oil & Gas", "IOC": "Oil & Gas", "BPCL": "Oil & Gas", "GAIL": "Oil & Gas",
    "HDFC": "Financial Services", "ICICIBANK": "Private Bank", "SBIN": "PSU Bank", 
    "KOTAKBANK": "Private Bank", "AXISBANK": "Private Bank", "HDFCBANK": "Private Bank",
    "ITC": "FMCG", "HINDUNILVR": "FMCG", "BRITANNIA": "FMCG", "DABUR": "FMCG", "MARICO": "FMCG",
    "DRREDDY": "Pharma", "SUNPHARMA": "Pharma", "CIPLA": "Pharma", "DIVISLAB": "Pharma", "AUROPHARMA": "Pharma",
    "TATAMOTORS": "Auto", "M&M": "Auto", "MARUTI": "Auto", "BAJAJ-AUTO": "Auto", "HEROMOTOCO": "Auto",
    "TATASTEEL": "Metal", "HINDALCO": "Metal", "JSWSTEEL": "Metal", "VEDL": "Metal", "COALINDIA": "Metal",
    "DLF": "Realty", "OBEROIRLTY": "Realty", "GODREJPROP": "Realty", "PRESTIGE": "Realty",
    "TITAN": "Consumer Durables", "VOLTAS": "Consumer Durables", "HAVELLS": "Consumer Durables",
    "ZEEL": "Media", "SUNTV": "Media", "PVR": "Media", "NETWORK18": "Media",
    "NIFTY50": "Index", "BANKNIFTY": "Index", "SENSEX": "Index", "FINNIFTY": "Index"
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
.stRadio > label {
    padding: 8px 20px;
    margin: 0 5px;
    border-radius: 8px;
    background-color: #1f2733;
    color: #e6e6e6;
    font-weight: bold;
    cursor: pointer;
    border: 1px solid #3e4451;
    transition: background-color 0.3s;
}
.stRadio > label:hover {
    background-color: #3e4451;
    transform: translateY(-2px);
}
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
    print("------------------------------------------------------------------------\n")

    print("Fetching option chain for:", symbol, "Expiry:", expiry_date, "Client ID:", client_id, 
          "Access Token:", access_token)
    print("------------------------------------------------------------------------\n")
    try:
        # Format symbol for option chain
        if symbol == "NIFTY50":
            option_symbol = "NSE:NIFTY50-INDEX"
        elif symbol == "BANKNIFTY":
            option_symbol = "NSE:NIFTYBANK-INDEX"
        else:
            option_symbol = f"NSE:{symbol}-INDEX"
        
        url = f"{FYERS_BASE}/data/optionchain"
        auth_header = f"{client_id}:{access_token}"
        headers = {"Authorization": auth_header}
        
        # Request payload
        payload = {
            "symbol": option_symbol,
            "strikecount": 50,
            "timestamp": expiry_date
        }
        
        resp = requests.put(url, json=payload, headers=headers, timeout=15)
        print("Option chain response ----------------------------------------: \n", resp)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"s": "error", "message": str(e)}

def build_df_from_quotes(quotes_json: dict) -> pd.DataFrame:
    """Build dataframe from Fyers quotes"""
    records = []
    for item in quotes_json.get("d", []):
        try:
            n = item.get("n") or item.get("symbol")
            v = item.get("v", {})
            short = n.split(":")[-1].replace("-EQ", "").replace("-INDEX", "") if n else None
            
            sector = STOCK_UNIVERSE.get(short, "Unknown")
            
            ltp = float(v.get("lp") or v.get("ltp") or 0)
            prev_close = float(v.get("prev_close_price", ltp) or ltp)
            volume = float(v.get("volume", 0) or 0)
            oi = float(v.get("open_interest", 0) or 0)
            prev_oi = float(v.get("prev_open_interest", oi) or oi)
            
            records.append({
                "symbol": short or n, 
                "name": v.get("description", short or n), 
                "sector": sector,
                "current_close": ltp, 
                "prev_close": prev_close,
                "prev_day_high": prev_close * 1.02,
                "prev_day_low": prev_close * 0.98,
                "prev_week_high": prev_close * 1.05,
                "prev_week_low": prev_close * 0.95,
                "oi_prev": prev_oi,
                "oi_current": oi,
                "iv_prev_high": 20.0,
                "iv_current": 22.0,
                "vol_20_avg": max(volume, 100000),
                "vol_current": volume,
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

def classify_row(row, timeframe="daily"):
    """Enhanced classification logic"""
    try:
        price_change = percent_change(row["prev_close"], row["current_close"])
        oi_pct = percent_change(row["oi_prev"], row["oi_current"])
        vol_ratio = row["vol_current"] / row["vol_20_avg"] if row["vol_20_avg"] > 0 else 1
        
        bull_score = 0
        if price_change > 2: bull_score += 3
        elif price_change > 1: bull_score += 2
        elif price_change > 0.3: bull_score += 1
        
        if vol_ratio > 2: bull_score += 2
        elif vol_ratio > 1.5: bull_score += 1
        
        if oi_pct > 10: bull_score += 2
        elif oi_pct > 5: bull_score += 1
        
        bear_score = 0
        if price_change < -2: bear_score += 3
        elif price_change < -1: bear_score += 2
        elif price_change < -0.3: bear_score += 1
        
        if vol_ratio > 2: bear_score += 2
        elif vol_ratio > 1.5: bear_score += 1
        
        if oi_pct > 10: bear_score += 2
        elif oi_pct > 5: bear_score += 1
        
        if bull_score >= 3 and bull_score > bear_score: return "bull"
        if bear_score >= 3 and bear_score > bull_score: return "bear"
        return None
    except:
        return None

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
                        print(result)
                        print("Access token: ", result.get("access_token"))
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
# PAGE 1: WATCHLIST WITH AUTO-REFRESH
# ==============================================================================
if page_selection == 'Watchlist':
    st.header("📈 Live Watchlist")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search Symbol", placeholder="Type: TCS, RELIANCE, NIFTY50")
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh (10s)", value=st.session_state.get('auto_refresh_watchlist', False))
        st.session_state['auto_refresh_watchlist'] = auto_refresh
    with col3:
        if st.button("🔄 Manual Refresh", use_container_width=True):
            st.rerun()
    
    # Auto-refresh logic
    if auto_refresh and st.session_state.get("fyers_access_token"):
        if time.time() - st.session_state.get('last_refresh', 0) > 10:
            st.session_state['last_refresh'] = time.time()
            time.sleep(0.1)
            st.rerun()
    
    # Suggestions
    if search_term:
        suggestions = [s for s in STOCK_UNIVERSE.keys() if search_term.upper() in s.upper()][:10]
        if suggestions:
            st.markdown("**Suggestions:**")
            cols = st.columns(min(5, len(suggestions)))
            for idx, sug in enumerate(suggestions):
                with cols[idx % 5]:
                    if st.button(f"➕ {sug}", key=f"add_{sug}"):
                        if sug not in st.session_state.watchlist_symbols:
                            st.session_state.watchlist_symbols.append(sug)
                            st.success(f"Added {sug}")
                            st.rerun()
    
    st.markdown("---")
    st.subheader("📋 Current Watchlist")
    
    if st.session_state.watchlist_symbols and st.session_state.get("fyers_access_token"):
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
                st.markdown(f"<span class='live-indicator'></span> **LIVE** - Updated: {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
                
                def color_chg(val):
                    color = '#00cc96' if val > 0 else '#ef553b' if val < 0 else 'white'
                    return f'color: {color}; font-weight: bold'
                
                styled = df_watch.style.applymap(color_chg, subset=['Change', 'Change (%)'])
                st.dataframe(styled, use_container_width=True, height=400)
        except Exception as e:
            st.error(f"Error loading watchlist: {e}")
    
    # Remove symbol
    if st.session_state.watchlist_symbols:
        col1, col2 = st.columns([3, 1])
        with col1:
            remove_sym = st.selectbox("Remove Symbol", [''] + st.session_state.watchlist_symbols)
        with col2:
            if remove_sym and st.button("Remove", use_container_width=True):
                st.session_state.watchlist_symbols.remove(remove_sym)
                st.success(f"Removed {remove_sym}")
                st.rerun()

# ==============================================================================
# PAGE 2: BULL/BEAR DASHBOARD WITH LIVE SECTOR DATA
# ==============================================================================
elif page_selection == 'Bull/Bear Dashboard':
    st.header("🎯 Bull/Bear Analysis")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<span class='live-indicator'></span> **LIVE DATA** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh", type="primary", use_container_width=True):
            st.rerun()
    
    # Fetch sector data
    if st.session_state.get("fyers_access_token"):
        st.subheader("📊 Live Sector Performance")
        
        try:
            sector_symbols = list(SECTOR_INDICES.values())
            resp = fetch_quotes(sector_symbols,
                              st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                              st.session_state.get("fyers_access_token"))
            
            # Debug: Show raw response structure for first item
            if resp.get("d") and len(resp.get("d", [])) > 0:
                with st.expander("🔍 Debug: Raw API Response (First Sector)"):
                    st.json(resp.get("d")[0])
            
            sector_data = []
            for item in resp.get("d", []):
                v = item.get("v", {})
                symbol = item.get("n", "")
                
                # Find sector name
                sector_name = None
                for name, sym in SECTOR_INDICES.items():
                    if sym in symbol:
                        sector_name = name
                        break
                
                if sector_name:
                    # Try multiple field names for LTP
                    ltp = float(v.get("lp") or v.get("ltp") or v.get("last_price") or v.get("cmd", {}).get("lp") or 0)
                    
                    # Try multiple field names for previous close
                    prev = float(v.get("prev_close_price") or v.get("previous_close") or v.get("close_price") or ltp or 0)
                    
                    # If still zero, try to get from change data
                    if ltp == 0 or prev == 0:
                        ch = float(v.get("ch") or v.get("change") or 0)
                        chp = float(v.get("chp") or v.get("change_percentage") or 0)
                        if chp != 0 and ltp > 0:
                            prev = ltp / (1 + chp/100)
                    
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
                    color = '#00cc96' if val > 0 else '#ef553b' if val < 0 else 'white'
                    return f'color: {color}; font-weight: bold'
                
                styled = df_sectors.style.applymap(color_sector, subset=['Change', 'Change %'])
                st.dataframe(styled, use_container_width=True, height=500)
            else:
                st.warning("No sector data available. Check the debug info above.")
        except Exception as e:
            st.error(f"Sector data error: {e}")
    
    st.markdown("---")
    
    # Stock analysis
    symbols_to_use = [
        "NSE:TCS-EQ", "NSE:INFY-EQ", "NSE:WIPRO-EQ", "NSE:HCLTECH-EQ",
        "NSE:HDFC-EQ", "NSE:ICICIBANK-EQ", "NSE:SBIN-EQ", "NSE:AXISBANK-EQ",
        "NSE:RELIANCE-EQ", "NSE:ONGC-EQ", "NSE:IOC-EQ", "NSE:BPCL-EQ",
        "NSE:ITC-EQ", "NSE:HINDUNILVR-EQ", "NSE:BRITANNIA-EQ",
        "NSE:DRREDDY-EQ", "NSE:SUNPHARMA-EQ", "NSE:CIPLA-EQ"
    ]
    
    if st.session_state.get("fyers_access_token"):
        try:
            resp = fetch_quotes(symbols_to_use,
                              st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                              st.session_state.get("fyers_access_token"))
            df = build_df_from_quotes(resp)
            
            if not df.empty:
                df["daily_tag"] = df.apply(lambda r: classify_row(r, "daily"), axis=1)
                
                st.subheader("📊 Bull/Bear Stock Lists")
                
                view_type = st.radio("View", ["🟢 Bullish", "🔴 Bearish", "📊 Both"], horizontal=True)
                
                if view_type == "🟢 Bullish":
                    bulls = df[df["daily_tag"] == "bull"]
                    if not bulls.empty:
                        bulls_display = bulls[["symbol", "name", "sector", "current_close"]].copy()
                        bulls_display['Change %'] = ((bulls["current_close"] - bulls["prev_close"]) / bulls["prev_close"] * 100).round(2)
                        st.success(f"✅ {len(bulls)} Bullish Stocks")
                        st.dataframe(bulls_display, use_container_width=True, height=400)
                    else:
                        st.info("No bullish stocks found")
                
                elif view_type == "🔴 Bearish":
                    bears = df[df["daily_tag"] == "bear"]
                    if not bears.empty:
                        bears_display = bears[["symbol", "name", "sector", "current_close"]].copy()
                        bears_display['Change %'] = ((bears["current_close"] - bears["prev_close"]) / bears["prev_close"] * 100).round(2)
                        st.error(f"⚠️ {len(bears)} Bearish Stocks")
                        st.dataframe(bears_display, use_container_width=True, height=400)
                    else:
                        st.info("No bearish stocks found")
                
                else:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🟢 Bullish Stocks")
                        bulls = df[df["daily_tag"] == "bull"]
                        if not bulls.empty:
                            bulls_display = bulls[["symbol", "current_close"]].copy()
                            bulls_display['Change %'] = ((bulls["current_close"] - bulls["prev_close"]) / bulls["prev_close"] * 100).round(2)
                            bulls_display.columns = ["Symbol", "Price", "Change %"]
                            st.success(f"✅ {len(bulls)} stocks")
                            st.dataframe(bulls_display, use_container_width=True, height=400)
                        else:
                            st.info("No bullish stocks")
                    
                    with col2:
                        st.markdown("#### 🔴 Bearish Stocks")
                        bears = df[df["daily_tag"] == "bear"]
                        if not bears.empty:
                            bears_display = bears[["symbol", "current_close"]].copy()
                            bears_display['Change %'] = ((bears["current_close"] - bears["prev_close"]) / bears["prev_close"] * 100).round(2)
                            bears_display.columns = ["Symbol", "Price", "Change %"]
                            st.error(f"⚠️ {len(bears)} stocks")
                            st.dataframe(bears_display, use_container_width=True, height=400)
                        else:
                            st.info("No bearish stocks")
        except Exception as e:
            st.error(f"Error loading stocks: {e}")

# ==============================================================================
# PAGE 3: OPTION CHAIN WITH LIVE DATA
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
            # Generate expiry dates (next 4 Thursdays)
            today = datetime.now()
            expiries = []
            for i in range(28):
                date = today + timedelta(days=i)
                if date.weekday() == 3:  # Thursday
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
                print("------------------------------------------------------------------------\n")
                print("Fetching option chain for:", symbol, "Expiry:", expiry)
                print("------------------------------------------------------------------------\n")

                option_data = fetch_option_chain(
                    symbol, 
                    expiry,
                    st.session_state.get("fyers_client_id", FYERS_CLIENT_ID),
                    st.session_state.get("fyers_access_token")
                )
                
                if option_data.get("s") == "ok":
                    print("------------------------------------------------------------------------\n")
                    print("Option Chain Data Retrieved Successfully: \n", option_data)
                    chain_data = option_data.get("data", {})
                    options = chain_data.get("optionsChain", [])
                    
                    if options:
                        st.markdown(f"<span class='live-indicator'></span> **LIVE** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
                        
                        # Process option chain
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
                        
                        # Display as side-by-side tables
                        col_call, col_put = st.columns(2)
                        
                        with col_call:
                            st.markdown("### 📞 CALL Options")
                            df_calls = pd.DataFrame(calls)
                            st.dataframe(df_calls, use_container_width=True, height=600)
                        
                        with col_put:
                            st.markdown("### 📉 PUT Options")
                            df_puts = pd.DataFrame(puts)
                            st.dataframe(df_puts, use_container_width=True, height=600)
                        
                        # Summary metrics
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
                            sentiment = "Bullish" if pcr > 1.2 else "Bearish" if pcr < 0.8 else "Neutral"
                            st.metric("Sentiment", sentiment)
                    else:
                        st.warning("No option chain data available")
                else:
                    st.error(f"❌ API Error: {option_data.get('message', 'Unknown error')}")
                    st.info("""
                    **Note:** Option chain may not be available in Fyers test/paper trading mode.
                    
                    **Alternatives:**
                    1. Use live trading account for option chain access
                    2. Check Fyers web platform
                    3. Verify if option chain endpoint is enabled for your account
                    """)
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Option chain requires live market hours and proper API permissions")

# ==============================================================================
# PAGE 4: ACCOUNT OVERVIEW WITH FIXED P&L
# ==============================================================================
elif page_selection == 'Account Overview':
    st.header("💼 Account Overview")
    
    if not st.session_state.get("fyers_access_token"):
        st.warning("🔌 Connect to Fyers API to view account")
    else:
        # Auto-refresh toggle
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"<span class='live-indicator'></span> **LIVE** - {datetime.now().strftime('%H:%M:%S')}", unsafe_allow_html=True)
        with col2:
            auto_refresh_acc = st.checkbox("🔄 Auto (15s)", value=st.session_state.get('auto_refresh_account', False))
            st.session_state['auto_refresh_account'] = auto_refresh_acc
        with col3:
            if st.button("🔄 Refresh", type="primary", use_container_width=True):
                st.rerun()
        
        # Auto-refresh
        if auto_refresh_acc:
            if time.time() - st.session_state.get('last_refresh', 0) > 15:
                st.session_state['last_refresh'] = time.time()
                time.sleep(0.1)
                st.rerun()
        
        client_id = st.session_state.get("fyers_client_id", FYERS_CLIENT_ID)
        access_token = st.session_state.get("fyers_access_token")
        
        with st.spinner("Loading account data..."):
            funds_data = fetch_funds(client_id, access_token)
            holdings_data = fetch_holdings(client_id, access_token)
            positions_data = fetch_positions(client_id, access_token)
        
        # Calculate P&L correctly
        total_pnl = 0.0
        holdings_pnl = 0.0
        positions_pnl = 0.0
        
        # Calculate Holdings P&L
        if holdings_data and holdings_data.get("s") == "ok":
            holdings_list = holdings_data.get("holdings", [])
            for holding in holdings_list:
                try:
                    qty = float(holding.get("quantity", 0) or 0)
                    buy_price = float(holding.get("costPrice", 0) or 0)
                    ltp = float(holding.get("ltp", 0) or 0)
                    
                    # P&L = (LTP - Buy Price) * Quantity
                    pnl = (ltp - buy_price) * qty
                    holdings_pnl += pnl
                except:
                    continue
        
        # Calculate Positions P&L
        if positions_data and positions_data.get("s") == "ok":
            net_positions = positions_data.get("netPositions", [])
            for position in net_positions:
                try:
                    # Use the realized + unrealized P&L from API
                    realized_pl = float(position.get("realized_profit", 0) or 0)
                    unrealized_pl = float(position.get("unrealized_profit", 0) or 0)
                    
                    # Total P&L for position
                    pnl = realized_pl + unrealized_pl
                    positions_pnl += pnl
                except:
                    continue
        
        total_pnl = holdings_pnl + positions_pnl
        
        # Display P&L Card
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
        
        # Account Balance
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
        
        # Holdings Table
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
        
        # Positions Table
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
        
        # Performance Summary
        st.markdown("---")
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_holdings_count = len(holdings_data.get("holdings", [])) if holdings_data and holdings_data.get("s") == "ok" else 0
            st.metric("📈 Holdings", total_holdings_count)
        
        with col2:
            total_pos_count = len(positions_data.get("netPositions", [])) if positions_data and positions_data.get("s") == "ok" else 0
            st.metric("🔄 Positions", total_pos_count)
        
        with col3:
            # Calculate win rate
            profitable = 0
            total_trades = 0
            
            if holdings_data and holdings_data.get("s") == "ok":
                for h in holdings_data.get("holdings", []):
                    try:
                        qty = float(h.get("quantity", 0) or 0)
                        avg = float(h.get("costPrice", 0) or 0)
                        ltp = float(h.get("ltp", 0) or 0)
                        if (ltp - avg) * qty > 0:
                            profitable += 1
                        total_trades += 1
                    except:
                        pass
            
            if positions_data and positions_data.get("s") == "ok":
                for p in positions_data.get("netPositions", []):
                    try:
                        r = float(p.get("realized_profit", 0) or 0)
                        u = float(p.get("unrealized_profit", 0) or 0)
                        if r + u > 0:
                            profitable += 1
                        total_trades += 1
                    except:
                        pass
            
            win_rate = f"{(profitable/total_trades*100):.1f}%" if total_trades > 0 else "N/A"
            st.metric("🎯 Win Rate", win_rate)

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%); border-radius: 10px;'>
    <h4>📊 Professional Market Analysis Dashboard</h4>
    <p>Real-time data powered by Fyers API</p>
    <p style='font-size: 0.8em; color: #718096;'>
        Live Watchlist • Bull/Bear Analysis • Option Chain • Account P&L
    </p>
</div>
""", unsafe_allow_html=True)