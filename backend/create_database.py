"""
Script to create the rules_engine database
This uses psycopg2 to connect and create the database
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

def create_database():
    """Create the rules_engine database"""
    
    # Get connection parameters (connect to default 'postgres' database first)
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "rules_engine")
    
    print("=" * 50)
    print("Creating Rules Engine Database")
    print("=" * 50)
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    print(f"Database: {db_name}")
    print()
    
    try:
        # Connect to PostgreSQL server (using default 'postgres' database)
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"[!] Database '{db_name}' already exists!")
            response = input("Do you want to continue anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Aborted.")
                return False
        else:
            # Create the database
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"[OK] Database '{db_name}' created successfully!")
        
        cursor.close()
        conn.close()
        
        # Test connection to the new database
        print(f"\nTesting connection to '{db_name}'...")
        test_conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        test_conn.close()
        print("[OK] Connection test successful!")
        
        print("\n" + "=" * 50)
        print("[OK] Database setup complete!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Run: python init_db.py --seed")
        print("2. Start the server: python main.py")
        
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"\n[ERROR] Connection failed: {error_msg}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print(f"2. Verify credentials in .env file (DB_USER, DB_PASSWORD)")
        print(f"3. Check if PostgreSQL is listening on port {db_port}")
        if "password authentication failed" in error_msg.lower():
            print("\n   -> Password authentication failed!")
            print("   -> Check your DB_PASSWORD in backend/.env file")
            print("   -> Or set it as an environment variable")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)

