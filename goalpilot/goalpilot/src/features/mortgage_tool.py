"""
Mortgage Calculator Tool
For home purchase planning
"""
from typing import Dict, Any
from src.utils.logger import logger

def calculate_mortgage(
    home_price: float,
    down_payment_percent: float = 20.0,
    interest_rate: float = 7.0,
    loan_term_years: int = 30
) -> Dict[str, Any]:
    """
    Calculate mortgage details for home purchase planning
    
    Args:
        home_price: Total home price
        down_payment_percent: Down payment as percentage (default 20%)
        interest_rate: Annual interest rate (default 7%)
        loan_term_years: Loan term in years (default 30)
        
    Returns:
        Dict with mortgage calculations
    """
    logger.info(f"Calculating mortgage for ${home_price:,.2f} home")
    
    down_payment = home_price * (down_payment_percent / 100)
    loan_amount = home_price - down_payment
    
    # Monthly interest rate
    monthly_rate = interest_rate / 100 / 12
    num_payments = loan_term_years * 12
    
    # Monthly payment formula: M = P[r(1+r)^n]/[(1+r)^n-1]
    if monthly_rate > 0:
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / (
            (1 + monthly_rate) ** num_payments - 1
        )
    else:
        monthly_payment = loan_amount / num_payments
    
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - loan_amount
    
    # Property tax estimate (1.2% annually)
    annual_property_tax = home_price * 0.012
    monthly_property_tax = annual_property_tax / 12
    
    # Homeowners insurance estimate (0.5% annually)
    annual_insurance = home_price * 0.005
    monthly_insurance = annual_insurance / 12
    
    # PMI if down payment < 20%
    monthly_pmi = 0
    if down_payment_percent < 20:
        monthly_pmi = loan_amount * 0.005 / 12  # 0.5% annually
    
    total_monthly_payment = (
        monthly_payment + 
        monthly_property_tax + 
        monthly_insurance + 
        monthly_pmi
    )
    
    result = {
        "home_price": round(home_price, 2),
        "down_payment": round(down_payment, 2),
        "loan_amount": round(loan_amount, 2),
        "interest_rate": interest_rate,
        "loan_term_years": loan_term_years,
        "monthly_principal_interest": round(monthly_payment, 2),
        "monthly_property_tax": round(monthly_property_tax, 2),
        "monthly_insurance": round(monthly_insurance, 2),
        "monthly_pmi": round(monthly_pmi, 2),
        "total_monthly_payment": round(total_monthly_payment, 2),
        "total_interest_paid": round(total_interest, 2),
        "total_cost": round(total_paid + down_payment, 2)
    }
    
    logger.info(f"Monthly payment: ${result['total_monthly_payment']:,.2f}")
    return result

__all__ = ["calculate_mortgage"]
