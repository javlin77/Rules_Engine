"""
Enhanced condition evaluator with support for multiple operators and functions
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

def get_nested_value(obj: Dict, path: str) -> Any:
    """Get nested value from object using dot notation (e.g., 'user.tier')"""
    parts = path.split(".")
    cur = obj
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        elif isinstance(cur, list) and p.isdigit() and int(p) < len(cur):
            cur = cur[int(p)]
        else:
            return None
    return cur

def days_since(date_str: str) -> Optional[int]:
    """Calculate days since a given date string (ISO format)"""
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            delta = datetime.utcnow() - dt.replace(tzinfo=None)
            return delta.days
    except:
        pass
    return None

def eval_condition(condition: Dict, event: Dict, context: Dict, explanation: Optional[List] = None) -> Tuple[bool, List]:
    """
    Evaluate a condition AST against event and context.
    Returns (result, explanation_list)
    """
    if explanation is None:
        explanation = []
    
    if not condition:
        return True, explanation
    
    # Handle logical operators (AND, OR, NOT)
    if "type" in condition and condition["type"] in ["AND", "OR", "NOT"]:
        typ = condition["type"]
        clauses = condition.get("clauses", [])
        
        if typ == "NOT":
            if len(clauses) != 1:
                explanation.append({"error": "NOT operator requires exactly one clause"})
                return False, explanation
            result, sub_expl = eval_condition(clauses[0], event, context, [])
            explanation.extend(sub_expl)
            return not result, explanation
        
        results = []
        for clause in clauses:
            result, sub_expl = eval_condition(clause, event, context, [])
            results.append(result)
            explanation.extend(sub_expl)
        
        if typ == "AND":
            final = all(results)
            explanation.append({"operator": "AND", "results": results, "final": final})
            return final, explanation
        else:  # OR
            final = any(results)
            explanation.append({"operator": "OR", "results": results, "final": final})
            return final, explanation
    
    # Handle function calls
    if "fn" in condition:
        fn_name = condition["fn"]
        args = condition.get("args", [])
        
        if fn_name == "days_since":
            if len(args) != 1:
                explanation.append({"error": "days_since requires one argument"})
                return False, explanation
            field_path = args[0]
            date_val = get_nested_value({"event": event, "context": context}, field_path)
            days = days_since(date_val) if date_val else None
            if days is None:
                explanation.append({"function": "days_since", "field": field_path, "result": None, "error": "Invalid date"})
                return False, explanation
            # Compare with value if provided
            if "op" in condition and "value" in condition:
                op = condition["op"]
                val = condition["value"]
                result = _compare_values(days, op, val)
                explanation.append({"function": "days_since", "field": field_path, "days": days, "op": op, "value": val, "result": result})
                return result, explanation
            explanation.append({"function": "days_since", "field": field_path, "days": days})
            return True, explanation
        
        explanation.append({"error": f"Unknown function: {fn_name}"})
        return False, explanation
    
    # Handle field comparisons
    if "field" in condition and "op" in condition:
        field = condition["field"]
        op = condition["op"]
        val = condition.get("value")
        
        # Merge event and context
        merged = {"event": event, "context": context}
        actual = get_nested_value(merged, field)
        
        result = _compare_values(actual, op, val)
        
        explanation.append({
            "field": field,
            "operator": op,
            "expected": val,
            "actual": actual,
            "result": result
        })
        
        return result, explanation
    
    explanation.append({"error": "Invalid condition structure"})
    return False, explanation

def _compare_values(actual: Any, op: str, expected: Any) -> bool:
    """Compare actual value with expected using operator"""
    if actual is None:
        return False
    
    try:
        if op == "==":
            return actual == expected
        elif op == "!=":
            return actual != expected
        elif op == ">":
            return actual > expected
        elif op == "<":
            return actual < expected
        elif op == ">=":
            return actual >= expected
        elif op == "<=":
            return actual <= expected
        elif op == "in":
            if isinstance(expected, list):
                return actual in expected
            return False
        elif op == "not_in":
            if isinstance(expected, list):
                return actual not in expected
            return True
        elif op == "contains":
            if isinstance(actual, str) and isinstance(expected, str):
                return expected in actual
            elif isinstance(actual, list):
                return expected in actual
            return False
        elif op == "regex":
            if isinstance(actual, str) and isinstance(expected, str):
                return bool(re.search(expected, actual))
            return False
        elif op == "starts_with":
            if isinstance(actual, str) and isinstance(expected, str):
                return actual.startswith(expected)
            return False
        elif op == "ends_with":
            if isinstance(actual, str) and isinstance(expected, str):
                return actual.endswith(expected)
            return False
        else:
            return False
    except (TypeError, ValueError):
        return False

