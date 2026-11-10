# Companion Code: Model Context Protocol (MCP) Part 3 — Under the Hood: JSON-RPC & Stdio Transport

This folder contains a **zero-dependency, standard-library implementation** of both an MCP Host Client and an MCP Server communicating over standard OS pipes (`stdin`, `stdout`, `stderr`).

---

## 📁 Files Overview

- **`raw_mcp_client.py`**: A pure standard-library (`subprocess`, `threading`, `json`) implementation of an MCP Host Client. It spawns the child process, creates dedicated reader threads for `stdout` (line-delimited JSON-RPC deserialization) and `stderr` (telemetry sink), correlates request/response IDs, and manages graceful process termination.
- **`raw_stdio_server.py`**: A pure standard-library MCP Server showing how to implement protocol handshakes, notifications, tools listing, and tool execution without importing FastMCP or any third-party framework.
- **`banner.png`**: Article banner adhering to Chalk White (`#f8fafc`) + Protocol Blue (`#2563eb`) + Emerald Green (`#059669`).
- **`stdio-pipe-multiplexing.png`**: Visual breakdown of the 3 OS file descriptors and channel hygiene.
- **`json-rpc-framing.png`**: Byte stream chunking, line accumulator buffering, and message schemas.
- **`error-contract-flow.png`**: Wire-level JSON-RPC protocol error vs application domain error architecture.

---

## 🚀 Running the Zero-Dependency Client & Server

No virtual environment or third-party packages are required:

```bash
# Run the raw MCP client (spawns raw_stdio_server.py by default)
python raw_mcp_client.py
```

### What You Will Observe:
1. **Child Subprocess Spawning**: The client forks `python raw_stdio_server.py` with line-buffered OS stream pipes.
2. **Capability Negotiation**: The client issues an `initialize` JSON-RPC request and receives the server's capabilities.
3. **Initialized Confirmation**: The client dispatches a one-way `notifications/initialized` event (omitting the `id` field).
4. **Tool Discovery**: Client queries `tools/list` and receives the validated input schema.
5. **Tool Execution**: Client executes `tools/call` with argument payload and prints the result.
6. **Graceful EOF Teardown**: The host closes `stdin`. The server's stream reader reaches EOF and exits with code `0`.

---

## 🔗 Official Documentation References
- [MCP Specification: Transports](https://modelcontextprotocol.io/docs/concepts/transports)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [MCP Architecture Principles](https://modelcontextprotocol.io/docs/concepts/architecture)
