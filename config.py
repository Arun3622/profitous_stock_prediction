"""
Configuration file for Stock Market Analysis Dashboard
Contains all constants, credentials, and stock universe mappings
"""

# ==============================================================================
# 🎯 FYERS API CREDENTIALS (SET AS DEFAULTS)
# ==============================================================================
FYERS_CLIENT_ID = "CC0CREMTTR-100"
FYERS_CLIENT_SECRET = "RFYZ6EPBEH"
FYERS_REDIRECT_URI = "https://www.google.com"
FYERS_BASE = "https://api-t1.fyers.in"
# ==============================================================================

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

# Stock symbols to scan for bull/bear analysis
SCAN_SYMBOLS = [
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

# Available sectors for filtering
AVAILABLE_SECTORS = [
    "All", "IT", "Private Bank", "PSU Bank", "Oil & Gas", "FMCG", 
    "Pharma", "Auto", "Metal", "Financial Services", "Cement", 
    "Consumer Durables", "Telecom", "Conglomerate"
]

# CSS styling constants
CUSTOM_CSS = """
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
"""
