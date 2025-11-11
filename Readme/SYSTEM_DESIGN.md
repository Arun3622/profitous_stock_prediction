# System Design - Stock Market Analysis Dashboard

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
│                          (Streamlit App)                             │
├─────────────────────────────────────────────────────────────────────┤
│  main_new.py │ ui_components.py │ pages/*.py (View Layer)           │
└────────┬────────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────────────────────────┐
         │                                                           │
┌────────▼─────────────────────────┐     ┌─────────────────────────▼─┐
│     BUSINESS LOGIC LAYER         │     │   CONFIGURATION LAYER     │
├──────────────────────────────────┤     ├───────────────────────────┤
│  data_processor.py               │     │  config.py                │
│  - Classification Logic          │     │  - Constants              │
│  - P&L Calculations              │     │  - Stock Universe         │
│  - Data Transformations          │     │  - Credentials            │
│  - Filtering                     │     │  - Styling                │
└────────┬─────────────────────────┘     └───────────────────────────┘
         │
         │
┌────────▼─────────────────────────┐     ┌───────────────────────────┐
│    INTEGRATION LAYER             │     │   UTILITY LAYER           │
├──────────────────────────────────┤     ├───────────────────────────┤
│  fyers_client.py                 │     │  utils.py                 │
│  - Authentication                │     │  - Formatters             │
│  - Quote Fetching                │     │  - Date Helpers           │
│  - Historical Data               │     │  - Search Functions       │
│  - Account Data                  │     │  - Sentiment Indicators   │
│  - Option Chain                  │     └───────────────────────────┘
└────────┬─────────────────────────┘
         │
         │
┌────────▼─────────────────────────┐
│      EXTERNAL API LAYER          │
├──────────────────────────────────┤
│  Fyers API (api-t1.fyers.in)    │
│  - OAuth Authentication          │
│  - Market Data                   │
│  - Account Information           │
│  - Historical Data               │
└──────────────────────────────────┘
```

---

## 🔄 Detailed Component Interaction

### 1. User Authentication Flow

```
User
  │
  └─► Sidebar UI (ui_components.py)
        │
        ├─► Generate Auth URL
        │     └─► FyersClient.get_auth_url()
        │           └─► Opens Fyers Login
        │                 └─► User Authorizes
        │                       └─► Returns auth_code
        │
        └─► Validate Code
              └─► FyersClient.validate_auth_code()
                    └─► Fyers API
                          └─► Returns access_token
                                └─► Store in st.session_state
                                      └─► Client authenticated ✓
```

### 2. Watchlist Data Flow

```
User selects "Watchlist"
  │
  └─► main_new.py routes to render_watchlist_page()
        │
        └─► pages/watchlist.py
              │
              ├─► User searches symbol
              │     └─► utils.search_symbols()
              │           └─► Returns suggestions
              │                 └─► User clicks to add
              │                       └─► Updates st.session_state
              │
              └─► Fetch live data
                    └─► client.fetch_quotes()
                          └─► Fyers API
                                └─► Returns quote data
                                      └─► Build DataFrame
                                            └─► Apply color styling
                                                  └─► Display table
```

### 3. Bull/Bear Analysis Flow

```
User selects "Bull/Bear Dashboard"
  │
  └─► main_new.py routes to render_bull_bear_page()
        │
        └─► pages/bull_bear.py
              │
              ├─► Render Sector Performance
              │     └─► client.fetch_quotes(sector_indices)
              │           └─► Fyers API
              │                 └─► Calculate changes
              │                       └─► Display colored table
              │
              └─► Render Stock Scanner
                    │
                    ├─► User sets filters (sector, volume)
                    │
                    ├─► client.fetch_quotes(SCAN_SYMBOLS)
                    │     └─► Fyers API
                    │           └─► Returns quote data
                    │
                    ├─► For each symbol:
                    │     └─► client.fetch_history()
                    │           └─► Get 20-period volume
                    │                 └─► Get weekly high/low
                    │
                    ├─► data_processor.build_df_from_quotes()
                    │     └─► Transform to DataFrame
                    │
                    ├─► Apply classification
                    │     └─► data_processor.classify_row_advanced()
                    │           │
                    │           ├─► Check: Price vs Weekly High/Low
                    │           ├─► Check: Volume > 2x average
                    │           ├─► Check: OI change > 10%
                    │           └─► Check: Option confirmation
                    │                 └─► Returns "bull" / "bear" / None
                    │
                    ├─► data_processor.apply_filters()
                    │     └─► Filter by sector and volume
                    │
                    └─► Display results
                          ├─► Bullish stocks table
                          ├─► Bearish stocks table
                          └─► Download CSV option
```

### 4. Option Chain Flow

```
User selects "Option Chain"
  │
  └─► main_new.py routes to render_option_chain_page()
        │
        └─► pages/option_chain.py
              │
              ├─► User selects:
              │     ├─► Index (NIFTY/BANKNIFTY)
              │     ├─► Expiry date (utils.get_expiry_dates())
              │     └─► Strike count
              │
              └─► Fetch option chain
                    └─► client.fetch_option_chain()
                          └─► Fyers API
                                └─► Returns option chain
                                      │
                                      ├─► Parse calls and puts
                                      │
                                      ├─► Display tables
                                      │     ├─► Call options (left)
                                      │     └─► Put options (right)
                                      │
                                      └─► Calculate summary
                                            ├─► Total Call OI
                                            ├─► Total Put OI
                                            ├─► PCR ratio
                                            └─► Sentiment indicator
```

### 5. Account Overview Flow

```
User selects "Account Overview"
  │
  └─► main_new.py routes to render_account_page()
        │
        └─► pages/account.py
              │
              ├─► Fetch account data (parallel)
              │     ├─► client.fetch_funds()
              │     ├─► client.fetch_holdings()
              │     └─► client.fetch_positions()
              │           └─► All call Fyers API
              │
              ├─► Calculate P&L
              │     └─► data_processor.calculate_pnl_summary()
              │           ├─► Process holdings P&L
              │           ├─► Process positions P&L
              │           └─► Calculate total P&L
              │
              └─► Render sections
                    ├─► P&L Summary (colored cards)
                    ├─► Funds (metrics)
                    ├─► Holdings (table)
                    └─► Positions (table)
```

---

## 🗄️ Data Models

### Stock Quote Model
```python
{
    "symbol": str,           # e.g., "TCS"
    "name": str,            # e.g., "Tata Consultancy Services"
    "sector": str,          # e.g., "IT"
    "current_close": float, # Latest price
    "prev_close": float,    # Previous close
    "prev_week_high": float,
    "prev_week_low": float,
    "oi_prev": float,       # Open Interest previous
    "oi_current": float,    # Open Interest current
    "vol_20_avg": float,    # 20-period average volume
    "vol_current": float    # Current volume
}
```

### Classification Result Model
```python
{
    "daily_tag": str,       # "bull", "bear", or None
    "vol_ratio": float,     # Current / Average volume
    "oi_change_pct": float, # OI percentage change
    "price_chg_pct": float  # Price percentage change
}
```

### P&L Summary Model
```python
{
    "total_pnl": float,     # Total profit/loss
    "holdings_pnl": float,  # Holdings profit/loss
    "positions_pnl": float  # Positions profit/loss
}
```

---

## 📊 State Management

### Session State Variables

```python
st.session_state = {
    # Authentication
    "fyers_access_token": str,    # Access token
    "fyers_client_id": str,       # Client ID
    
    # Watchlist
    "watchlist_symbols": List[str],  # ["TCS", "RELIANCE", ...]
    
    # Filters
    "selected_sector": str,          # Current sector filter
    
    # Option Chain
    "selected_option_symbol": str,   # "NIFTY50" / "BANKNIFTY"
    
    # Auto-refresh
    "last_auto_refresh": float       # Unix timestamp
}
```

### State Flow

```
Application Start
  │
  └─► initialize_session_state()
        │
        ├─► Set default watchlist
        ├─► Set default filters
        └─► Initialize refresh timer
              │
              └─► User actions modify state
                    │
                    ├─► Add/remove symbols
                    ├─► Change filters
                    ├─► Switch pages
                    └─► Authentication
                          │
                          └─► State persists across pages
                                └─► Auto-refresh updates state
```

---

## 🔐 Security Architecture

### Authentication Flow

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ 1. Request Auth URL
       ▼
┌──────────────┐
│  Streamlit   │
│     App      │
└──────┬───────┘
       │ 2. Generate Auth URL
       ▼
┌──────────────┐
│ FyersClient  │
└──────┬───────┘
       │ 3. Return Auth URL
       ▼
┌──────────────┐
│    User      │
│  (Manual)    │
└──────┬───────┘
       │ 4. Login & Authorize
       ▼
┌──────────────┐
│  Fyers API   │
└──────┬───────┘
       │ 5. Redirect with auth_code
       ▼
┌──────────────┐
│    User      │
│  (Paste)     │
└──────┬───────┘
       │ 6. Submit auth_code
       ▼
┌──────────────┐
│  Streamlit   │
└──────┬───────┘
       │ 7. Validate code
       ▼
┌──────────────┐
│ FyersClient  │
└──────┬───────┘
       │ 8. Request access_token
       ▼
┌──────────────┐
│  Fyers API   │
└──────┬───────┘
       │ 9. Return access_token
       ▼
┌──────────────┐
│ Session      │
│   State      │
└──────────────┘
    (Stored securely)
```

### API Request Security

```
Every API Request:
  │
  ├─► Headers:
  │     └─► Authorization: "{client_id}:{access_token}"
  │
  ├─► HTTPS Only
  │
  └─► Timeout: 10-15 seconds
```

---

## ⚡ Performance Optimizations

### Current Optimizations

1. **Batched API Calls**
   ```python
   # Single call for multiple symbols
   symbols = ["NSE:TCS-EQ", "NSE:INFY-EQ", ...]
   quotes = client.fetch_quotes(symbols)  # Batch request
   ```

2. **Efficient Data Processing**
   ```python
   # DataFrame operations (vectorized)
   df["vol_ratio"] = df["vol_current"] / df["vol_20_avg"]
   ```

3. **Conditional Rendering**
   ```python
   # Only fetch if authenticated
   if client:
       data = client.fetch_quotes(symbols)
   ```

### Future Optimizations

1. **Caching Strategy**
   ```python
   @st.cache_data(ttl=60)  # Cache for 60 seconds
   def fetch_sector_data():
       return client.fetch_quotes(sector_symbols)
   ```

2. **Background Data Fetching**
   ```python
   # Use threading for parallel API calls
   with ThreadPoolExecutor() as executor:
       futures = [
           executor.submit(client.fetch_quotes, batch)
           for batch in symbol_batches
       ]
   ```

3. **WebSocket for Real-time**
   ```python
   # Replace polling with WebSocket
   ws = FyersWebSocket(client_id, access_token)
   ws.subscribe(symbols)
   ```

---

## 🧪 Testing Strategy

### Unit Testing Structure

```
tests/
  ├── test_config.py
  │     └─► Test constant values
  │
  ├── test_fyers_client.py
  │     ├─► Mock API responses
  │     └─► Test error handling
  │
  ├── test_data_processor.py
  │     ├─► Test classification logic
  │     ├─► Test P&L calculations
  │     └─► Test filtering
  │
  ├── test_utils.py
  │     ├─► Test date functions
  │     ├─► Test search function
  │     └─► Test formatters
  │
  └── test_pages/
        ├─► test_watchlist.py
        ├─► test_bull_bear.py
        ├─► test_option_chain.py
        └─► test_account.py
```

### Integration Testing

```python
# Test complete flow
def test_bull_bear_flow():
    # 1. Authenticate
    client = authenticate_test_user()
    
    # 2. Fetch data
    quotes = client.fetch_quotes(SCAN_SYMBOLS)
    
    # 3. Process
    df = build_df_from_quotes(quotes, client)
    
    # 4. Classify
    df["tag"] = df.apply(classify_row_advanced, axis=1)
    
    # 5. Assert
    assert len(df) > 0
    assert "tag" in df.columns
```

---

## 📈 Scalability Considerations

### Current Capacity
- **Users:** Single user per instance
- **Symbols:** ~50 stocks analyzed
- **Refresh Rate:** 10 seconds for watchlist
- **API Calls:** ~100 per minute

### Scaling Strategy

#### Horizontal Scaling
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ User 1  │────▶│  App 1  │     │ User 2  │
└─────────┘     └────┬────┘     └────┬────┘
                     │                │
                     ▼                ▼
                ┌────────────────────────┐
                │    Load Balancer       │
                └────────────────────────┘
                     │         │
                     ▼         ▼
                ┌────────┐ ┌────────┐
                │ App 2  │ │ App 3  │
                └────────┘ └────────┘
```

#### Vertical Scaling
- Increase API rate limits
- Add caching layer (Redis)
- Database for historical data
- Message queue for async tasks

---

## 🔄 Deployment Architecture

### Development Environment
```
Local Machine
  └─► streamlit run main_new.py
        └─► Direct API calls
              └─► Session-based auth
```

### Production Environment (Recommended)
```
┌─────────────────────────────────────────┐
│          Cloud Platform                  │
│  (Streamlit Cloud / AWS / Azure)        │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐    │
│  │   Streamlit App Container       │    │
│  │   - main_new.py                 │    │
│  │   - All modules                 │    │
│  └──────────┬─────────────────────┘    │
│             │                            │
│             ├─► Secrets Manager          │
│             │   (credentials)            │
│             │                            │
│             ├─► Redis Cache              │
│             │   (quotes, history)        │
│             │                            │
│             └─► Logging Service          │
│                 (errors, metrics)        │
│                                          │
└─────────────┬───────────────────────────┘
              │
              ▼
         Fyers API
```

---

## 📝 API Rate Limits

### Fyers API Limits
- **Quotes:** 100 requests/minute
- **History:** 50 requests/minute
- **Account:** 20 requests/minute

### Mitigation Strategy
```python
# 1. Batch requests
symbols = [...50 symbols...]
quotes = client.fetch_quotes(symbols)  # 1 call instead of 50

# 2. Cache results
@st.cache_data(ttl=10)
def get_quotes(symbols):
    return client.fetch_quotes(symbols)

# 3. Rate limiting
time.sleep(0.6)  # 600ms between calls
```

---

## 🎯 Future Enhancements

### Phase 1: Enhanced Analysis
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Support/Resistance levels
- [ ] Pattern recognition
- [ ] Backtesting capability

### Phase 2: Multi-user Support
- [ ] User authentication
- [ ] Personal watchlists
- [ ] Portfolio tracking
- [ ] Alerts system

### Phase 3: Advanced Features
- [ ] Machine learning predictions
- [ ] Sentiment analysis from news
- [ ] Social media integration
- [ ] Mobile app

### Phase 4: Enterprise Features
- [ ] Multi-broker support
- [ ] Team collaboration
- [ ] Compliance reporting
- [ ] Custom strategies

---

**This system design provides a clear blueprint for understanding, maintaining, and extending the Stock Market Analysis Dashboard. Follow these patterns when adding new features!**
