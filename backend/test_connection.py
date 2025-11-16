"""
Test database and Kafka connections
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from kafka_client import get_kafka_producer

load_dotenv()

def test_database():
    """Test PostgreSQL connection"""
    print("Testing PostgreSQL connection...")
    
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "rules_engine")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"  Connecting to: {db_host}:{db_port}/{db_name}")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"  ✅ Connected successfully!")
            print(f"  PostgreSQL version: {version.split(',')[0]}")
            
            # Test if database exists and has tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            if tables:
                print(f"  Found {len(tables)} tables: {', '.join(tables)}")
            else:
                print("  ⚠️  No tables found. Run 'python init_db.py' to create them.")
            
        return True
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print(f"  Make sure PostgreSQL is running on {db_host}:{db_port}")
        return False

def test_kafka():
    """Test Kafka connection"""
    print("\nTesting Kafka connection...")
    
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    print(f"  Connecting to: {bootstrap_servers}")
    
    try:
        producer = get_kafka_producer()
        if producer and producer.producer:
            print("  ✅ Kafka producer connected successfully!")
            return True
        else:
            print("  ⚠️  Kafka not available (this is optional)")
            print("  The system will work without Kafka for sync evaluation")
            return False
    except Exception as e:
        print(f"  ⚠️  Kafka connection failed: {e}")
        print("  This is optional - the system works without Kafka")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Rules Engine Connection Test")
    print("=" * 50)
    print()
    
    db_ok = test_database()
    kafka_ok = test_kafka()
    
    print("\n" + "=" * 50)
    if db_ok:
        print("✅ Database: OK")
    else:
        print("❌ Database: FAILED - Please check your PostgreSQL setup")
    
    if kafka_ok:
        print("✅ Kafka: OK")
    else:
        print("⚠️  Kafka: Not available (optional)")
    
    print("=" * 50)
    
    if db_ok:
        print("\n✅ System is ready to use!")
    else:
        print("\n❌ Please fix database connection before proceeding")

