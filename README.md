# Stock Market Sector & Stock Analysis Dashboard (mock)

This is a small Streamlit prototype implementing your requested dashboard using mock data. It demonstrates:

- Sector stacked bar chart (Bull vs Bear counts) using Plotly.
- Clickable sector bars (requires `streamlit-plotly-events`) to list stocks in a sector.
- Side-by-side Daily and Weekly Bull/Bear tables using the exact filtering logic you specified (implemented against mock data):
  - Price strength: current close vs prior high/low per timeframe
  - Open Interest (OI) change threshold: > 10% (bull) / < -10% (bear)
  - Implied Volatility (IV): current > previous high (bull) / current < previous high (bear)
  - Volume: current > 2x 20-period average (bull) / current < 0.5x average (bear)

Notes and security
- This app uses mock data only — no live API integration is enabled.
- Do NOT hardcode FYERS app secrets in source code. Use Streamlit secrets manager (`.streamlit/secrets.toml`) or environment variables.

Run locally (Windows PowerShell):

```powershell
pip install -r requirements.txt
streamlit run main.py
```

If you want click interactions on the Plotly chart, make sure `streamlit-plotly-events` installs correctly. If it's missing, the chart will still render but clicks won't be captured by the app; a sector dropdown could be used as fallback.

Next steps / suggestions
- Replace mock data with FYERS `history` / `quotes` / `depth` endpoints.
- Move FYERS App ID / Secret into `st.secrets` and implement OAuth flow on a backend for production.
- If you need richer click interactions, consider a small Dash app for more natural Plotly event handling, or keep using streamlit-plotly-events.

FYERS secrets example (recommended)

Create a file `.streamlit/secrets.toml` in the project root (do NOT commit this file). Put:

```toml
[fyers]
client_id = "YOUR_APP_ID-100"
client_secret = "YOUR_APP_SECRET"
redirect_uri = "https://www.google.com"
```

The app will automatically read `st.secrets.fyers` if available. Otherwise paste credentials in the FYERS login expander in the app.
