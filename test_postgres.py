import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            database=os.getenv("POSTGRES_DB", "smart_focus"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        print("✅ Successfully connected to PostgreSQL!")
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")

if __name__ == "__main__":
    test_connection()
