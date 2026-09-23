
from db import get_db_connection


def save_application(data, user_id=None):
    """
    Inserts a loan application form submission into the "apply" table.

    Parameters
    ----------
    data : dict
        Dictionary containing the loan application form fields.
    user_id : int, optional
        The ID of the logged-in user submitting the application.

    Returns
    -------
    bool
        True if the record was saved successfully, False otherwise.
    """
    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        query = """
    INSERT INTO apply
        (user_id, full_name, age, email, mobile, address, city, state,
         occupation, monthly_income, loan_type, loan_amount, loan_tenure, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
        values = (
            user_id,
            data['full_name'],
            data['age'],
            data['email'],
            data['mobile'],
            data['address'],
            data['city'],
            data['state'],
            data['occupation'],
            data['monthly_income'],
            data['loan_type'],
            data['loan_amount'],
            data['loan_tenure'],
            'Pending'
        )
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not save loan application: {e}")
        return False

def get_user_applications(user_id):
    """Returns all loan applications submitted by a specific user, newest first."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM apply WHERE user_id = %s ORDER BY id DESC",
        (user_id,)
    )
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return records