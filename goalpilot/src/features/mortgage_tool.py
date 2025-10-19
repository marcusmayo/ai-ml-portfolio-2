"""
Mortgage calculator tool
"""
from typing import Dict, Any
from src.utils.logger import logger

def calculate_mortgage(
    home_price: float,
    down_payment_percent: float,
    interest_rate: float,
    loan_term_years: int
) -> Dict[str, Any]:
    """
    Calculate mortgage payment and total cost
    
    Args:
        home_price: Total home price
        down_payment_percent: Down payment as percentage (e.g., 20 for 20%)
        interest_rate: Annual interest rate (e.g., 7.0 for 7%)
        loan_term_years: Loan term in years (typically 15 or 30)
        
    Returns:
        Dict with monthly payment, total interest, etc.
    """
    # Calculate loan amount
    down_payment = home_price * (down_payment_percent / 100)
    loan_amount = home_price - down_payment
    
    # Convert annual rate to monthly
    monthly_rate = (interest_rate / 100) / 12
    num_payments = loan_term_years * 12
    
    # Calculate monthly payment using amortization formula
    if monthly_rate > 0:
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** num_payments
        ) / (
            (1 + monthly_rate) ** num_payments - 1
        )
    else:
        monthly_payment = loan_amount / num_payments
    
    # Calculate totals
    total_paid = monthly_payment * num_payments
    total_interest = total_paid - loan_amount
    
    # Estimate additional costs (property tax, insurance, PMI)
    monthly_property_tax = (home_price * 0.012) / 12  # ~1.2% annual
    monthly_insurance = (home_price * 0.005) / 12     # ~0.5% annual
    monthly_pmi = 0
    
    # PMI if down payment < 20%
    if down_payment_percent < 20:
        monthly_pmi = loan_amount * 0.005 / 12  # ~0.5% of loan amount annually
    
    total_monthly_payment = monthly_payment + monthly_property_tax + monthly_insurance + monthly_pmi
    
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
