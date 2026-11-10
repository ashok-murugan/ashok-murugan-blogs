"""
Model Context Protocol (MCP) Explained - Part 3 Companion Code
Zero-dependency, pure standard-library raw MCP Server demonstrating
manual sys.stdin reading, line framing, and strictly guarded stdout.
"""

import json
import sys


def log_debug(msg: str):
    """Write diagnostic logs strictly to stderr. stdout is sacred!"""
    sys.stderr.write(f"[RawServer STDERR] {msg}\n")
    sys.stderr.flush()


def send_response(req_id: int, result: dict):
    """Format single-line JSON-RPC response and flush to stdout."""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": result
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def send_error(req_id: int, code: int, message: str):
    """Format single-line JSON-RPC wire error."""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": code,
            "message": message
        }
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def main():
    log_debug("Raw MCP Server initialized. Awaiting stdio requests...")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            log_debug(f"JSON Parse Error: {e}")
            send_error(None, -32700, "Parse error: Invalid JSON")
            continue

        method = req.get("method")
        req_id = req.get("id")
        params = req.get("params", {})
        log_debug(f"Received RPC method: {method} (id={req_id})")

        # 1. Initialize Handshake
        if method == "initialize":
            send_response(req_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False}
                },
                "serverInfo": {
                    "name": "Raw-StandardLibrary-MCPServer",
                    "version": "1.0.0"
                }
            })

        # 2. Initialized Notification (no id)
        elif method == "notifications/initialized":
            log_debug("Client confirmed initialization handshake complete.")

        # 3. Tools Discovery
        elif method == "tools/list":
            send_response(req_id, {
                "tools": [
                    {
                        "name": "calculate_hash",
                        "description": "Compute a deterministic string hash.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to hash"}
                            },
                            "required": ["text"]
                        }
                    }
                ]
            })

        # 4. Tool Execution
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            if tool_name == "calculate_hash":
                text = args.get("text", "")
                computed = hash(text)
                send_response(req_id, {
                    "content": [{"type": "text", "text": f"Hash of '{text}': {computed}"}],
                    "isError": False
                })
            else:
                # Expected domain error vs protocol error
                send_response(req_id, {
                    "content": [{"type": "text", "text": f"Tool '{tool_name}' is not recognized."}],
                    "isError": True
                })

        # 5. Ping
        elif method == "ping":
            send_response(req_id, {})

        else:
            # Wire-level method not found
            if req_id is not None:
                send_error(req_id, -32601, f"Method '{method}' not implemented.")


if __name__ == "__main__":
    main()
