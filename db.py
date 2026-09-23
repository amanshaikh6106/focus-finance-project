import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "Aman",
    "password": "Aman@6106",
    "database": "focusfinance6106"
}


def get_db_connection():
    """
    Creates and returns a new MySQL database connection.
    Returns None if the connection fails (and prints the error to the console).
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        return None