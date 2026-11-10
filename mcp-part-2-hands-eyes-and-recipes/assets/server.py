"""
Model Context Protocol (MCP) Explained - Part 2 Reference Server
Demonstrating the Core MCP Triad: Tools (Hands), Resources (Eyes), and Prompts (Recipes).

Run with:
    uv run server.py
Or inspect with MCP Inspector:
    npx @modelcontextprotocol/inspector uv run server.py
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("TaskMaster-Part2", dependencies=["mcp[cli]"])

# In-Memory Task Database
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Migrate auth service to OAuth2 / OIDC",
        "description": "Deprecate legacy session tokens in favor of short-lived JWTs.",
        "status": "in-progress",
        "priority": "high",
        "created_at": "2026-11-01T10:00:00Z",
    },
    {
        "id": 2,
        "title": "Implement Redis read-replica connection pool",
        "description": "Offload cache read spikes from primary Redis node during peak traffic.",
        "status": "completed",
        "priority": "high",
        "created_at": "2026-11-01T14:30:00Z",
    },
    {
        "id": 3,
        "title": "Configure OpenTelemetry trace exporter for gRPC gateway",
        "description": "Propagate traceparent headers across external microservice boundaries.",
        "status": "pending",
        "priority": "medium",
        "created_at": "2026-11-02T09:15:00Z",
    },
]
next_id = 4


# ==============================================================================
# 1. RESOURCES (Eyes / Nouns / Read-Only Context)
# ==============================================================================

@mcp.resource("tasks://all", mime_type="application/json")
def get_all_tasks() -> str:
    """Read-only resource exposing the entire active task ledger."""
    return json.dumps(tasks_db, indent=2)


@mcp.resource("tasks://status/{status}", mime_type="application/json")
def get_tasks_by_status(status: str) -> str:
    """Dynamic URI template resource filtering tasks by status ('pending', 'in-progress', 'completed')."""
    normalized = status.lower().strip()
    filtered = [t for t in tasks_db if t["status"].lower() == normalized]
    return json.dumps(filtered, indent=2)


@mcp.resource("tasks://stats", mime_type="application/json")
def get_task_statistics() -> str:
    """Read-only aggregate metrics for current backlog health."""
    total = len(tasks_db)
    completed = sum(1 for t in tasks_db if t["status"] == "completed")
    in_progress = sum(1 for t in tasks_db if t["status"] == "in-progress")
    pending = sum(1 for t in tasks_db if t["status"] == "pending")
    rate = round((completed / total * 100), 1) if total > 0 else 0.0

    stats = {
        "total_tasks": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "completion_rate_percent": rate,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(stats, indent=2)


# ==============================================================================
# 2. TOOLS (Hands / Verbs / Executable Mutations)
# ==============================================================================

@mcp.tool()
def add_task(title: str, description: str = "", priority: str = "medium") -> str:
    """Add a new engineering task to the system backlog.
    
    Args:
        title: Concise title of the task
        description: Technical details, acceptance criteria, or context
        priority: Urgency level ('low', 'medium', 'high', 'critical')
    """
    global next_id
    if not title.strip():
        return "Error: Task title cannot be empty."

    valid_priorities = {"low", "medium", "high", "critical"}
    prio = priority.lower().strip()
    if prio not in valid_priorities:
        prio = "medium"

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "description": description.strip(),
        "status": "pending",
        "priority": prio,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    tasks_db.append(new_task)
    assigned_id = next_id
    next_id += 1

    return f"Task #{assigned_id} successfully created: '{new_task['title']}' [priority: {prio}]."


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Mark an existing task as completed.
    
    Args:
        task_id: Numeric unique identifier of the task
    """
    for task in tasks_db:
        if task["id"] == task_id:
            if task["status"] == "completed":
                return f"Task #{task_id} ('{task['title']}') was already completed."
            task["status"] = "completed"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            return f"Success: Task #{task_id} ('{task['title']}') is now marked completed."
    return f"Error: Task with ID #{task_id} not found."


@mcp.tool()
def delete_task(task_id: int) -> str:
    """Permanently delete a task from the system backlog.
    
    Args:
        task_id: Numeric unique identifier of the task to delete
    """
    global tasks_db
    initial_len = len(tasks_db)
    tasks_db = [t for t in tasks_db if t["id"] != task_id]
    if len(tasks_db) < initial_len:
        return f"Task #{task_id} deleted successfully."
    return f"Error: Task with ID #{task_id} not found."


# ==============================================================================
# 3. PROMPTS (Recipes / Workflows / User & Agent Playbooks)
# ==============================================================================

@mcp.prompt("daily_standup")
def daily_standup_prompt(team_name: str = "Core Infrastructure") -> str:
    """Construct an automated engineering daily standup summary workflow."""
    current_context = json.dumps(tasks_db, indent=2)
    return f"""You are the Staff Technical Lead for the '{team_name}' engineering squad.
Analyze the following active task ledger from our MCP task server:

{current_context}

Please generate a high-signal, executive-ready Daily Standup Report formatted as follows:
1. 🏁 Completed Items (What was shipped and validated)
2. ⚡ In-Flight Focus (What is actively under development today)
3. 🚧 Roadblocks & Dependencies (Pending items requiring architectural unblocking or cross-team alignment)
4. 📊 Backlog Velocity Assessment (One sentence on current momentum)

Keep explanations technical, concise, and focused on systemic throughput."""


@mcp.prompt("task_prioritization_audit")
def task_audit_prompt() -> str:
    """Interactive recipe to audit task prioritization using an Eisenhower matrix."""
    current_context = json.dumps(tasks_db, indent=2)
    return f"""Audit the following engineering task backlog using the Eisenhower Matrix (Urgent vs Important):

{current_context}

For each task:
- Evaluate whether its stated priority matches technical dependencies.
- Flag any architectural risks where critical infrastructure tasks are languishing in 'pending'.
- Recommend the immediate next 2 tasks the engineering lead should pull into active sprint development."""


if __name__ == "__main__":
    # Launch stdio transport server
    mcp.run()
