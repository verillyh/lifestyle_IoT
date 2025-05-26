import mysql.connector

def initialize_db(cursor, db):
    cursor.execute("CREATE DATABASE IF NOT EXISTS smartlock")
    cursor.execute("USE smartlock")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lock_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            uid VARCHAR(255) NOT NULL,
            status VARCHAR(255) NOT NULL           
        )
    """)
    db.commit()

def connect(host, user, password):
    db = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
    )
    cursor = db.cursor(dictionary=True)
    initialize_db(cursor, db)

    return db, cursor