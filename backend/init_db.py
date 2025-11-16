"""
Database initialization script
Creates tables and optionally seeds with sample data
"""
import sys
from sqlalchemy import text, inspect
from database import engine, SessionLocal
from models import Base, Rule, RuleVersion, AuditLog
from datetime import datetime

def check_schema_compatibility():
    """Check if existing tables match the current model schema"""
    inspector = inspect(engine)
    
    if 'rules' not in inspector.get_table_names():
        return True  # Tables don't exist, will be created
    
    # Check if rules table has required columns
    rules_columns = [col['name'] for col in inspector.get_columns('rules')]
    required_columns = ['id', 'name', 'priority', 'active', 'version', 'conditions', 'actions']
    
    missing = [col for col in required_columns if col not in rules_columns]
    
    if missing:
        print(f"[!] Schema mismatch detected!")
        print(f"    Missing columns in 'rules' table: {', '.join(missing)}")
        print(f"\n    This usually happens when tables were created before model updates.")
        print(f"    Solution: Run 'python fix_schema.py' to update the schema")
        return False
    
    return True

def init_database():
    """Create all tables"""
    print("Checking database schema...")
    
    # Check if schema is compatible
    if not check_schema_compatibility():
        return False
    
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables created successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify your .env file has correct DB_USER, DB_PASSWORD, DB_HOST, DB_PORT")
        print("3. Make sure the database 'rules_engine' exists (run create_database.py first)")
        print("4. Check that your password doesn't have unescaped special characters")
        print("5. If schema is outdated, run: python fix_schema.py")
        return False

def seed_sample_data():
    """Seed database with sample rules"""
    db = SessionLocal()
    try:
        # Check if rules already exist
        existing = db.query(Rule).count()
        if existing > 0:
            print(f"Database already has {existing} rules. Skipping seed.")
            return
        
        print("Seeding sample data...")
        
        # Sample rule 1: Premium user discount
        rule1 = Rule(
            id="premium_discount_10pct",
            name="10% off for premium users",
            priority=100,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "context.user.tier", "op": "==", "value": "premium"},
                    {"field": "event.cart.total", "op": ">=", "value": 1000}
                ]
            },
            actions=[
                {"type": "apply_discount", "payload": {"percent": 10}},
                {"type": "log", "payload": {"tag": "promo_applied"}}
            ],
            tags=["discount", "promo"],
            stop_on_match=False,
            created_by="system",
            description="Apply 10% discount for premium users on purchases over $1000"
        )
        db.add(rule1)
        
        # Sample rule 2: High value withdrawal approval
        rule2 = Rule(
            id="high_value_withdrawal_approval",
            name="High value withdrawal approval",
            priority=900,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "event.type", "op": "==", "value": "withdrawal"},
                    {"field": "event.amount", "op": ">", "value": 50000},
                    {"field": "context.user.account_status", "op": "!=", "value": "frozen"}
                ]
            },
            actions=[
                {"type": "escalate_for_approval", "payload": {"level": "manager"}}
            ],
            tags=["approval", "compliance"],
            stop_on_match=True,
            created_by="system",
            description="Require manager approval for withdrawals over $50,000"
        )
        db.add(rule2)
        
        # Sample rule 3: New user welcome
        rule3 = Rule(
            id="new_user_welcome",
            name="New user welcome discount",
            priority=50,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "event.type", "op": "==", "value": "first_purchase"},
                    {
                        "fn": "days_since",
                        "args": ["context.user.signup_date"],
                        "op": "<=",
                        "value": 7
                    }
                ]
            },
            actions=[
                {"type": "apply_discount", "payload": {"percent": 15}},
                {"type": "send_email", "payload": {"template": "welcome"}}
            ],
            tags=["welcome", "discount"],
            stop_on_match=False,
            created_by="system",
            description="15% discount for new users within 7 days of signup"
        )
        db.add(rule3)
        
        # Create initial versions
        for rule in [rule1, rule2, rule3]:
            version = RuleVersion(
                id=f"{rule.id}_v1",
                rule_id=rule.id,
                version=1,
                conditions=rule.conditions,
                actions=rule.actions,
                created_by="system"
            )
            db.add(version)
        
        db.commit()
        print("[OK] Sample data seeded successfully!")
        print(f"   - Created {db.query(Rule).count()} rules")
        
    except Exception as e:
        print(f"[ERROR] Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Rules Engine Database Initialization")
    print("=" * 50)
    
    success = init_database()
    if success:
        if len(sys.argv) > 1 and sys.argv[1] == "--seed":
            try:
                seed_sample_data()
            except Exception as e:
                error_msg = str(e)
                if "version" in error_msg.lower() and "does not exist" in error_msg.lower():
                    print("\n" + "=" * 50)
                    print("[ERROR] Schema mismatch detected!")
                    print("=" * 50)
                    print("\nThe database tables are missing the 'version' column.")
                    print("This happens when tables were created before the model was updated.")
                    print("\nTo fix this, run:")
                    print("  python fix_schema.py")
                    print("\nThis will update your schema to match the current models.")
                    sys.exit(1)
                else:
                    raise
        else:
            print("\nTip: Run with --seed to add sample rules")
            print("   python init_db.py --seed")
        print("\n[OK] Database initialization complete!")
    else:
        print("\n[ERROR] Database initialization failed!")
        print("Please fix the errors above and try again.")
        sys.exit(1)

