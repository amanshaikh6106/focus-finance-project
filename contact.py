

from db import get_db_connection


def save_contact_message(data, user_id=None):
    """
    Inserts a contact form submission into the "contact" table.

    Parameters
    ----------
    data : dict
        Dictionary containing the contact form fields
        (name, email, subject, message).
    user_id : int, optional
        The ID of the logged-in user submitting the message.

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
            INSERT INTO contact (user_id, name, email, subject, message)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            user_id,
            data['name'],
            data['email'],
            data['subject'],
            data['message']
        )
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not save contact message: {e}")
        return False