import os
from dotenv import load_dotenv

load_dotenv()

results = []
results.append("Testing connections...")

# 1. Test Postgres
try:
    import psycopg2
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        conn.close()
        results.append("[OK] PostgreSQL connection successful!")
    else:
        results.append("[FAIL] PostgreSQL connection failed: DATABASE_URL not found in .env")
except Exception as e:
    results.append(f"[FAIL] PostgreSQL connection failed: {e}")

# 2. Test Redis
try:
    import redis
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        r = redis.from_url(redis_url)
        r.ping()
        results.append("[OK] Redis connection successful!")
    else:
        results.append("[FAIL] Redis connection failed: REDIS_URL not found in .env")
except Exception as e:
    results.append(f"[FAIL] Redis connection failed: {e}")

# 3. Test Pinecone
try:
    from pinecone import Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if api_key:
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        
        index_names = [idx.name for idx in indexes]
        if index_name in index_names:
            results.append(f"[OK] Pinecone connection successful! Index '{index_name}' found.")
        else:
            results.append(f"[WARN] Pinecone connection successful, but index '{index_name}' not found. Available: {index_names}")
    else:
        results.append("[FAIL] Pinecone connection failed: PINECONE_API_KEY not found in .env")
except Exception as e:
    results.append(f"[FAIL] Pinecone connection failed: {e}")

with open("test_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
