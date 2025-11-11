"""
Fyers API Client Module
Handles all interactions with Fyers API for authentication and data retrieval
"""

import requests
import hashlib
import urllib.parse
from typing import Dict, List, Optional
import streamlit as st
from config import FYERS_BASE, FYERS_CLIENT_ID
from fyers_apiv3 import fyersModel



class FyersClient:
    """Client for interacting with Fyers API"""
    
    def __init__(self, client_id: str, client_secret: str = None, access_token: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = FYERS_BASE
        self.fyers = fyersModel.FyersModel(client_id=FYERS_CLIENT_ID, token=access_token, is_async=False)
        
    
    @staticmethod
    def get_auth_url(client_id: str, redirect_uri: str, state: str) -> str:
        """Generate authorization URL for OAuth flow"""
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{FYERS_BASE}/api/v3/generate-authcode?" + urllib.parse.urlencode(params)
    
    @staticmethod
    def compute_appid_hash(client_id: str, client_secret: str) -> str:
        """Compute SHA256 hash of client_id:client_secret"""
        combo = f"{client_id}:{client_secret}".encode("utf-8")
        return hashlib.sha256(combo).hexdigest()
    
    def validate_auth_code(self, code: str) -> Dict:
        """Validate authorization code and get access token"""
        url = f"{self.base_url}/api/v3/validate-authcode"
        appIdHash = self.compute_appid_hash(self.client_id, self.client_secret)
        payload = {
            "grant_type": "authorization_code",
            "appIdHash": appIdHash,
            "code": code,
        }
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    
    def fetch_quotes(self, symbols: List[str]) -> Dict:
        """Fetch live quotes from Fyers API"""
        try:
            url = f"{self.base_url}/data/quotes?symbols=" + urllib.parse.quote(",".join(symbols))
            auth_header = f"{self.client_id}:{self.access_token}"
            headers = {"Authorization": auth_header}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            st.error(f"Quotes fetch error: {e}")
            return {"s": "error", "message": str(e)}
    
    def fetch_history(self, symbol: str, resolution: str, date_from: str, 
                     date_to: str) -> Dict:
        """Fetch historical data for volume and price analysis"""
        try:
            url = f"{self.base_url}/data/history"
            auth_header = f"{self.client_id}:{self.access_token}"
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
    
    def fetch_funds(self) -> Dict:
        """Fetch account funds"""
        try:
            url = f"{self.base_url}/api/v3/funds"
            auth_header = f"{self.client_id}:{self.access_token}"
            headers = {"Authorization": auth_header}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"s": "error", "message": str(e)}
    
    def fetch_holdings(self) -> Dict:
        """Fetch holdings"""
        try:
            url = f"{self.base_url}/api/v3/holdings"
            auth_header = f"{self.client_id}:{self.access_token}"
            headers = {"Authorization": auth_header}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"s": "error", "message": str(e)}
    
    def fetch_positions(self) -> Dict:
        """Fetch positions"""
        try:
            url = f"{self.base_url}/api/v3/positions"
            auth_header = f"{self.client_id}:{self.access_token}"
            headers = {"Authorization": auth_header}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"s": "error", "message": str(e)}
    
    def fetch_option_chain(self, symbol: str, expiry_date: str, strike_count: int = 50) -> Dict:
        """Fetch option chain data"""
        try:
            if symbol == "NIFTY50":
                option_symbol = "NSE:NIFTY50-INDEX"
            elif symbol == "BANKNIFTY":
                option_symbol = "NSE:NIFTYBANK-INDEX"
            else:
                option_symbol = symbol
            
            data = {
                "symbol": option_symbol,
                "strikecount": strike_count,
                "timestamp": ""
            }

            response = self.fyers.optionchain(data=data)
            print("----------------option chain------------------\n")
            print(response)
            print("----------------------------------------------\n")
           
            return response
        except Exception as e:
            return {"s": "error", "message": str(e)}


def get_fyers_client() -> Optional[FyersClient]:
    """Get Fyers client from session state"""
    if st.session_state.get("fyers_access_token"):
        return FyersClient(
            client_id=st.session_state.get("fyers_client_id"),
            access_token=st.session_state.get("fyers_access_token")
        )
    return None
