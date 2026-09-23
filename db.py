import mysql.connector
from mysql.connector import Error

import os

DB_CONFIG = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "user": os.getenv("MYSQLUSER", "Aman"),
    "password": os.getenv("MYSQLPASSWORD", "YOUR_LOCAL_MYSQL_PASSWORD"),
    "database": os.getenv("MYSQLDATABASE", "focusfinance6106"),
    "port": int(os.getenv("MYSQLPORT", "3306"))
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