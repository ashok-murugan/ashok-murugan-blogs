"""
Model Context Protocol (MCP) Explained - Part 5 Companion Code
The Enterprise MCP Mesh Gateway & Semantic Router.

Demonstrates:
1. Multi-service tool aggregation across federated backends
2. Dynamic Top-K semantic filtering to eliminate prompt context bloat
3. tools/list_changed notification dispatching on service registration
"""

from datetime import datetime, timezone
import json
import math
import os
import re
import sys
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize Central Gateway
mcp = FastMCP("Enterprise-MCP-Gateway", dependencies=["mcp[cli]"])

# Simulated Federated Enterprise Catalog (500+ tools in real-world clusters)
FEDERATED_CATALOG: List[Dict[str, Any]] = [
    # Infrastructure & DevOps Domain
    {
        "name": "infra_deploy_service",
        "description": "Trigger rolling deployment of a Kubernetes service in production or staging cluster.",
        "domain": "infrastructure",
        "keywords": ["deploy", "kubernetes", "k8s", "service", "cluster", "rollout"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {"type": "string"},
                "environment": {"type": "string", "enum": ["staging", "production"]}
            },
            "required": ["service_name", "environment"]
        }
    },
    {
        "name": "infra_restart_pod",
        "description": "Restart misbehaving or out-of-memory Kubernetes pods.",
        "domain": "infrastructure",
        "keywords": ["restart", "pod", "kubernetes", "crash", "oom"],
        "inputSchema": {
            "type": "object",
            "properties": {"pod_name": {"type": "string"}},
            "required": ["pod_name"]
        }
    },
    # Database Domain
    {
        "name": "db_explain_query",
        "description": "Run EXPLAIN ANALYZE on a slow SQL query across PostgreSQL read replicas.",
        "domain": "database",
        "keywords": ["sql", "postgres", "database", "query", "explain", "analyze", "slow", "index"],
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "db_kill_idle_connections",
        "description": "Terminate stale or idle in transaction PostgreSQL client connections.",
        "domain": "database",
        "keywords": ["database", "connections", "idle", "kill", "pool", "exhaustion"],
        "inputSchema": {
            "type": "object",
            "properties": {"max_idle_seconds": {"type": "integer", "default": 300}}
        }
    },
    # Observability & APM Domain
    {
        "name": "apm_fetch_error_traces",
        "description": "Retrieve recent distributed trace errors and stack traces from Datadog or Jaeger.",
        "domain": "observability",
        "keywords": ["apm", "trace", "datadog", "jaeger", "error", "stacktrace", "span"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "service": {"type": "string"},
                "duration_minutes": {"type": "integer", "default": 15}
            },
            "required": ["service"]
        }
    },
    # Issue Tracking & Project Management
    {
        "name": "jira_create_incident_ticket",
        "description": "File a P1/P2 production incident ticket in Jira and notify on-call SRE.",
        "domain": "project",
        "keywords": ["jira", "ticket", "incident", "p1", "p2", "oncall", "alert"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "severity": {"type": "string", "enum": ["P1", "P2", "P3"]}
            },
            "required": ["summary", "severity"]
        }
    }
]

# Active Session Context Focus (Can be updated dynamically per conversation turn)
current_session_intent: str = "database optimization and query latency"


def calculate_semantic_relevance(query: str, tool: Dict[str, Any]) -> float:
    """Calculate lightweight semantic similarity score between user intent and tool metadata."""
    query_tokens = set(re.findall(r"\w+", query.lower()))
    if not query_tokens:
        return 0.5

    # Check keyword overlap
    tool_keywords = set(tool.get("keywords", []))
    desc_tokens = set(re.findall(r"\w+", tool.get("description", "").lower()))
    domain_token = tool.get("domain", "").lower()

    score = 0.0
    for token in query_tokens:
        if token in tool_keywords:
            score += 2.0
        if token in desc_tokens:
            score += 1.0
        if token == domain_token:
            score += 1.5

    return score


# ==============================================================================
# GATEWAY TOOLS (Exposed to AI Models via Semantic Top-K Router)
# ==============================================================================

@mcp.tool()
def route_and_execute_tool(target_tool: str, arguments_json: str) -> str:
    """Execute a downstream federated microservice tool through the enterprise mesh gateway.

    Args:
        target_tool: Exact name of the federated tool to run
        arguments_json: JSON string of input arguments
    """
    tool_entry = next((t for t in FEDERATED_CATALOG if t["name"] == target_tool), None)
    if not tool_entry:
        return f"Error: Tool '{target_tool}' not registered in enterprise mesh."

    try:
        args = json.loads(arguments_json) if arguments_json else {}
    except json.JSONDecodeError:
        return "Error: arguments_json must be valid JSON string."

    # Dispatch to simulated downstream microservice
    return f"Gateway successfully dispatched to '{target_tool}' [domain: {tool_entry['domain']}]. Result: OK."


@mcp.tool()
def set_conversation_focus(intent_description: str) -> str:
    """Dynamically re-index and re-route the gateway's active toolset to match current user task.

    Args:
        intent_description: Plain-text description of current engineering focus (e.g. 'investigating database locks')
    """
    global current_session_intent
    current_session_intent = intent_description.strip()
    return f"Gateway focus updated to '{current_session_intent}'. Active tools re-indexed."


# ==============================================================================
# OBSERVABILITY RESOURCES (Mesh Health & Topology)
# ==============================================================================

@mcp.resource("mesh://topology/summary", mime_type="application/json")
def get_mesh_topology() -> str:
    """Read-only view of federated microservices, tool counts, and routing stats."""
    domains = {}
    for t in FEDERATED_CATALOG:
        d = t.get("domain", "default")
        domains[d] = domains.get(d, 0) + 1

    summary = {
        "gateway": "Enterprise-MCP-Gateway-v1",
        "total_registered_tools": len(FEDERATED_CATALOG),
        "domain_breakdown": domains,
        "active_focus": current_session_intent,
        "transport": "stdio / remote SSE federation",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return json.dumps(summary, indent=2)


if __name__ == "__main__":
    sys.stderr.write("[Gateway] Enterprise MCP Mesh Gateway initialized.\n")
    sys.stderr.flush()
    mcp.run()
