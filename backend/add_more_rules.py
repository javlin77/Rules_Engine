"""
Script to add more example rules to the database
Run this after init_db.py to add additional rules
"""
import sys
from database import SessionLocal
from models import Rule, RuleVersion
from datetime import datetime

def add_more_rules():
    """Add additional example rules"""
    db = SessionLocal()
    try:
        print("Adding more example rules...")
        
        # Rule 4: Low stock alert
        rule4 = Rule(
            id="low_stock_alert",
            name="Low stock alert",
            priority=200,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "event.type", "op": "==", "value": "inventory_check"},
                    {"field": "event.stock_level", "op": "<=", "value": 10}
                ]
            },
            actions=[
                {"type": "send_alert", "payload": {"channel": "email", "message": "Low stock detected"}},
                {"type": "notify_warehouse", "payload": {"action": "restock"}}
            ],
            tags=["inventory", "alert"],
            stop_on_match=False,
            created_by="system",
            description="Alert when inventory drops below 10 units"
        )
        db.add(rule4)
        
        # Rule 5: Fraud detection
        rule5 = Rule(
            id="fraud_detection_multiple_countries",
            name="Fraud detection - multiple countries",
            priority=1000,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "event.type", "op": "==", "value": "transaction"},
                    {"field": "context.user.transaction_countries", "op": "contains", "value": "US"},
                    {
                        "type": "OR",
                        "clauses": [
                            {"field": "event.amount", "op": ">", "value": 10000},
                            {"field": "context.user.suspicious_activity", "op": "==", "value": True}
                        ]
                    }
                ]
            },
            actions=[
                {"type": "block_transaction", "payload": {"reason": "fraud_suspected"}},
                {"type": "flag_account", "payload": {"level": "high"}},
                {"type": "notify_security", "payload": {"priority": "urgent"}}
            ],
            tags=["fraud", "security", "compliance"],
            stop_on_match=True,
            created_by="system",
            description="Block transactions with suspicious patterns"
        )
        db.add(rule5)
        
        # Rule 6: VIP customer special treatment
        rule6 = Rule(
            id="vip_customer_special",
            name="VIP customer special treatment",
            priority=150,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "context.user.tier", "op": "==", "value": "vip"},
                    {"field": "event.type", "op": "in", "value": ["purchase", "support_request", "refund"]}
                ]
            },
            actions=[
                {"type": "assign_vip_agent", "payload": {"team": "premium_support"}},
                {"type": "apply_priority", "payload": {"level": "high"}},
                {"type": "log", "payload": {"tag": "vip_customer"}}
            ],
            tags=["vip", "customer_service"],
            stop_on_match=False,
            created_by="system",
            description="Provide special treatment for VIP customers"
        )
        db.add(rule6)
        
        # Rule 7: Weekend promotion
        rule7 = Rule(
            id="weekend_promotion",
            name="Weekend promotion discount",
            priority=75,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {
                        "fn": "days_since",
                        "args": ["event.timestamp"],
                        "op": "<=",
                        "value": 0
                    },
                    {"field": "event.day_of_week", "op": "in", "value": ["Saturday", "Sunday"]},
                    {"field": "event.cart.total", "op": ">=", "value": 500}
                ]
            },
            actions=[
                {"type": "apply_discount", "payload": {"percent": 20, "code": "WEEKEND20"}},
                {"type": "send_notification", "payload": {"message": "Weekend special applied!"}}
            ],
            tags=["promotion", "weekend", "discount"],
            stop_on_match=False,
            created_by="system",
            description="20% discount on weekends for purchases over $500"
        )
        db.add(rule7)
        
        # Rule 8: Age-based restrictions
        rule8 = Rule(
            id="age_restriction_alcohol",
            name="Age restriction for alcohol products",
            priority=950,
            active=True,
            version=1,
            conditions={
                "type": "AND",
                "clauses": [
                    {"field": "event.product_category", "op": "==", "value": "alcohol"},
                    {"field": "context.user.age", "op": "<", "value": 21}
                ]
            },
            actions=[
                {"type": "block_purchase", "payload": {"reason": "age_restriction"}},
                {"type": "log", "payload": {"tag": "age_restriction_violation"}}
            ],
            tags=["compliance", "age_restriction", "alcohol"],
            stop_on_match=True,
            created_by="system",
            description="Block alcohol purchases for users under 21"
        )
        db.add(rule8)
        
        # Create versions for all new rules
        for rule in [rule4, rule5, rule6, rule7, rule8]:
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
        print(f"[OK] Added 5 new rules successfully!")
        print(f"   - Low stock alert")
        print(f"   - Fraud detection - multiple countries")
        print(f"   - VIP customer special treatment")
        print(f"   - Weekend promotion discount")
        print(f"   - Age restriction for alcohol products")
        print(f"\nTotal rules in database: {db.query(Rule).count()}")
        
    except Exception as e:
        print(f"[ERROR] Error adding rules: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Add More Rules to Database")
    print("=" * 50)
    print()
    add_more_rules()
    print("\n[OK] Done!")

