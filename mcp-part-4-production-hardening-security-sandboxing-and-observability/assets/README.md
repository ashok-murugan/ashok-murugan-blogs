# Companion Code: Model Context Protocol (MCP) Part 4 — Production Hardening: Security, Sandboxing & Observability

This folder contains reference implementations, container configurations, and architectural guides for production-hardening MCP servers.

---

## 📁 Files Overview

- **`hardened_server.py`**: A production-grade Python FastMCP server demonstrating:
  - **Sliding-Window Rate Limiting**: Mitigating recursive AI tool execution loops.
  - **Input Boundary Sanitization**: String length bounds, strict enum constraints, and schema enforcement.
  - **Human-in-the-Loop (HITL) Confirmation Token**: Protecting destructive operations (`delete_task`).
  - **Structured JSON Audit Logging to `stderr`**: Invariant-compliant logging that never pollutes `stdout`.
  - **W3C Distributed Trace Propagation**: Forwarding `traceparent` context.
- **`banner.png`**: Article banner adhering to Chalk White (`#f8fafc`) + Protocol Blue (`#2563eb`) + Emerald Green (`#059669`).
- **`agent-threat-model.png`**: Visual breakdown of Indirect Prompt Injection, Confused Deputy attacks, and the 4 Defense Rings.
- **`sandboxed-mcp-architecture.png`**: Container sandbox boundary diagram (seccomp, read-only rootfs, no-network).
- **`otel-distributed-tracing.png`**: OpenTelemetry distributed span correlation across host, stdio, and backend.

---

## 🔒 Containerized Sandboxing Quickstart

To run this server inside a production-hardened Docker container with zero network egress, read-only root filesystem, and dropped capabilities:

```bash
# 1. Build the lightweight container
docker build -t mcp-hardened:v1 .

# 2. Run with maximum isolation flags connected over stdio
docker run --rm -i \
  --network=none \
  --read-only \
  --cap-drop=ALL \
  --user=nobody:nogroup \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  mcp-hardened:v1
```

---

## 🔗 Official Documentation References
- [MCP Security Best Practices](https://modelcontextprotocol.io/docs/concepts/architecture#security)
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [OWASP Top 10 for Large Language Models](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

