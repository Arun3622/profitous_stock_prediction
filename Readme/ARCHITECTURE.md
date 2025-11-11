# Stock Market Analysis Dashboard - Architecture Documentation

## 📁 Project Structure

```
profitous_stock_prediction/
│
├── main.py                    # Legacy monolithic file (backup)
├── main_new.py               # New entry point - USE THIS
│
├── config.py                 # Configuration & Constants
├── fyers_client.py          # Fyers API Client
├── data_processor.py        # Data Processing & Classification
├── utils.py                 # Utility Functions
├── ui_components.py         # Reusable UI Components
│
├── pages/                   # Page Modules
│   ├── watchlist.py        # Live Watchlist Page
│   ├── bull_bear.py        # Bull/Bear Analysis Page
│   ├── option_chain.py     # Option Chain Page
│   └── account.py          # Account Overview Page
│
├── requirements.txt        # Python Dependencies
└── README.md              # This file
```

## 🎯 Module Responsibilities

### 1. **config.py** - Configuration Layer
**Purpose:** Central configuration management

**Contains:**
- Fyers API credentials and endpoints
- Stock universe with sector mappings (200+ stocks)
- Sector indices mapping
- Scan symbols for bull/bear analysis
- Available sectors for filtering
- Custom CSS styling constants

**Why separate:** 
- Easy to update credentials without touching code
- Single source of truth for all constants
- Improves security (credentials in one place)

---

### 2. **fyers_client.py** - API Integration Layer
**Purpose:** Handles all Fyers API interactions

**Key Classes:**
- `FyersClient`: Main API client with methods for:
  - Authentication (OAuth flow)
  - Fetching quotes
  - Historical data retrieval
  - Account data (funds, holdings, positions)
  - Option chain data

**Key Functions:**
- `get_fyers_client()`: Gets authenticated client from session

**Why separate:**
- Abstraction of API complexity
- Easy to test and mock
- Reusable across different pages
- Clear separation of concerns

---

### 3. **data_processor.py** - Business Logic Layer
**Purpose:** Data transformation and analysis logic

**Key Functions:**
- `build_df_from_quotes()`: Transform API data to DataFrame
- `classify_row_advanced()`: Bull/Bear classification algorithm
- `check_resistance_weakening()`: Option-based resistance analysis
- `check_support_weakening()`: Option-based support analysis
- `apply_filters()`: Sector and volume filtering
- `calculate_pnl_summary()`: P&L calculations
- `percent_change()`: Utility for percentage calculations

**Classification Logic:**
```
BULLISH:
✓ Current Price > Previous Week High
✓ Volume > 2x (20-period average)
✓ OI Change > 10%
✓ Put addition OR Call unwinding

BEARISH:
✓ Current Price < Previous Week Low
✓ Volume > 2x (20-period average)
✓ OI Change > 10%
✓ Call addition OR Put unwinding
```

**Why separate:**
- Complex logic isolated from UI
- Easy to test algorithms
- Can be reused across pages
- Easier to modify classification rules

---

### 4. **utils.py** - Helper Functions Layer
**Purpose:** Generic utility functions

**Key Functions:**
- `get_expiry_dates()`: Calculate option expiry dates
- `format_large_number()`: Number formatting
- `color_positive_negative()`: Style helper
- `get_sentiment_indicator()`: Sentiment calculation
- `format_timestamp()`: Time formatting
- `search_symbols()`: Smart symbol search with priorities

