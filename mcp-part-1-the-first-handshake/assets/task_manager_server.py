# assets/task_manager_server.py
"""
Production Reference: Model Context Protocol (MCP) stdio Server Adapter.
Connects an AI Agent to a real Task REST API (http://localhost:8080/tasks).
Implements official Model Context Protocol specifications (https://modelcontextprotocol.io/).
"""

import os
import sys
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("TASK_API_BASE", "http://localhost:8080")

# 1. Initialize FastMCP Server
mcp = FastMCP(
    name="task-manager",
    instructions="Manage tasks in the corporate task manager. Supports listing, creating, and completing tasks."
)

# 2. Expose Real Tool: add_task
@mcp.tool()
async def add_task(title: str) -> str:
    """
    Create a new task in the task manager with PENDING status.

    Args:
        title: The descriptive title of the task to create.
    """
    # ⚠️ PROTOCOL RULE: Log exclusively to stderr to avoid stdout wire corruption!
    sys.stderr.write(f"[Server Log] Creating task: {title}\n")
    sys.stderr.flush()

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/tasks", json={"title": title}, timeout=5.0)
            resp.raise_for_status()
            task = resp.json()
            return f"Task #{task['id']} created: '{task['title']}' [status: {task['status']}]."
        except Exception as e:
            sys.stderr.write(f"[Server Error] Failed to call backend API: {e}\n")
            return f"Error: Unable to add task. Backend API unreachable: {e}"

# 3. Expose Real Tool: list_tasks
@mcp.tool()
async def list_tasks(status: Optional[str] = "ALL") -> str:
    """
    Retrieve tasks from the task manager.

    Args:
        status: Optional filter: ALL, PENDING, or COMPLETED.
    """
    sys.stderr.write(f"[Server Log] Querying tasks with filter: {status}\n")
    sys.stderr.flush()

    async with httpx.AsyncClient() as client:
        try:
            params = {} if not status or status == "ALL" else {"status": status.upper()}
            resp = await client.get(f"{API_BASE}/tasks", params=params, timeout=5.0)
            resp.raise_for_status()
            tasks = resp.json()

            if not tasks:
                return f"No tasks found matching filter: {status}."

            lines = [f"#{t['id']} [{t['status']}] {t['title']}" for t in tasks]
            return "\n".join(lines)
        except Exception as e:
            return f"Error: Unable to fetch tasks: {e}"


if __name__ == "__main__":
    # Start the stdio JSON-RPC loop defined by modelcontextprotocol.io
    mcp.run(transport="stdio")

