from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, JSON, Boolean, DateTime, Text, ForeignKey
from datetime import datetime

Base = declarative_base()

class Rule(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    priority = Column(Integer, default=100)
    active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    tags = Column(JSON, default=[])
    stop_on_match = Column(Boolean, default=False)
    created_by = Column(String, default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text, nullable=True)

class RuleVersion(Base):
    __tablename__ = "rule_versions"
    id = Column(String, primary_key=True)
    rule_id = Column(String, ForeignKey("rules.id"), nullable=False)
    version = Column(Integer, nullable=False)
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, default="system")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True)
    event_id = Column(String, nullable=True)
    event_type = Column(String, nullable=True)
    event_data = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)
    matched_rules = Column(JSON, default=[])
    actions_taken = Column(JSON, default=[])
    explanation = Column(JSON, default=[])
    evaluation_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
