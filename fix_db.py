from sqlalchemy import text
from app.core.database import engine

def fix_database():
    print("🔧 Connecting to database to add 'tracked_stocks' column...")
    with engine.connect() as conn:
        try:
            # Forcefully add the missing column to Postgres
            conn.execute(text("ALTER TABLE users ADD COLUMN tracked_stocks JSON DEFAULT '[]'::json;"))
            conn.commit()
            print("✅ SUCCESS: 'tracked_stocks' column added to users table!")
        except Exception as e:
            print(f"⚠️ Note: {e}")

if __name__ == "__main__":
    fix_database()