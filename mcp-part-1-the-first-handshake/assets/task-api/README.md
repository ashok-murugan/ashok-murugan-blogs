# Task REST API Service (Companion Backend)

This directory contains the standalone backend service that our Python MCP Server adapter bridges to in **[Model Context Protocol (MCP) Explained, Part 1: The First Handshake](https://blogs.ashokmurugan.com/mcp-part-1-the-first-handshake)**.

---

## Architectural Role

> **Mental Model:**  
> **MCP Server** = **Traditional Backend Service** + **MCP Adapter**

This service represents the **Traditional Backend Service**. It is an ordinary, concurrent HTTP microservice with **zero knowledge of AI or MCP**. The Python FastMCP adapter (`server.py` in the parent directory) communicates with this backend over standard HTTP REST.

---

## Prerequisites
* [Go 1.22+](https://go.dev/dl/) installed.
* Zero third-party packages required (uses only the Go standard library `net/http`, `sync`, `encoding/json`).

---

## How to Run

From this directory, start the HTTP server:

```bash
go run main.go
```

*Output:*
```text
2026/11/10 19:00:00 Starting Task REST API on http://localhost:8080 ...
```

---

## API Endpoints

| Method | Endpoint | Description | Sample Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck endpoint | `curl http://localhost:8080/health` |
| `GET` | `/tasks` | List all tasks (optional `?status=ALL\|PENDING\|COMPLETED`) | `curl http://localhost:8080/tasks` |
| `POST` | `/tasks` | Create a new task | `curl -X POST http://localhost:8080/tasks -H "Content-Type: application/json" -d '{"title":"Ship MCP"}'` |
| `POST/PUT` | `/tasks/{id}/complete` | Mark a task as completed | `curl -X POST http://localhost:8080/tasks/1/complete` |

---

## How the MCP Adapter Connects

1. **Keep this service running** in one terminal (`http://localhost:8080`).
2. In another terminal, navigate to the parent `assets/` directory and run the Python FastMCP adapter:
   ```bash
   python server.py
   ```
   Or launch it inside the official **MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector python server.py
   ```
3. When the AI model invokes `add_task(title="Review PR")`, the Python adapter sends a `POST http://localhost:8080/tasks` request here and returns the formatted response back over the JSON-RPC `stdio` pipe.

