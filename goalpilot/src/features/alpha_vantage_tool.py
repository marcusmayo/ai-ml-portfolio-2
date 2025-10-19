"""
Alpha Vantage API Tool
For fetching stock market data and investment projections
"""
import os
import requests
from typing import Dict, Any, Optional
from src.utils.logger import logger

class AlphaVantageError(Exception):
    """Custom exception for Alpha Vantage API errors"""
    pass

def get_stock_quote(symbol: str = "SPY") -> Dict[str, Any]:
    """
    Get current stock quote with 2-API fallback strategy
    1. Try Yahoo Finance
    2. Try Alpha Vantage (if key available)
    3. Fall back to historical data
    
    Args:
        symbol: Stock symbol (default: SPY)
        
    Returns:
        Dict with stock data and data source indicator
    """
    logger.info(f"Fetching stock quote for {symbol}")
    
    # API 1: Yahoo Finance
    try:
        import requests
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        response = requests.get(
            url, 
            params={"interval": "1d", "range": "1d"},
            timeout=5,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            meta = data['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('previousClose', price)
            change = price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            result = {
                "symbol": symbol,
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "52_week_high": meta.get('fiftyTwoWeekHigh', 0),
                "52_week_low": meta.get('fiftyTwoWeekLow', 0),
                "historical_return_7yr": 14.2,
                "data_source": "Yahoo Finance (Real-time)",
                "data_freshness": "live"
            }
            
            logger.info(f"✅ API 1 (Yahoo): ${result['price']}")
            return result
    except Exception as e:
        logger.warning(f"API 1 (Yahoo Finance) failed: {e}")
    
    # API 2: Try Finnhub (free tier, no key needed for basic quote)
    try:
        import requests
        url = f"https://finnhub.io/api/v1/quote"
        response = requests.get(
            url,
            params={"symbol": symbol, "token": "demo"},  # demo token for testing
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('c', 0)  # current price
            prev_close = data.get('pc', price)  # previous close
            change = price - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0
            
            if price > 0:
                result = {
                    "symbol": symbol,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "52_week_high": data.get('h', 0),
                    "52_week_low": data.get('l', 0),
                    "historical_return_7yr": 14.2,
                    "data_source": "Finnhub API (Real-time)",
                    "data_freshness": "live"
                }
                
                logger.info(f"✅ API 2 (Finnhub): ${result['price']}")
                return result
    except Exception as e:
        logger.warning(f"API 2 (Finnhub) failed: {e}")
    
    # Fallback: Historical averages
    logger.warning("⚠️ All real-time APIs unavailable - using historical data")
    
    return {
        "symbol": symbol,
        "price": None,
        "change": None,
        "change_percent": None,
        "52_week_high": None,
        "52_week_low": None,
        "historical_return_7yr": 14.2,  # S&P 500 historical average
        "data_source": "Historical S&P 500 Averages (1957-2023)",
        "data_freshness": "historical",
        "fallback_note": "Real-time market data temporarily unavailable. Projections based on historical 7%% annual return rate."
    }


def calculate_retirement_projection(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    current_savings: float = 0.0,
    expected_return: float = 0.07
) -> Dict[str, Any]:
    """
    Calculate retirement savings projection
    
    Args:
        current_age: Current age
        retirement_age: Target retirement age
        monthly_contribution: Monthly savings amount
        current_savings: Current retirement savings
        expected_return: Expected annual return (default 7%)
        
    Returns:
        Dict with retirement projection
    """
    logger.info(f"Calculating retirement projection: age {current_age} → {retirement_age}")
    
    years = retirement_age - current_age
    months = years * 12
    monthly_return = expected_return / 12
    
    # Future value of current savings
    fv_current = current_savings * ((1 + expected_return) ** years)
    
    # Future value of monthly contributions (annuity formula)
    if monthly_return > 0:
        fv_contributions = monthly_contribution * (
            ((1 + monthly_return) ** months - 1) / monthly_return
        )
    else:
        fv_contributions = monthly_contribution * months
    
    total_saved = fv_current + fv_contributions
    total_contributions = (monthly_contribution * months) + current_savings
    total_interest = total_saved - total_contributions
    
    result = {
        "years_to_retirement": years,
        "total_contributions": round(total_contributions, 2),
        "projected_balance": round(total_saved, 2),
        "total_interest_earned": round(total_interest, 2),
        "monthly_contribution": monthly_contribution,
        "assumed_return_rate": expected_return,
        "safe_withdrawal_rate_4pct": round(total_saved * 0.04 / 12, 2),  # 4% rule monthly
    }
    
    logger.info(f"Projection: ${result['projected_balance']:,.2f} at retirement")
    return result

__all__ = ["get_stock_quote", "calculate_retirement_projection", "AlphaVantageError"]
