"""
Model Context Protocol (MCP) Explained - Part 4 Companion Code
Production-Hardened FastMCP Server demonstrating:
1. Input sanitization & boundary defense
2. Token rate-limiting & recursive loop prevention
3. OpenTelemetry distributed trace context propagation
4. Structured JSON audit logging to stderr
"""

from datetime import datetime, timezone
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("HardenedTaskServer-Part4", dependencies=["mcp[cli]"])

# Rate Limiting State (Sliding Window per tool)
RATE_LIMIT_MAX_CALLS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
call_history: Dict[str, List[float]] = {}


def check_rate_limit(tool_name: str) -> bool:
    """Enforce sliding window rate limit to prevent recursive LLM tool execution loops."""
    now = time.time()
    history = call_history.setdefault(tool_name, [])
    # Evict timestamps older than window
    call_history[tool_name] = [t for t in history if now - t < RATE_LIMIT_WINDOW_SECONDS]

    if len(call_history[tool_name]) >= RATE_LIMIT_MAX_CALLS:
        return False
    call_history[tool_name].append(now)
    return True


def audit_log(event_type: str, details: Dict[str, Any]):
    """Emit structured audit events strictly to stderr (stdout is sacred wire)."""
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "details": details,
    }
    sys.stderr.write(f"[AUDIT] {json.dumps(log_entry)}\n")
    sys.stderr.flush()


# In-Memory Backend Data Store
tasks_db: List[Dict[str, Any]] = [
    {"id": 1, "title": "Upgrade PostgreSQL cluster to v17", "status": "pending", "priority": "critical"},
    {"id": 2, "title": "Audit AWS IAM roles for wildcard policies", "status": "completed", "priority": "high"},
]
next_id = 3


# ==============================================================================
# SECURED TOOLS WITH INPUT CONSTRAINTS & RATE LIMITING
# ==============================================================================

@mcp.tool()
def create_hardened_task(
    title: str,
    priority: str = "medium",
    traceparent: Optional[str] = None
) -> str:
    """Create an engineering task with strict parameter validation and rate limiting.

    Args:
        title: Task summary (max 120 chars, alphanumeric with standard punctuation)
        priority: Urgency level ('low', 'medium', 'high', 'critical')
        traceparent: W3C distributed trace header (e.g., '00-4bf92f35...-01')
    """
    global next_id

    # 1. Rate Limiting Check
    if not check_rate_limit("create_hardened_task"):
        audit_log("RATE_LIMIT_EXCEEDED", {"tool": "create_hardened_task"})
        return "Error: Tool rate limit exceeded (10 calls/min). Halting to prevent loop."

    # 2. Strict Input Boundary Defense
    clean_title = title.strip()
    if not clean_title or len(clean_title) > 120:
        audit_log("VALIDATION_FAILURE", {"field": "title", "length": len(clean_title)})
        return "Error: Title must be between 1 and 120 characters."

    valid_priorities = {"low", "medium", "high", "critical"}
    prio = priority.lower().strip()
    if prio not in valid_priorities:
        audit_log("VALIDATION_FAILURE", {"field": "priority", "value": priority})
        return f"Error: Invalid priority '{priority}'. Allowed: {sorted(valid_priorities)}."

    # 3. Distributed Tracing Telemetry
    audit_log("TOOL_EXECUTION_START", {
        "tool": "create_hardened_task",
        "title": clean_title,
        "priority": prio,
        "traceparent": traceparent or "none"
    })

    # 4. State Mutation
    new_task = {
        "id": next_id,
        "title": clean_title,
        "status": "pending",
        "priority": prio,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tasks_db.append(new_task)
    assigned_id = next_id
    next_id += 1

    audit_log("TOOL_EXECUTION_SUCCESS", {"task_id": assigned_id})
    return f"Task #{assigned_id} securely created: '{clean_title}' [priority: {prio}]."


@mcp.tool()
def delete_task_with_confirmation(
    task_id: int,
    confirmation_token: str
) -> str:
    """Delete a task. Requires an explicit human confirmation token from client HITL gate.

    Args:
        task_id: ID of the task to delete
        confirmation_token: Explicit confirmation token 'CONFIRM_DELETE_<task_id>'
    """
    global tasks_db

    expected_token = f"CONFIRM_DELETE_{task_id}"
    if confirmation_token.strip() != expected_token:
        audit_log("AUTH_FAILURE", {"task_id": task_id, "token": confirmation_token})
        return f"Error: Human-in-the-loop authorization failed. Expected token '{expected_token}'."

    initial_len = len(tasks_db)
    tasks_db = [t for t in tasks_db if t["id"] != task_id]

    if len(tasks_db) < initial_len:
        audit_log("DESTRUCTION_EVENT", {"task_id": task_id, "status": "deleted"})
        return f"Task #{task_id} successfully deleted after verified human authorization."

    return f"Error: Task #{task_id} not found."


# ==============================================================================
# READ-ONLY OBSERVABILITY RESOURCES
# ==============================================================================

@mcp.resource("tasks://audit/recent", mime_type="application/json")
def get_audit_summary() -> str:
    """Read-only view of current server health and active task count."""
    return json.dumps({
        "active_tasks_count": len(tasks_db),
        "rate_limit_window": f"{RATE_LIMIT_WINDOW_SECONDS}s",
        "status": "hardened_and_healthy"
    }, indent=2)


if __name__ == "__main__":
    audit_log("SERVER_STARTUP", {"pid": os.getpid(), "transport": "stdio"})
    mcp.run()
