import psycopg2

DB_CONFIG = {
    "dbname": "email",  # ✅ Make sure this is correct
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Connection successful!")
    conn.close()
except psycopg2.OperationalError as e:
    print("❌ Database connection failed!")
    print(e)
