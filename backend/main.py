from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uuid
import time
from datetime import datetime
import json
import logging

from database import SessionLocal, engine
from models import Base, Rule, RuleVersion, AuditLog
from schemas import (
    RuleCreate, RuleUpdate, SimulateRequest, EvaluateRequest,
    EvaluationResponse, RuleResponse
)
from evaluator import eval_condition
from kafka_client import get_kafka_producer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rules Engine API",
    description="Production-ready Rules Engine with versioning, audit logs, and Kafka integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to normalize id
def make_id(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")[:48]

def create_audit_log(
    db: Session,
    event: dict,
    context: dict,
    matched_rules: list,
    actions: list,
    explanation: list,
    evaluation_time_ms: int,
    event_id: str = None
) -> str:
    """Create audit log entry"""
    audit_id = str(uuid.uuid4())
    audit = AuditLog(
        id=audit_id,
        event_id=event_id or str(uuid.uuid4()),
        event_type=event.get("type"),
        event_data=event,
        context_data=context,
        matched_rules=matched_rules,
        actions_taken=actions,
        explanation=explanation,
        evaluation_time_ms=evaluation_time_ms
    )
    db.add(audit)
    db.commit()
    return audit_id

# ========== RULE CRUD ENDPOINTS ==========

@app.get("/rules", response_model=List[RuleResponse])
def list_rules(
    active: bool = None,
    tag: str = None,
    db: Session = Depends(get_db)
):
    """List all rules with optional filtering"""
    query = db.query(Rule)
    
    if active is not None:
        query = query.filter(Rule.active == active)
    
    if tag:
        # Filter by tag (JSON array contains)
        query = query.filter(Rule.tags.contains([tag]))
    
    rules = query.order_by(Rule.priority.desc(), Rule.created_at.desc()).all()
    
    return [
        RuleResponse(
            id=r.id,
            name=r.name,
            priority=r.priority,
            active=r.active,
            version=r.version,
            conditions=r.conditions,
            actions=r.actions,
            tags=r.tags or [],
            stop_on_match=r.stop_on_match,
            created_by=r.created_by,
            created_at=r.created_at,
            updated_at=r.updated_at,
            description=r.description
        )
        for r in rules
    ]

@app.get("/rules/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)):
    """Get a specific rule by ID"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return RuleResponse(
        id=rule.id,
        name=rule.name,
        priority=rule.priority,
        active=rule.active,
        version=rule.version,
        conditions=rule.conditions,
        actions=rule.actions,
        tags=rule.tags or [],
        stop_on_match=rule.stop_on_match,
        created_by=rule.created_by,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        description=rule.description
    )

@app.post("/rules", response_model=dict)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    """Create a new rule"""
    rid = make_id(payload.name)
    existing = db.query(Rule).filter(Rule.id == rid).first()
    if existing:
        rid = f"{rid}_{uuid.uuid4().hex[:6]}"
    
    rule = Rule(
        id=rid,
        name=payload.name,
        priority=payload.priority,
        active=True,
        version=1,
        conditions=payload.conditions,
        actions=payload.actions,
        tags=payload.tags or [],
        stop_on_match=payload.stop_on_match,
        created_by=payload.created_by or "system",
        description=payload.description
    )
    
    db.add(rule)
    
    # Create initial version
    version = RuleVersion(
        id=str(uuid.uuid4()),
        rule_id=rid,
        version=1,
        conditions=payload.conditions,
        actions=payload.actions,
        created_by=payload.created_by or "system"
    )
    db.add(version)
    db.commit()
    
    return {
        "id": rule.id,
        "name": rule.name,
        "version": rule.version,
        "created_at": rule.created_at.isoformat()
    }

@app.put("/rules/{rule_id}", response_model=dict)
def update_rule(rule_id: str, payload: RuleUpdate, db: Session = Depends(get_db)):
    """Update a rule (creates new version)"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields if provided
    if payload.name is not None:
        rule.name = payload.name
    if payload.priority is not None:
        rule.priority = payload.priority
    if payload.conditions is not None:
        rule.conditions = payload.conditions
    if payload.actions is not None:
        rule.actions = payload.actions
    if payload.tags is not None:
        rule.tags = payload.tags
    if payload.active is not None:
        rule.active = payload.active
    if payload.stop_on_match is not None:
        rule.stop_on_match = payload.stop_on_match
    if payload.description is not None:
        rule.description = payload.description
    
    # Create new version if conditions or actions changed
    if payload.conditions is not None or payload.actions is not None:
        rule.version += 1
        version = RuleVersion(
            id=str(uuid.uuid4()),
            rule_id=rule_id,
            version=rule.version,
            conditions=rule.conditions,
            actions=rule.actions,
            created_by="system"
        )
        db.add(version)
    
    rule.updated_at = datetime.utcnow()
    db.commit()
    
    return {"id": rule.id, "version": rule.version, "updated_at": rule.updated_at.isoformat()}

@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"deleted": True}

# ========== EVALUATION ENDPOINTS ==========

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_all(req: EvaluateRequest, db: Session = Depends(get_db)):
    """
    Evaluate all active rules against an event.
    Returns matched rules, actions, and explanation.
    """
    start_time = time.time()
    
    # If async mode, send to Kafka and return immediately
    if req.async_mode:
        producer = get_kafka_producer()
        if producer:
            producer.send_event(req.event, req.context, req.event_id)
            return EvaluationResponse(
                actions=[],
                matched_rules=[],
                explanation=[{"message": "Event sent to Kafka for async processing"}],
                evaluation_time_ms=0
            )
        else:
            logger.warning("Kafka not available, falling back to sync evaluation")
    
    # Get active rules sorted by priority
    rules = db.query(Rule).filter(Rule.active == True).order_by(Rule.priority.desc()).all()
    
    matched_rules = []
    actions = []
    all_explanations = []
    
    for rule in rules:
        result, explanation = eval_condition(rule.conditions, req.event, req.context, [])
        
        if result:
            matched_rules.append(rule.id)
            actions.extend(rule.actions)
            all_explanations.append({
                "rule_id": rule.id,
                "rule_name": rule.name,
                "matched": True,
                "explanation": explanation
            })
            
            # Stop if rule says to stop on match
            if rule.stop_on_match:
                all_explanations.append({"message": f"Stopped at rule {rule.id} (stop_on_match=True)"})
                break
        else:
            # Log why rule didn't match (optional, can be verbose)
            pass
    
    evaluation_time_ms = int((time.time() - start_time) * 1000)
    
    # Create audit log
    audit_id = create_audit_log(
        db=db,
        event=req.event,
        context=req.context,
        matched_rules=matched_rules,
        actions=actions,
        explanation=all_explanations,
        evaluation_time_ms=evaluation_time_ms,
        event_id=req.event_id
    )
    
    return EvaluationResponse(
        actions=actions,
        matched_rules=matched_rules,
        explanation=all_explanations,
        evaluation_time_ms=evaluation_time_ms,
        audit_log_id=audit_id
    )

@app.post("/rules/{rule_id}/simulate")
def simulate_rule(rule_id: str, req: SimulateRequest, db: Session = Depends(get_db)):
    """Simulate a single rule against an event"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    result, explanation = eval_condition(rule.conditions, req.event, req.context, [])
    
    return {
        "matched": result,
        "rule_id": rule_id,
        "rule_name": rule.name,
        "would_execute": rule.actions if result else [],
        "explanation": explanation
    }

# ========== AUDIT & VERSIONING ENDPOINTS ==========

@app.get("/audit")
def get_audit_logs(
    event_id: str = None,
    rule_id: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering"""
    query = db.query(AuditLog)
    
    if event_id:
        query = query.filter(AuditLog.event_id == event_id)
    
    if rule_id:
        # Filter by rule_id in matched_rules JSON array
        query = query.filter(AuditLog.matched_rules.contains([rule_id]))
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "event_id": log.event_id,
            "event_type": log.event_type,
            "matched_rules": log.matched_rules,
            "actions_taken": log.actions_taken,
            "evaluation_time_ms": log.evaluation_time_ms,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]

@app.get("/rules/{rule_id}/versions")
def get_rule_versions(rule_id: str, db: Session = Depends(get_db)):
    """Get all versions of a rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    versions = db.query(RuleVersion).filter(RuleVersion.rule_id == rule_id).order_by(RuleVersion.version.desc()).all()
    
    return [
        {
            "id": v.id,
            "version": v.version,
            "conditions": v.conditions,
            "actions": v.actions,
            "created_at": v.created_at.isoformat(),
            "created_by": v.created_by
        }
        for v in versions
    ]

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "kafka_available": get_kafka_producer() is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
