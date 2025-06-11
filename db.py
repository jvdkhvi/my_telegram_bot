import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",  # رمز MySQL تو اینجا بذار
        database="chatbot"
    )
