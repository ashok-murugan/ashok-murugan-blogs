# Companion Code: Model Context Protocol (MCP) Part 2 — Hands, Eyes, and Recipes

This folder contains the complete, runnable Python FastMCP reference server demonstrating the three core primitives of the **Model Context Protocol (MCP)**:
- **Tools (Hands / Verbs)**: `add_task`, `complete_task`, `delete_task`
- **Resources (Eyes / Nouns)**: `tasks://all`, `tasks://status/{status}`, `tasks://stats`
- **Prompts (Recipes / Workflows)**: `daily_standup`, `task_prioritization_audit`

---

## 🛠️ Prerequisites

- **Python**: 3.10 or higher
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`
- **Node.js**: v18+ (for running the official `@modelcontextprotocol/inspector`)

---

## 🚀 Quickstart

### 1. Run Directly with FastMCP CLI
```bash
# Using uv (fastest, zero-install virtualenv)
uv run server.py
```

### 2. Interactive Testing with the Official MCP Inspector
The easiest way to test Tools, Resources, and Prompts interactively in your browser without needing Claude Desktop or Cursor configured is via the official **MCP Inspector**:

```bash
npx @modelcontextprotocol/inspector uv run server.py
```

Once running, the Inspector web UI will launch (typically at `http://localhost:5173`):
1. **Resources Tab**:
   - Click **List Resources** to discover `tasks://all`, `tasks://stats`, and URI templates.
   - Click `tasks://all` to fetch the real-time JSON task array.
   - Enter `tasks://status/completed` to inspect dynamically routed parameters.
2. **Tools Tab**:
   - Inspect the generated JSON Schema for `add_task`, `complete_task`, and `delete_task`.
   - Execute `add_task` with `{"title": "Setup distributed caching layer"}`.
   - Switch back to the **Resources Tab** and re-fetch `tasks://all` to see the updated state!
3. **Prompts Tab**:
   - Click `daily_standup`.
   - Enter `Core Platform Team` as the `team_name` argument.
   - Observe how the server dynamically hydrates the prompt with the live `tasks_db` state and returns structured LLM instructions.

---

## 📁 Architecture Overview

```
mcp-part-2-hands-eyes-and-recipes/assets/
├── server.py           # Unified FastMCP server exposing Tools, Resources & Prompts
├── requirements.txt    # Python dependencies (mcp[cli]>=1.0.0)
├── banner.png          # Blog header banner (Chalk White + Blue + Emerald)
├── the-mcp-triad.png   # Architectural breakdown: Tools vs Resources vs Prompts
├── resource-uri-routing.png # URI dispatching and context hydration flow
├── prompt-workflow-flow.png # Prompt argument compilation and context injection
└── README.md           # This document
```

---

## 🔗 Official Documentation References
- [MCP Tools Specification](https://modelcontextprotocol.io/docs/concepts/tools)
- [MCP Resources Specification](https://modelcontextprotocol.io/docs/concepts/resources)
- [MCP Prompts Specification](https://modelcontextprotocol.io/docs/concepts/prompts)
- [FastMCP Python SDK Guide](https://github.com/modelcontextprotocol/python-sdk)

