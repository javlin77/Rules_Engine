"""
Script to fix/update database schema
Drops and recreates tables to match current models
"""
import sys
from sqlalchemy import text
from database import engine, SessionLocal
from models import Base, Rule, RuleVersion, AuditLog

def drop_all_tables():
    """Drop all existing tables"""
    print("Dropping existing tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("[OK] All tables dropped successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Error dropping tables: {e}")
        return False

def create_all_tables():
    """Create all tables from current models"""
    print("Creating tables from current models...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] All tables created successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False

def check_schema():
    """Check if version column exists"""
    print("Checking current schema...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'rules'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            print("\nCurrent 'rules' table columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            column_names = [col[0] for col in columns]
            
            if 'version' not in column_names:
                print("\n[!] Missing 'version' column - schema needs update")
                return False
            else:
                print("\n[OK] Schema looks correct!")
                return True
    except Exception as e:
        print(f"[ERROR] Error checking schema: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Database Schema Fix Script")
    print("=" * 50)
    print()
    
    # Check current schema
    schema_ok = check_schema()
    
    if not schema_ok:
        print("\n" + "=" * 50)
        response = input("Schema needs fixing. Drop and recreate all tables? (y/n): ").strip().lower()
        
        if response == 'y':
            print()
            if drop_all_tables():
                if create_all_tables():
                    print("\n" + "=" * 50)
                    print("[OK] Schema fixed successfully!")
                    print("=" * 50)
                    print("\nNext steps:")
                    print("1. Run: python init_db.py --seed")
                    sys.exit(0)
                else:
                    print("\n[ERROR] Failed to create tables!")
                    sys.exit(1)
            else:
                print("\n[ERROR] Failed to drop tables!")
                sys.exit(1)
        else:
            print("Aborted.")
            sys.exit(0)
    else:
        print("\n[OK] Schema is already correct!")
        sys.exit(0)

