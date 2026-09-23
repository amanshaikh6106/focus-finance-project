
LOAN_INTEREST_RATES = {
    "Home Loan": 8.5,
    "Vehicle Loan": 9.5,
    "Education Loan": 8.0,
    "Business Loan": 11.0,
    "Personal Loan": 12.5,
    "Agriculture Loan": 7.0,
}

DEFAULT_INTEREST_RATE = 10.0  


def calculate_emi(loan_amount, loan_tenure_months, loan_type):
    """
    Calculates the estimated monthly EMI, total interest, and total
    payment for a given loan amount, tenure (in months), and loan type.

    Returns a dict: { emi, total_interest, total_payment, interest_rate }
    """
    principal = float(loan_amount)
    tenure = int(loan_tenure_months)
    annual_rate = LOAN_INTEREST_RATES.get(loan_type, DEFAULT_INTEREST_RATE)
    monthly_rate = annual_rate / 12 / 100

    if tenure <= 0:
        return {
            "emi": 0,
            "total_interest": 0,
            "total_payment": 0,
            "interest_rate": annual_rate
        }

    if monthly_rate == 0:
        emi = principal / tenure
    else:
        factor = (1 + monthly_rate) ** tenure
        emi = (principal * monthly_rate * factor) / (factor - 1)

    total_payment = emi * tenure
    total_interest = total_payment - principal

    return {
        "emi": round(emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
        "interest_rate": annual_rate
    }