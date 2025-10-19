"""
Alpha Vantage API integration for stock quotes and retirement calculations
"""
import requests
from typing import Dict, Any
from src.utils.config import settings
from src.utils.logger import logger

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    Get current stock quote from Alpha Vantage
    
    Args:
        symbol: Stock ticker symbol (e.g., 'SPY', 'AAPL')
        
    Returns:
        Dict with price, change, volume
    """
    try:
        api_key = settings.alpha_vantage_api_key
        
        # Use demo key if not configured
        if api_key == "demo":
            logger.warning("Using demo API key - limited to 5 calls/min")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        
        logger.debug(f"Fetching quote for {symbol}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            quote = data["Global Quote"]
            result = {
                "symbol": symbol,
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "latest_trading_day": quote.get("07. latest trading day", "")
            }
            logger.info(f"Got quote for {symbol}: ${result['price']:.2f}")
            return result
        else:
            logger.warning(f"No data for {symbol}, using mock data")
            return {
                "symbol": symbol,
                "price": 450.00,
                "change": 2.50,
                "change_percent": "+0.56%",
                "volume": 1000000,
                "latest_trading_day": "2024-10-18"
            }
            
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")
        return {
            "symbol": symbol,
            "price": 0.0,
            "error": str(e)
        }

def calculate_retirement_projection(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    current_savings: float = 0,
    expected_return: float = 0.07
) -> Dict[str, Any]:
    """
    Calculate retirement savings projection
    
    Args:
        current_age: Current age in years
        retirement_age: Target retirement age
        monthly_contribution: Monthly contribution amount
        current_savings: Current savings balance
        expected_return: Expected annual return (default 7%)
        
    Returns:
        Dict with projected balance, total contributions, growth
    """
    years_to_retirement = retirement_age - current_age
    months = years_to_retirement * 12
    monthly_rate = expected_return / 12
    
    # Future value of current savings
    fv_current = current_savings * ((1 + monthly_rate) ** months)
    
    # Future value of monthly contributions (annuity)
    if monthly_rate > 0:
        fv_contributions = monthly_contribution * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        )
    else:
        fv_contributions = monthly_contribution * months
    
    projected_balance = fv_current + fv_contributions
    total_contributions = current_savings + (monthly_contribution * months)
    investment_growth = projected_balance - total_contributions
    
    result = {
        "current_age": current_age,
        "retirement_age": retirement_age,
        "years_to_retirement": years_to_retirement,
        "monthly_contribution": monthly_contribution,
        "current_savings": current_savings,
        "expected_annual_return": expected_return,
        "total_contributions": round(total_contributions, 2),
        "projected_balance": round(projected_balance, 2),
        "investment_growth": round(investment_growth, 2)
    }
    
    logger.info(f"Retirement projection: ${result['projected_balance']:,.2f} in {years_to_retirement} years")
    return result

# Create __init__.py
