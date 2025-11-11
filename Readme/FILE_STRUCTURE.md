# 📂 Project File Structure

```
profitous_stock_prediction/
│
├── 📄 main.py                          # ⚠️ OLD VERSION (Backup - 1,100+ lines)
│                                       # Monolithic implementation - DO NOT USE
│
├── ⭐ main_new.py                      # ✅ NEW ENTRY POINT (100 lines)
│                                       # USE THIS - Clean modular entry point
│                                       # - Application initialization
│                                       # - Page routing
│                                       # - Auto-refresh logic
│
├── 📋 config.py                        # Configuration Layer (150 lines)
│                                       # - Fyers API credentials
│                                       # - Stock universe (200+ stocks)
│                                       # - Sector mappings
│                                       # - Custom CSS styling
│                                       # - Constants and settings
│
├── 🔌 fyers_client.py                  # API Integration Layer (150 lines)
│                                       # - FyersClient class
│                                       # - Authentication (OAuth)
│                                       # - Quote fetching
│                                       # - Historical data
│                                       # - Account data (funds, holdings, positions)
│                                       # - Option chain data
│
├── 🧮 data_processor.py                # Business Logic Layer (250 lines)
│                                       # - Data transformation
│                                       # - Bull/Bear classification algorithm
│                                       # - Option analysis (resistance/support)
│                                       # - P&L calculations
│                                       # - Filtering and sorting
│
├── 🛠️ utils.py                         # Utility Functions (80 lines)
│                                       # - Date calculations (expiry dates)
│                                       # - Number formatting
│                                       # - Color styling helpers
│                                       # - Sentiment indicators
│                                       # - Symbol search functions
│
├── 🎨 ui_components.py                 # Presentation Layer (200 lines)
│                                       # - Reusable UI components
│                                       # - Sidebar authentication
│                                       # - Live indicators
│                                       # - P&L cards
│                                       # - Styled metrics
│                                       # - Navigation
│                                       # - Footer
│
├── 📁 pages/                           # Feature Modules Directory
│   │
│   ├── 📈 watchlist.py                 # Watchlist Feature (100 lines)
│   │                                   # - Live quote updates
│   │                                   # - Symbol search & suggestions
│   │                                   # - Add/remove symbols
│   │                                   # - Auto-refresh (10 sec)
│   │
│   ├── 🎯 bull_bear.py                 # Bull/Bear Analysis (300 lines)
│   │                                   # - Sector performance table
│   │                                   # - Stock scanner with filters
│   │                                   # - Advanced classification
│   │                                   # - Export to CSV
│   │                                   # - Bullish/Bearish views
│   │
│   ├── 🎲 option_chain.py              # Option Chain Feature (100 lines)
│   │                                   # - Multi-index support
│   │                                   # - Call/Put OI display
│   │                                   # - PCR calculation
│   │                                   # - Sentiment indicators
│   │
│   └── 💼 account.py                   # Account Overview (200 lines)
│                                       # - Live P&L summary
│                                       # - Holdings display
│                                       # - Positions monitoring
│                                       # - Fund availability
│
├── 📖 README.md                        # User Documentation
│                                       # - Quick start guide
│                                       # - Feature overview
│                                       # - Usage instructions
│                                       # - Troubleshooting
│
├── 📚 ARCHITECTURE.md                  # Developer Documentation
│                                       # - Module responsibilities
│                                       # - Data flow diagrams
│                                       # - Customization guide
│                                       # - Testing strategy
│                                       # - Detailed explanations
│
├── 📊 SYSTEM_DESIGN.md                 # System Design Documentation
│                                       # - Architecture diagrams
│                                       # - Component interactions
│                                       # - State management
│                                       # - Security architecture
│                                       # - Performance considerations
│                                       # - Scaling strategy
│
├── 🔄 MIGRATION_GUIDE.md               # Migration Documentation
│                                       # - Old vs New comparison
│                                       # - Code examples
│                                       # - Migration checklist
│                                       # - Troubleshooting
│                                       # - Benefits overview
│
└── 📦 requirements.txt                 # Python Dependencies
                                        # - streamlit>=1.24.0
                                        # - pandas>=1.5.0
                                        # - numpy>=1.24.0
                                        # - plotly>=5.0.0
                                        # - requests>=2.28.0
```

---

## 🎯 Module Interaction Map

```
                    ┌──────────────────────┐
                    │    main_new.py       │
                    │   (Entry Point)      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    config.py         │
                    │  (Configuration)     │
                    └──────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
        ┌───────▼────────┐ ┌──▼───────┐ ┌───▼──────────┐
        │ fyers_client.py│ │ utils.py │ │ui_components │
        │  (API Client)  │ │(Helpers) │ │   (UI)       │
        └────────┬───────┘ └──────────┘ └───┬──────────┘
                 │                           │
                 │      ┌────────────────────┤
                 │      │                    │
        ┌────────▼──────▼─────┐             │
        │  data_processor.py   │             │
        │  (Business Logic)    │             │
        └──────────────────────┘             │
                 │                            │
                 └────────────┬───────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
        ┌───────▼──┐  ┌───────▼──┐  ┌──────▼──────┐
        │watchlist │  │bull_bear │  │option_chain │
        │   .py    │  │   .py    │  │    .py      │
        └──────────┘  └──────────┘  └─────────────┘
                              │
                      ┌───────▼────────┐
                      │  account.py    │
                      └────────────────┘
```

