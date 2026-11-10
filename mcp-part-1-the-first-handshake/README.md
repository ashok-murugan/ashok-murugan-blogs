---
title: "Model Context Protocol (MCP) Explained, Part 1: The First Handshake"
description: "A developer's guide to the Model Context Protocol (MCP). Learn how AI models connect to tools over JSON-RPC 2.0 stdio pipes, capability negotiation, and why stdout is sacred."
author: "Ashok Murugan"
date: "2026-11-10"
keywords: ["model-context-protocol", "mcp-tutorial", "mcp-guide", "modelcontextprotocol.io", "json-rpc-2.0", "ai-agents", "python-mcp-sdk", "llm-tool-calling", "anthropic-mcp", "cursor-mcp", "stdio-pipes"]
image: "assets/banner.png"
---

<p align="center">
  <img src="assets/banner.png" alt="Model Context Protocol MCP Explained Banner" width="80%" />
</p>

## Introduction — The USB-C Moment for Artificial Intelligence

Remember the nightmare of proprietary laptop chargers a decade ago? 

Every laptop brand had its own charging port. If you carried a Dell, a ThinkPad, and a MacBook, you needed three different bulky adapters. Then came **USB-C**: one universal plug, one open specification, and suddenly every phone, laptop, and monitor spoke the same electrical language.

In the world of Artificial Intelligence, developers have been living in that exact same proprietary mess.

If you wanted Claude to talk to your PostgreSQL database, you had to write custom function-calling wrappers. If you wanted Cursor to talk to that same database, you wrote another tool plugin. If you switched to an internal agent, you started over from scratch.

<p align="center">
  <img src="assets/integration-problem.png" alt="Comparison between Before MCP and With MCP" width="85%" />
</p>

