import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def add_user(user_id, username):
    print(f"🔧 add_user called with: {user_id} - {username}")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("SQL_HOST"),
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASSWORD"),
            database=os.getenv("SQL_DB"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username))
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("خطا در ذخیره کاربر:", e)
