import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432',
            dbname='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'smart_focus'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute('CREATE DATABASE smart_focus')
            print("Database 'smart_focus' created successfully.")
        else:
            print("Database 'smart_focus' already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
