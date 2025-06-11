from db import connect_db

try:
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")

    for table in cursor.fetchall():
        print("جدول موجود:", table)

    db.close()

except Exception as e:
    print("خطا:", e)
