import mysql.connector
from mysql.connector import Error
import os


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=3306
        )

        return connection

    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        return None