

from db import get_db_connection

# Eligibility rule thresholds (kept as constants so they are easy to tune)
MIN_AGE = 21
MIN_MONTHLY_INCOME = 25000
MIN_CREDIT_SCORE = 650
MAX_EMI_RATIO = 0.40  # Existing EMI must not exceed 40% of monthly income


def calculate_eligibility(data):
    """
    Evaluates loan eligibility based on the rules defined for FocusFinance.

    Parameters
    ----------
    data : dict
        Dictionary containing the form fields submitted by the user.

    Returns
    -------
    tuple (result, reasons)
        result  : "Eligible" or "Not Eligible"
        reasons : list of strings explaining any failed conditions
    """
    age = int(data['age'])
    monthly_income = float(data['monthly_income'])
    credit_score = int(data['credit_score'])
    existing_emi = float(data['existing_emi'])
    monthly_savings = float(data['monthly_savings'])

    reasons = []
    eligible = True

    if age < MIN_AGE:
        eligible = False
        reasons.append(f"Age must be {MIN_AGE} or above.")

    if monthly_income < MIN_MONTHLY_INCOME:
        eligible = False
        reasons.append(f"Monthly income must be at least ₹{MIN_MONTHLY_INCOME:,}.")

    if credit_score < MIN_CREDIT_SCORE:
        eligible = False
        reasons.append(f"Credit score must be at least {MIN_CREDIT_SCORE}.")

    if existing_emi > (MAX_EMI_RATIO * monthly_income):
        eligible = False
        reasons.append("Existing EMI exceeds 40% of your monthly income.")

    if monthly_savings <= 0:
        eligible = False
        reasons.append("Monthly savings must be greater than 0.")

    result = "Eligible" if eligible else "Not Eligible"
    return result, reasons


def save_eligibility(data, result, user_id=None):
    """
    Inserts the eligibility form data and the calculated result
    into the MySQL "eligibility" table.

    Returns True on success, False on failure.
    """
    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO eligibility
                (user_id, full_name, age, gender, mobile, email, employment_type,
                 monthly_income, monthly_expenses, monthly_savings, existing_emi,
                 credit_score, loan_type, loan_amount, loan_tenure, result)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id,
            data['full_name'],
            data['age'],
            data['gender'],
            data['mobile'],
            data['email'],
            data['employment_type'],
            data['monthly_income'],
            data['monthly_expenses'],
            data['monthly_savings'],
            data['existing_emi'],
            data['credit_score'],
            data['loan_type'],
            data['loan_amount'],
            data['loan_tenure'],
            result
        )
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not save eligibility record: {e}")
        return False
