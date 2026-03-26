import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE news_articles ADD COLUMN is_embedded BOOLEAN DEFAULT FALSE;")
    print("Column added successfully.")
    conn.close()
except Exception as e:
    print(f"Migration error: {e}")