The **[Model Context Protocol (MCP)](https://modelcontextprotocol.io/)** is the USB-C cable for AI. 

Maintained as an open standard by Anthropic and the open-source community, MCP standardizes how any AI model connects to data sources, local files, developer tools, and backend microservices. In this first part of our engineering series, we explore how an AI host and a local program introduce themselves over the wire—and why a single `print()` statement can accidentally crash the entire connection.

---

## The Core Problem — Why Not Just Traditional REST APIs

A common question systems engineers and developers ask when first reading the [official MCP specification](https://modelcontextprotocol.io/specification):

> *"We already have HTTP REST APIs and JSON. Why not just pass an OpenAPI schema to the LLM instead of inventing a whole new protocol?"*

While REST APIs are excellent for standard client-server web apps, they fall short for local AI agent orchestration due to three fundamental architectural gaps:

1. **REST is Stateless and Unidirectional:** An HTTP client asks for data, the server answers, and the socket closes. Traditional REST has no built-in bidirectional event loop for an AI editor (like Cursor or Claude Desktop) to negotiate sessions, push real-time progress notifications, or handle stateful tool interruptions.
2. **Missing Capability Negotiation:** When an AI connects to an external tool, how does it know whether the server supports dynamic resource subscriptions, prompt templates, or streaming outputs? The [MCP Architecture](https://modelcontextprotocol.io/introduction) includes a formal handshake where client and server exchange explicit capability flags before any tool is ever called.
3. **Local Process Sandboxing (Zero Open Ports):** When an AI desktop app runs on your machine, spinning up a local HTTP web server listening on `http://localhost:8080` introduces open-port attack vectors on developer workstations. MCP solves this by communicating directly over **operating system process pipes (`stdio`)**, requiring zero open network ports.

---

## The Sacred Wire — Standard Input and Standard Output

When you run a local MCP server, it does not listen on a network socket. Instead, the AI application (the Client / Host) spawns your script as a **child process** and hooks directly into its standard operating system file descriptors:

<p align="center">
  <img src="assets/stdio-pipes.png" alt="The Sacred Wire: stdio Process Pipes" width="85%" />
</p>

* **Standard Input (`stdin`):** The AI Client writes line-delimited JSON-RPC 2.0 requests into your program's input stream.
* **Standard Output (`stdout`):** Your program writes line-delimited JSON-RPC 2.0 responses back to the AI Client.
* **Standard Error (`stderr`):** Your program sends human-readable diagnostic logs to the terminal or host console.

### The Mystery of the Broken Client

Here is a rite of passage every engineer faces when building their first MCP adapter:

You write a tool to create a record. You add an innocent debugging statement:
```python
print("Connecting to backend database...")
```
Instantly, your AI client disconnects with a fatal JSON parsing error. What happened?

> **Mental Model: The Sacred Wire**  
> In local `stdio` transport, `stdout` is the sacred wire. The MCP client expects every single line on `stdout` to be a strictly valid JSON-RPC 2.0 message ending with a newline (`\n`). When you call `print()`, Python writes raw text directly to `stdout`, corrupting the JSON-RPC framing. Diagnostic logging must be routed exclusively to `stderr`.

---

## The Three-Phase Handshake — How Programs Introduce Themselves

Before an AI can ask your server to do anything, the protocol mandates a **Three-Phase Connection Handshake** as defined in the [MCP Lifecycle Specification](https://modelcontextprotocol.io/specification/architecture#lifecycle):

<p align="center">
  <img src="assets/handshake-sequence.png" alt="The 3-Phase Model Context Protocol Handshake" width="85%" />
</p>

### Phase 1: The Greeting (`initialize`)
The client sends an `initialize` request over `stdin`. It shares its protocol version (e.g. `"2024-11-05"`) and client metadata:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "cursor-client", "version": "1.0.0" }
  }
}
```
The server responds on `stdout` with its name, version, and supported capability map (e.g., `{"tools": {}, "resources": {}}`).

### Phase 2: The Acknowledgment (`notifications/initialized`)
The client acknowledges with a one-way JSON-RPC notification:
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```
Because this is a notification (no `"id"` field), the server does not send a response. Both processes are now officially connected.

### Phase 3: The Catalog Discovery (`tools/list`)
Now that the session is established, the client queries what functions are available:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```
The server responds with an array of tools, complete with their **JSON Schema** parameter contracts. The LLM reads these schemas to decide when and how to call your tools.

---

## Production Implementation — Building an MCP Server Adapter

In real enterprise systems, an MCP server is rarely a toy script with hardcoded responses. It is an **adapter** that connects an AI assistant to an existing production backend.

Below is an asynchronous Python MCP server using the official [`mcp`](https://github.com/modelcontextprotocol/python-sdk) SDK that bridges an AI agent to a live REST API:

```python
# server.py
import os
import sys
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("TASK_API_BASE", "http://localhost:8080")

# 1. Initialize FastMCP Server with lifecycle management
mcp = FastMCP(
    name="task-manager",
    instructions="Production task manager adapter. Supports creating and listing tasks."
)

# 2. Expose Tool: add_task
@mcp.tool()
async def add_task(title: str) -> str:
    """
    Create a new task in the corporate task manager.

    Args:
        title: The descriptive title of the task to create.
    """
    # ⚠️ PROTOCOL RULE: Log exclusively to stderr to avoid stdout corruption!
    sys.stderr.write(f"[Server Log] Creating task: {title}\n")
    sys.stderr.flush()

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/tasks", json={"title": title}, timeout=5.0)
        resp.raise_for_status()
        task = resp.json()
        return f"Task #{task['id']} created: '{task['title']}' [status: {task['status']}]."

# 3. Expose Tool: list_tasks
@mcp.tool()
async def list_tasks(status: Optional[str] = "ALL") -> str:
    """
    Retrieve tasks from the task manager filtered by status.

    Args:
        status: Filter criteria: ALL, PENDING, or COMPLETED.
    """
    sys.stderr.write(f"[Server Log] Querying tasks with filter: {status}\n")
    sys.stderr.flush()

    async with httpx.AsyncClient() as client:
        params = {} if not status or status == "ALL" else {"status": status.upper()}
        resp = await client.get(f"{API_BASE}/tasks", params=params, timeout=5.0)
        resp.raise_for_status()
        tasks = resp.json()

        lines = [f"#{t['id']} [{t['status']}] {t['title']}" for t in tasks]
        return "\n".join(lines) if lines else "No tasks found."


if __name__ == "__main__":
    # Start listening over standard I/O OS pipes
    mcp.run(transport="stdio")
```

### Why This Architecture Works:
1. **Zero Manual JSON Parsing:** FastMCP automatically reflects Python type hints (`title: str`, `status: Optional[str]`) and docstrings into JSON Schema definitions sent during `tools/list`.
2. **Safe Logging:** All diagnostics use `sys.stderr`, keeping the `stdout` JSON-RPC stream pure.
3. **Decoupled Architecture:** The backend service remains a standard HTTP microservice; the MCP adapter simply exposes it safely to the AI model.

*(A complete, runnable reference implementation of this adapter is included in this article's [`assets/task_manager_server.py`](./assets/task_manager_server.py) file).*

---

## Conclusion

The Model Context Protocol establishes the fundamental foundation for agentic AI engineering:

* **Open USB-C Standard:** Solves the $M \times N$ fragmentation problem across AI clients and enterprise data sources.
* **Process Sandboxing:** Uses OS `stdio` pipes to run tools locally on developer machines without opening vulnerable network ports.
* **The Sacred Wire:** Keeps `stdout` strictly reserved for newline-delimited JSON-RPC frames while routing all diagnostics to `stderr`.
* **The 3-Phase Handshake:** Negotiates capabilities upfront before exposing tool schemas dynamically to the LLM.

Now that our AI knows how to shake hands and discover tools over the wire, what kind of capabilities can it expose?

In **Part 2: Hands, Eyes, and Recipes**, we explore the three core primitives defined by [modelcontextprotocol.io](https://modelcontextprotocol.io/)—**Tools**, **Resources**, and **Prompts**—and why treating every data source as a tool is a dangerous anti-pattern.