---

## 📊 Code Distribution

```
Total Lines: ~1,530

config.py          ████░░ (150 lines, 10%)
fyers_client.py    ████░░ (150 lines, 10%)
data_processor.py  ████████ (250 lines, 16%)
utils.py           ██░░░░ (80 lines, 5%)
ui_components.py   ██████░ (200 lines, 13%)
main_new.py        ███░░░ (100 lines, 7%)

pages/watchlist.py      ███░░░ (100 lines, 7%)
pages/bull_bear.py      █████████░ (300 lines, 20%)
pages/option_chain.py   ███░░░ (100 lines, 7%)
pages/account.py        ██████░ (200 lines, 13%)
```

---

## 🔍 Where to Find What

| Need to... | Look in... |
|------------|-----------|
| 🔑 Change API credentials | `config.py` |
| ➕ Add new stock symbols | `config.py` → `STOCK_UNIVERSE` |
| 🎨 Modify styling/colors | `config.py` → `CUSTOM_CSS` |
| 🔌 Debug API calls | `fyers_client.py` |
| 📊 Modify classification logic | `data_processor.py` → `classify_row_advanced()` |
| 📅 Change date calculations | `utils.py` |
| 🎯 Add new UI component | `ui_components.py` |
| 📈 Modify watchlist feature | `pages/watchlist.py` |
| 🐂🐻 Change bull/bear logic | `pages/bull_bear.py` |
| 🎲 Update option chain | `pages/option_chain.py` |
| 💼 Modify account display | `pages/account.py` |
| 🚀 Change app structure | `main_new.py` |

---

## 🎓 Reading Order for New Developers

1. **Start Here:** `README.md`
   - Understand what the app does
   - Learn how to run it

2. **Architecture:** `ARCHITECTURE.md`
   - Understand module responsibilities
   - Learn data flows

3. **Entry Point:** `main_new.py`
   - See how app initializes
   - Understand routing

4. **Configuration:** `config.py`
   - See all constants
   - Understand stock universe

5. **API Layer:** `fyers_client.py`
   - Learn API integration
   - Understand authentication

6. **Business Logic:** `data_processor.py`
   - Study classification algorithm
   - Understand data transformations

7. **Pages:** `pages/*.py`
   - See feature implementations
   - Understand user flows

8. **Deep Dive:** `SYSTEM_DESIGN.md`
   - Complete system understanding
   - Advanced concepts

---

## 🛠️ Modification Quick Guide

### Add a New Stock
```python
# File: config.py
# Line: ~15
STOCK_UNIVERSE = {
    "NEWSTOCK": "Technology",  # ← Add here
    # ... rest
}
```

### Change Volume Threshold
```python
# File: data_processor.py
# Function: classify_row_advanced()
vol_condition = vol_ratio >= 2.0  # ← Change 2.0 to desired value
```

### Add New Page
```python
# 1. Create: pages/new_feature.py
def render_new_feature(client):
    st.header("New Feature")
    # Your code

# 2. Import in: main_new.py
from pages.new_feature import render_new_feature

# 3. Add routing in: main_new.py
if page_selection == 'New Feature':
    render_new_feature(client)
```

### Change Styling
```python
# File: config.py
# Variable: CUSTOM_CSS
# Modify the CSS string
```

---

## 📏 Code Quality Metrics

- **Modularity:** ✅ Excellent (8 separate modules)
- **Cohesion:** ✅ High (each module has clear purpose)
- **Coupling:** ✅ Low (modules are independent)
- **Readability:** ✅ High (clear structure, comments)
- **Maintainability:** ✅ High (easy to modify)
- **Testability:** ✅ High (isolated components)
- **Documentation:** ✅ Comprehensive (4 detailed docs)

---

## 🎯 Key Files Priority

### 🔴 Critical (Touch carefully)
- `main_new.py` - Entry point
- `fyers_client.py` - API integration
- `config.py` - Core configuration

### 🟡 Important (Modify with testing)
- `data_processor.py` - Business logic
- `pages/bull_bear.py` - Main feature
- `ui_components.py` - UI consistency

### 🟢 Safe (Easy to modify)
- `utils.py` - Helper functions
- `pages/watchlist.py` - Isolated feature
- `pages/option_chain.py` - Isolated feature
- `pages/account.py` - Isolated feature

---

**This structure makes the codebase maintainable, testable, and easy to understand! 🚀**
