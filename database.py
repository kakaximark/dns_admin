
import mysql.connector
from config import DATABASE_CONFIG

def db():
    connection = mysql.connector.connect(**DATABASE_CONFIG)
    return connection

def save_user(username, password_hash):
    connection = db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO sys_api_user (username, password_hash) VALUES (%s, %s)", (username, password_hash))
    connection.commit()
    connection.close()

def get_user_by_username(username):
    connection = db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sys_api_user WHERE username = %s", (username,))
    user = cursor.fetchone()
    connection.close()
    return user
