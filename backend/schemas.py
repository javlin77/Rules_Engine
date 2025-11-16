from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

class ActionSchema(BaseModel):
    type: str
    payload: Dict[str, Any] = {}

class RuleCreate(BaseModel):
    name: str
    priority: int = 100
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    tags: List[str] = []
    stop_on_match: bool = False
    description: Optional[str] = None
    created_by: Optional[str] = "system"

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    priority: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    active: Optional[bool] = None
    stop_on_match: Optional[bool] = None
    description: Optional[str] = None

class SimulateRequest(BaseModel):
    event: Dict[str, Any]
    context: Dict[str, Any] = {}
    event_id: Optional[str] = None

class EvaluateRequest(BaseModel):
    event: Dict[str, Any]
    context: Dict[str, Any] = {}
    event_id: Optional[str] = None
    async_mode: bool = False  # If True, send to Kafka instead of evaluating immediately

class EvaluationResponse(BaseModel):
    actions: List[Dict[str, Any]]
    matched_rules: List[str]
    explanation: List[Dict[str, Any]]
    evaluation_time_ms: Optional[int] = None
    audit_log_id: Optional[str] = None

class RuleResponse(BaseModel):
    id: str
    name: str
    priority: int
    active: bool
    version: int
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    tags: List[str]
    stop_on_match: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
