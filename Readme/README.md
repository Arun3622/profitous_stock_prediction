# 📊 Stock Market Analysis Dashboard

Professional real-time market analysis tool with live data from Fyers API. Features bull/bear detection, sector analysis, option chain monitoring, and portfolio tracking.

## ✨ Features

### 📈 Live Watchlist
- Real-time quote updates with auto-refresh (10 seconds)
- Smart symbol search with suggestions
- Color-coded price movements
- Easy add/remove symbols

### 🎯 Bull/Bear Dashboard
- **Advanced Classification Algorithm:**
  - ✅ Price breakout above weekly high/low
  - ✅ Volume > 2x average (20-period)
  - ✅ OI change > 10%
  - ✅ Option confirmation (Put/Call analysis)
- Sector performance overview (13+ sectors)
- Customizable filters (sector, volume ratio)
- Export to CSV
- Side-by-side comparison view

### 🎲 Option Chain
- Multi-index support (NIFTY, BANKNIFTY, FINNIFTY)
- Live Call/Put data with OI and IV
- PCR (Put-Call Ratio) calculation
- Sentiment indicators
- Customizable expiry and strike count

### 💼 Account Overview
- Live P&L tracking
- Holdings display with profit/loss
- Open positions monitoring
- Fund availability and margin usage
- Color-coded performance metrics

## 🏗️ Architecture

**NEW MODULAR STRUCTURE** - Code split into logical modules for better readability and maintenance:

```
profitous_stock_prediction/
├── main_new.py              # ⭐ Entry point (USE THIS)
├── config.py                # Configuration & constants
├── fyers_client.py          # API integration layer
├── data_processor.py        # Business logic & classification
├── utils.py                 # Utility functions
├── ui_components.py         # Reusable UI components
├── pages/                   # Feature modules
│   ├── watchlist.py
│   ├── bull_bear.py
│   ├── option_chain.py
│   └── account.py
├── ARCHITECTURE.md          # 📖 Detailed architecture docs
├── SYSTEM_DESIGN.md         # 📊 System design diagrams
└── requirements.txt
```

**📚 Documentation:**
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Module responsibilities, data flow, customization guide
- **[SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md)** - Complete system design with diagrams and flows

## 🚀 Quick Start

### Installation

```powershell
# Clone or download the project
cd profitous_stock_prediction

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```powershell
# Run the MODULAR version (recommended)
streamlit run main_new.py

# Old monolithic version (backup)
# streamlit run main.py
```

### First-Time Setup

1. **Get Fyers API Credentials:**
   - Sign up at [Fyers](https://fyers.in/)
   - Create an API app
   - Get your Client ID and Secret

2. **Configure Credentials:**
   
   **Option A: Edit config.py** (Quick start)
   ```python
   # Edit config.py
   FYERS_CLIENT_ID = "YOUR_CLIENT_ID"
   FYERS_CLIENT_SECRET = "YOUR_SECRET"
   ```

   **Option B: Use Secrets** (Recommended for production)
   ```toml
   # Create .streamlit/secrets.toml
   [fyers]
   client_id = "YOUR_CLIENT_ID"
   client_secret = "YOUR_SECRET"
   redirect_uri = "https://www.google.com"
   ```

3. **Authenticate:**
   - Open the app
   - Click "Generate Auth URL" in sidebar
   - Login to Fyers
   - Copy the `auth_code` from URL
   - Paste and click "Validate & Connect"

## 📖 Usage Guide

### Watchlist
1. Search and add stocks using smart search
2. View live prices with auto-refresh
3. Remove symbols when needed

### Bull/Bear Analysis
1. View sector performance heatmap
2. Apply filters (sector, volume ratio)
3. See TODAY'S fresh breakouts
4. Export results to CSV

### Option Chain
1. Select index (NIFTY/BANKNIFTY)
2. Choose expiry date
3. Set strike count
4. Analyze Call/Put OI and PCR

### Account Overview
1. View live P&L summary
2. Check holdings performance
3. Monitor open positions
4. Track fund availability

## 🎯 Key Benefits of Modular Architecture

### ✅ Better Readability
- Each file has a clear purpose
- Easy to find specific functionality
- Clean separation of concerns

### ✅ Easier Debugging
- Isolate issues to specific modules
- Test components independently
- Clear error tracing

### ✅ Simpler Modifications
- Add new features without breaking existing code
- Modify classification logic in one place
- Update UI components globally

### ✅ Better Collaboration
- Multiple developers can work simultaneously
- Clear module boundaries
- Self-documenting structure

## 🔧 Customization

### Adding New Stocks
Edit `config.py`:
```python
STOCK_UNIVERSE = {
    "NEWSYMBOL": "Sector",
    # ... existing stocks
}
```

### Modifying Classification Logic
Edit `data_processor.py`:
```python
def classify_row_advanced(row, option_data=None):
    # Modify thresholds or add new conditions
    vol_ratio_threshold = 2.0  # Change this
    oi_threshold = 10.0        # Change this
    # ... rest of logic
