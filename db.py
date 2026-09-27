import mysql.connector
from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT
)
def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

    return connection


def save_lead_to_db(name, email, phone, ai_score, status="New"):
    """Insert a scored lead or update its score and status by email."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO leads (name, email, phone, ai_score, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            ai_score = VALUES(ai_score),
            status = VALUES(status)
        """
        values = (name, email, phone, ai_score, status)

        cursor.execute(query, values)
        connection.commit()

        print(f"[SUCCESS] Lead '{name}' saved to MySQL database.")
        return True
    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection failed: {err}")
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()