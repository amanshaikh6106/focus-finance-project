
from db import get_db_connection


def get_all_users():
    """Returns a list of all registered users (excluding password hashes)."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        """SELECT id, full_name, username, email, mobile, is_admin,
                  last_login, created_at
           FROM users
           ORDER BY created_at DESC"""
    )
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users


def get_all_eligibility():
    """Returns all eligibility check submissions, most recent first."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eligibility ORDER BY id DESC")
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return records


def get_all_applications():
    """Returns all loan applications, most recent first."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM apply ORDER BY id DESC")
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return records


def get_all_contacts():
    """Returns all contact form messages, most recent first."""
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contact ORDER BY id DESC")
    records = cursor.fetchall()
    cursor.close()
    connection.close()
    return records


def update_application_status(application_id, new_status):
    """
    Updates the status of a loan application (Pending / Approved / Rejected).
    Returns True on success, False on failure.
    """
    if new_status not in ('Pending', 'Approved', 'Rejected'):
        return False

    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE apply SET status = %s WHERE id = %s",
            (new_status, application_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not update application status: {e}")
        return False