```

### Adding New Pages
1. Create `pages/new_feature.py`
2. Import in `main_new.py`
3. Add to navigation

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed customization guide.

## 🔒 Security Best Practices

**⚠️ IMPORTANT:** Never commit real credentials to Git!

```gitignore
# Add to .gitignore
.streamlit/secrets.toml
config.py  # if it contains real credentials
*.pyc
__pycache__/
```

**Recommended approach:**
- Use Streamlit secrets for production
- Use environment variables
- Keep `config.py` with placeholder values only

## 📊 Bull/Bear Classification Algorithm

```
BULLISH CRITERIA:
├─ Price > Previous Week High ✓
├─ Volume > 2x (20-period average) ✓
├─ OI Change > 10% ✓
└─ Put addition OR Call unwinding ✓

BEARISH CRITERIA:
├─ Price < Previous Week Low ✓
├─ Volume > 2x (20-period average) ✓
├─ OI Change > 10% ✓
└─ Call addition OR Put unwinding ✓
```

## 🐛 Troubleshooting

### Import Errors
- Ensure all files are in correct directories
- Check Python path includes project root

### API Authentication Fails
- Verify credentials in `config.py`
- Check redirect URI matches Fyers app settings
- Ensure auth_code is fresh (expires quickly)

### Classification Not Working
- Check thresholds in `data_processor.py`
- Verify historical data is fetching correctly
- Review console for error messages

### UI Not Rendering
- Check Streamlit version (`pip install --upgrade streamlit`)
- Review browser console for errors
- Clear Streamlit cache

## 📚 Learning Resources

### Understanding the Codebase
1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) - Module responsibilities
2. Review [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) - System flows
3. Start with `main_new.py` - Entry point
4. Study `config.py` - Constants
5. Explore page modules - Features

### API Documentation
- [Fyers API Docs](https://myapi.fyers.in/docs/)
- [Streamlit Docs](https://docs.streamlit.io/)

## 📈 Performance Notes

- **API Calls:** Batched to minimize requests
- **Auto-refresh:** 10-second interval for watchlist
- **Caching:** Can be added for expensive operations
- **Rate Limits:** Respects Fyers API limits

## 🤝 Contributing

When modifying code:
1. Keep module responsibilities clear
2. Update documentation
3. Add comments for complex logic
4. Test thoroughly
5. Follow existing code style

## 📝 Version History

### v2.0 - Modular Architecture (Current)
- ✅ Split into 8+ focused modules
- ✅ Clear separation of concerns
- ✅ Comprehensive documentation
- ✅ Improved maintainability
- ✅ Better debugging capability

### v1.0 - Monolithic (Legacy)
- Single file implementation
- All logic in main.py
- Harder to maintain

## 📞 Support

For questions or issues:
1. Check [ARCHITECTURE.md](./ARCHITECTURE.md)
2. Review [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md)
3. Check code comments
4. Review Fyers API documentation

## 📄 License

This project is for educational and personal use. Ensure compliance with Fyers API terms of service.

---

**🎓 Remember:** The modular structure makes the code easy to read, modify, and debug. Each module has a single clear purpose. Happy trading! 📈