**Why separate:**
- DRY principle (Don't Repeat Yourself)
- Reusable across all modules
- Easy to unit test
- No dependencies on business logic

---

### 5. **ui_components.py** - Presentation Layer
**Purpose:** Reusable Streamlit UI components

**Key Functions:**
- `render_custom_css()`: Apply styling
- `render_sidebar_auth()`: Authentication UI
- `render_sidebar_balance()`: Balance display
- `render_live_indicator()`: Live status indicator
- `render_pnl_card()`: P&L display card
- `render_styled_metric()`: Styled metric boxes
- `render_dataframe_with_colors()`: Colored tables
- `render_navigation()`: Page navigation
- `render_footer()`: Footer section
- `render_search_suggestions()`: Smart search UI

**Why separate:**
- Consistent UI across pages
- Reusable components
- Easy to modify styling
- Reduces code duplication

---

### 6. **pages/** - Feature Modules

#### **pages/watchlist.py**
**Purpose:** Live watchlist with real-time updates

**Features:**
- Symbol search with smart suggestions
- Live quote updates (auto-refresh)
- Add/remove symbols
- Color-coded price changes

#### **pages/bull_bear.py**
**Purpose:** Market analysis and breakout detection

**Features:**
- Sector performance overview
- Bull/Bear stock scanning
- Advanced classification logic
- Filtering by sector and volume
- Export to CSV
- Side-by-side comparison view

#### **pages/option_chain.py**
**Purpose:** Option chain analysis

**Features:**
- Multi-index support (NIFTY, BANKNIFTY, FINNIFTY)
- Expiry date selection
- Strike count customization
- Call/Put OI comparison
- PCR (Put-Call Ratio) calculation
- Sentiment indicators

#### **pages/account.py**
**Purpose:** Portfolio and account management

**Features:**
- Live P&L tracking
- Holdings display with P&L
- Open positions monitoring
- Fund availability
- Color-coded profit/loss

**Why separate pages:**
- Each page is self-contained
- Easy to add new features
- Independent testing
- Clear flow of code
- Parallel development possible

---

### 7. **main_new.py** - Application Entry Point
**Purpose:** Application initialization and routing

**Responsibilities:**
- Configure Streamlit
- Initialize session state
- Handle page routing
- Coordinate components
- Auto-refresh logic

**Flow:**
```
1. Initialize session state
2. Render authentication sidebar
3. Get authenticated client
4. Show navigation
5. Route to selected page
6. Render footer
7. Handle auto-refresh
```

**Why separate:**
- Clean entry point
- Easy to understand flow
- Minimal business logic
- Orchestration only

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main_new.py                          │
│                     (Entry Point)                            │
└─────────┬───────────────────────────────────────────────────┘
          │
          ├─► config.py (Load constants)
          │
          ├─► ui_components.py (Render sidebar auth)
          │
          ├─► fyers_client.py (Get authenticated client)
          │
          └─► Route to page:
              │
              ├─► pages/watchlist.py
              │   ├─► fyers_client.py (Fetch quotes)
              │   ├─► ui_components.py (Render UI)
              │   └─► utils.py (Search symbols)
              │
              ├─► pages/bull_bear.py
              │   ├─► fyers_client.py (Fetch quotes & history)
              │   ├─► data_processor.py (Classify stocks)
              │   ├─► ui_components.py (Render tables)
              │   └─► utils.py (Format data)
              │
              ├─► pages/option_chain.py
              │   ├─► fyers_client.py (Fetch options)
              │   ├─► ui_components.py (Render chain)
              │   └─► utils.py (Get expiries)
              │
              └─► pages/account.py
                  ├─► fyers_client.py (Fetch account data)
                  ├─► data_processor.py (Calculate P&L)
                  └─► ui_components.py (Render metrics)
```

---

## 🚀 Getting Started

### Installation

```powershell
# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```powershell
# Run the NEW modular version
streamlit run main_new.py

# Old version (backup)
# streamlit run main.py
```

### Configuration

Edit `config.py` to update:
- Fyers credentials
- Stock universe
- Sector mappings
- Styling

---

## 🧪 Testing Strategy

### Unit Tests (Recommended)

```python
# Test data_processor.py
def test_percent_change():
    assert percent_change(100, 110) == 10.0
    assert percent_change(100, 90) == -10.0

# Test utils.py
def test_get_expiry_dates():
    dates = get_expiry_dates(2)
    assert len(dates) == 2

# Test classification logic
def test_classify_row_advanced():
    # Test with mock data
    pass
```

### Integration Tests

```python
# Test fyers_client.py
def test_fetch_quotes():
    client = FyersClient(test_id, test_token)
    result = client.fetch_quotes(["NSE:TCS-EQ"])
    assert result["s"] == "ok"
```

---

## 📊 System Design Principles

### 1. **Separation of Concerns**
- Each module has a single responsibility
- Clear boundaries between layers
- Independent modification possible

### 2. **DRY (Don't Repeat Yourself)**
- Reusable components
- Shared utilities
- Common styling

### 3. **Modularity**
- Easy to add new pages
- Easy to add new features
- Easy to remove features

### 4. **Maintainability**
- Clear code organization
- Easy to locate bugs
- Easy to understand flow

### 5. **Scalability**
- Can add more data sources
- Can add more analysis types
- Can add more visualization

---

## 🔧 Customization Guide

### Adding a New Page

1. Create `pages/new_page.py`:
```python
def render_new_page(client):
    st.header("New Feature")
    # Your code here
```

2. Import in `main_new.py`:
```python
from pages.new_page import render_new_page
```

3. Add to navigation:
```python
if page_selection == 'New Feature':
    render_new_page(client)
```

### Adding a New Indicator

1. Add logic to `data_processor.py`:
```python
def calculate_new_indicator(df):
    # Your calculation
    return result
```

2. Use in any page:
```python
from data_processor import calculate_new_indicator

result = calculate_new_indicator(df)
st.metric("New Indicator", result)
```

### Adding a New Stock/Sector

Edit `config.py`:
```python
STOCK_UNIVERSE = {
    "NEWSYMBOL": "NewSector",
    # ... existing stocks
}
```

---

## 🐛 Debugging Guide

### Issue: Import errors
**Solution:** Check that all files are in the correct directory

### Issue: API errors
**Solution:** Check `fyers_client.py` and credentials in `config.py`

### Issue: Classification not working
**Solution:** Check `data_processor.py` logic and thresholds

### Issue: UI not rendering
**Solution:** Check `ui_components.py` and Streamlit version

---

## 📈 Performance Considerations

### Current Performance
- **Modular design:** Faster development
- **Cached components:** Reduced re-rendering
- **Efficient API calls:** Batched requests

### Future Optimizations
- Add `@st.cache_data` for expensive calculations
- Implement connection pooling for API
- Add background data fetching
- Use WebSocket for real-time updates

---

## 🔒 Security Best Practices

### Current
- Credentials in `config.py` (not in code)
- Session-based authentication
- No hardcoded tokens

### Recommended
1. **Use Streamlit Secrets:**
```toml
# .streamlit/secrets.toml
[fyers]
client_id = "YOUR_ID"
client_secret = "YOUR_SECRET"
```

2. **Use Environment Variables:**
```powershell
$env:FYERS_CLIENT_ID="YOUR_ID"
$env:FYERS_SECRET="YOUR_SECRET"
```

3. **Never commit credentials to Git:**
```gitignore
.streamlit/secrets.toml
config.py  # if it contains real credentials
```

---

## 🎓 Learning Resources

### Understanding the Code Flow
1. Start with `main_new.py` - entry point
2. Read `config.py` - understand constants
3. Study `fyers_client.py` - API integration
4. Analyze `data_processor.py` - business logic
5. Review page modules - feature implementation

### Modification Tips
- Always test changes in isolation
- Use print statements for debugging
- Check Streamlit docs for UI components
- Review Fyers API docs for data structure

---

## 📝 Version History

### Version 2.0 (Modular Architecture)
- Split monolithic code into 8+ modules
- Clear separation of concerns
- Improved maintainability
- Added comprehensive documentation

### Version 1.0 (Legacy)
- Single `main.py` file
- All logic in one place
- Harder to maintain and debug

---

## 🤝 Contributing

When modifying the code:
1. Keep module responsibilities clear
2. Update this documentation
3. Add comments to complex logic
4. Test thoroughly before deployment
5. Follow existing code style

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review code comments
3. Check Streamlit documentation
4. Review Fyers API documentation

---

**Remember:** The goal of this architecture is to make the code **easy to read, easy to modify, and easy to debug**. Always keep modules focused on their single responsibility!
