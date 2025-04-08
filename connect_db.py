import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="your_password",
    host="localhost",
    port="5432"
)

print("✅ Connected to PostgreSQL!")
conn.close()
