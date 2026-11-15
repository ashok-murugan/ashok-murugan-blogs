"""
Model Context Protocol (MCP) Explained - Part 6 Companion Code
Production-Hardened FastMCP Server demonstrating:
1. The Read-Back Verification Pattern (preventing false success signals)
2. Filesystem Atomicity via Write-to-Temp and Atomic Rename
3. Idempotency Key Semantics for Safe Agent Retries
4. Fail-Closed Error Taxonomy for Autonomous LLM Consumers
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("BattleHardenedServer-Part6", dependencies=["mcp[cli]"])


# ==============================================================================
# AUDIT LOGGING & TELEMETRY (STDERR ONLY)
# ==============================================================================

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


# ==============================================================================
# IN-MEMORY SIMULATED TRANSACTIONAL STORE
# ==============================================================================

tasks_db: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "title": "Upgrade PostgreSQL cluster to v17", "status": "PENDING", "idempotency_key": "seed-1"},
    2: {"id": 2, "title": "Audit AWS IAM roles for wildcard policies", "status": "COMPLETED", "idempotency_key": "seed-2"},
}
next_id = 3


# ==============================================================================
# INVARIANT 1 & 3: READ-BACK VERIFICATION + IDEMPOTENCY
# ==============================================================================

@mcp.tool()
def add_task_verified(
    title: str,
    idempotency_key: Optional[str] = None
) -> str:
    """Create a new task with strict read-back verification and idempotency support.

    Args:
        title: Task summary (max 120 chars)
        idempotency_key: Client-provided unique request token to prevent double-writes
    """
    global next_id, tasks_db

    clean_title = title.strip() if title else ""
    if not clean_title or len(clean_title) > 120:
        audit_log("VALIDATION_FAILURE", {"field": "title", "error": "Length must be between 1 and 120"})
        return "Error: Title must be between 1 and 120 characters."

    # Step 1: Idempotency Check (Prevent duplicate state mutation)
    if idempotency_key:
        clean_key = idempotency_key.strip()
        for existing in tasks_db.values():
            if existing.get("idempotency_key") == clean_key:
                audit_log("IDEMPOTENT_HIT", {"idempotency_key": clean_key, "task_id": existing["id"]})
                return f"Notice: Idempotent replay detected. Task #{existing['id']} already exists: '{existing['title']}'."

    # Step 2: Mutate Storage
    assigned_id = next_id
    next_id += 1
    tasks_db[assigned_id] = {
        "id": assigned_id,
        "title": clean_title,
        "status": "PENDING",
        "idempotency_key": idempotency_key.strip() if idempotency_key else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Step 3: READ-BACK VERIFY (The Ranucoli Invariant)
    # Never trust the write operation blindly; immediately re-query storage by ID
    verified_record = tasks_db.get(assigned_id)
    if not verified_record or verified_record["title"] != clean_title or verified_record["status"] != "PENDING":
        audit_log("WRITE_VERIFICATION_FAILURE", {"task_id": assigned_id})
        return f"CRITICAL_ERROR: Write verification failed for Task #{assigned_id}. Storage state unconfirmed."

    audit_log("TOOL_EXECUTION_SUCCESS", {"task_id": assigned_id, "verified": True})
    return f"Successfully created and verified Task #{assigned_id}: '{clean_title}' [status: PENDING]."


@mcp.tool()
def complete_task_verified(task_id: int) -> str:
    """Mark a task as completed with mandatory read-back state assertion.

    Args:
        task_id: Unique integer ID of the task
    """
    global tasks_db

    if task_id not in tasks_db:
        audit_log("NOT_FOUND", {"task_id": task_id})
        return f"Error: Task #{task_id} not found."

    # Step 1: Execute Mutation
    tasks_db[task_id]["status"] = "COMPLETED"
    tasks_db[task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Step 2: READ-BACK VERIFY
    # Re-fetch state directly from source of truth to confirm commit
    confirmed_state = tasks_db.get(task_id)
    if not confirmed_state or confirmed_state.get("status") != "COMPLETED":
        audit_log("MUTATION_VERIFICATION_FAILURE", {"task_id": task_id})
        return f"CRITICAL_ERROR: Mutation verification failed for Task #{task_id}. Status not committed."

    audit_log("TOOL_EXECUTION_SUCCESS", {"task_id": task_id, "status": "COMPLETED", "verified": True})
    return f"Successfully completed and verified Task #{task_id}: '{confirmed_state['title']}' [status: COMPLETED]."


# ==============================================================================
# INVARIANT 2: FILESYSTEM ATOMICITY (WRITE-TEMP-RENAME)
# ==============================================================================

@mcp.tool()
def write_file_atomic(
    file_path: str,
    content: str
) -> str:
    """Atomically write content to a file using temp-and-rename mechanics.
    Guarantees that a killed sidecar or process leaves either the old file or new file,
    never a truncated or half-written file.

    Args:
        file_path: Absolute or relative target destination path
        content: Full text content to commit
    """
    target = Path(file_path).resolve()

    # Prevent path traversal outside safe sandbox
    sandbox_root = Path.cwd().resolve()
    if not str(target).startswith(str(sandbox_root)):
        audit_log("SECURITY_VIOLATION", {"target": str(target), "reason": "Path traversal attempt"})
        return "Error: Permission denied. Path must be within project root."

    target.parent.mkdir(parents=True, exist_ok=True)

    # Step 1: Write to unique temp file in same directory (guarantees same filesystem)
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False, encoding="utf-8") as f:
            temp_file = Path(f.name)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Flush OS buffers to physical disk

        # Step 2: Atomic rename (Atomic on POSIX and modern Windows NTFS)
        os.replace(temp_file, target)

        # Step 3: READ-BACK VERIFY
        actual_bytes = target.stat().st_size
        expected_bytes = len(content.encode("utf-8"))
        if actual_bytes != expected_bytes:
            audit_log("SIZE_MISMATCH", {"target": str(target), "expected": expected_bytes, "actual": actual_bytes})
            return f"CRITICAL_ERROR: File size mismatch after write. Expected {expected_bytes} bytes, read {actual_bytes}."

        audit_log("ATOMIC_WRITE_SUCCESS", {"target": str(target), "bytes": actual_bytes})
        return f"Successfully and atomically wrote {actual_bytes} bytes to '{target.name}'."

    except Exception as e:
        if temp_file and temp_file.exists():
            temp_file.unlink(missing_ok=True)
        audit_log("WRITE_EXCEPTION", {"error": str(e)})
        return f"Error: Atomic write failed: {str(e)}"


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    audit_log("SERVER_STARTUP", {"pid": os.getpid(), "transport": "stdio"})
    mcp.run()
