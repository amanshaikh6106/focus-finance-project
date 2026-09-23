import mysql.connector
from mysql.connector import Error
import os
from urllib.parse import urlparse, unquote


def get_db_connection():
    try:
        db_url = os.getenv("MYSQL_PRIVATE_URL")

        if not db_url:
            print("[DB ERROR] MYSQL_PRIVATE_URL is not set")
            return None

        parsed = urlparse(db_url)

        connection = mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username),
            password=unquote(parsed.password),
            database=parsed.path.lstrip("/")
        )

        return connection

    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        return None