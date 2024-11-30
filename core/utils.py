from decimal import Decimal

def calculate_total(transactions):
    """Calculate total amount from transactions"""
    return sum(t.amount for t in transactions)

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}" 