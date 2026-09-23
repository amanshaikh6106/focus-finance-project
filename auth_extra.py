

from werkzeug.security import generate_password_hash
from db import get_db_connection


def change_user_password(user_id, new_hashed_password):
    """Updates the password for a given user_id. Returns True/False."""
    connection = get_db_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_hashed_password, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not change password: {e}")
        return False


def verify_identity_for_reset(username, email, mobile):
    """
    Verifies that the given username, email, and mobile number all
    belong to the same account. Returns the user's id if verified,
    otherwise None.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id FROM users WHERE username = %s AND email = %s AND mobile = %s",
        (username, email, mobile)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    return user['id'] if user else None


def reset_password_by_user_id(user_id, new_password):
    """Hashes and saves a new password for the given user_id."""
    hashed_password = generate_password_hash(new_password)
    return change_user_password(user_id, hashed_password)