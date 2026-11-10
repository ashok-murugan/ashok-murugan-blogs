"""
Model Context Protocol (MCP) Explained - Part 3 Companion Code
Zero-dependency, pure standard-library MCP Client demonstrating low-level
OS pipe spawning, newline-delimited JSON-RPC framing, and stream multiplexing.
"""

import json
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional


class RawMCPClient:
    """A lightweight, low-level MCP Host Client implementation over standard OS streams."""

    def __init__(self, command: list[str]):
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._pending_requests: Dict[int, threading.Event] = {}
        self._responses: Dict[int, Dict[str, Any]] = {}
        self._running = False

    def start(self):
        """Spawn the child MCP server process with redirected standard streams."""
        print(f"[Host] Spawning MCP server subprocess: {' '.join(self.command)}")
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
        )
        self._running = True

        # Thread 1: Reader for stdout (The Sacred Wire)
        self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self.stdout_thread.start()

        # Thread 2: Reader for stderr (Diagnostic telemetry)
        self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self.stderr_thread.start()

    def _read_stdout(self):
        """Continuously read newline-delimited JSON-RPC messages from stdout."""
        for line in self.process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                msg_id = msg.get("id")
                if msg_id is not None and msg_id in self._pending_requests:
                    self._responses[msg_id] = msg
                    self._pending_requests[msg_id].set()
                else:
                    # One-way notification from server
                    print(f"[Host] Received Notification: method={msg.get('method')}")
            except json.JSONDecodeError as e:
                print(f"[Host FATAL] Corrupt non-JSON bytes received on stdout: {line!r} ({e})")

    def _read_stderr(self):
        """Continuously read diagnostic and telemetry logs from stderr."""
        for line in self.process.stderr:
            sys.stderr.write(f"[Server STDERR] {line}")
            sys.stderr.flush()

    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Dict[str, Any]:
        """Format and write a JSON-RPC request to child stdin, awaiting response."""
        self._request_id += 1
        req_id = self._request_id

        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }
        wire_bytes = json.dumps(payload) + "\n"

        event = threading.Event()
        self._pending_requests[req_id] = event

        # Write to sacred stdin
        self.process.stdin.write(wire_bytes)
        self.process.stdin.flush()
        print(f"[Host -> Child] Sent RPC #{req_id}: {method}")

        if not event.wait(timeout=timeout):
            raise TimeoutError(f"RPC #{req_id} timed out after {timeout} seconds")

        del self._pending_requests[req_id]
        return self._responses.pop(req_id)

    def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send a one-way notification (no response expected, id omitted)."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        wire_bytes = json.dumps(payload) + "\n"
        self.process.stdin.write(wire_bytes)
        self.process.stdin.flush()
        print(f"[Host -> Child] Sent Notification: {method}")

    def close(self):
        """Clean shutdown: close stdin to signal EOF, allowing child to terminate gracefully."""
        print("[Host] Closing stdin to signal shutdown...")
        if self.process and self.process.stdin:
            self.process.stdin.close()
        if self.process:
            self.process.wait(timeout=3)
        print(f"[Host] Child process exited with code {self.process.returncode}")


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1:]
    else:
        # Default to raw standard-library server demonstrating pure stdio framing
        server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "raw_stdio_server.py"))
        command = [sys.executable, server_script]

    client = RawMCPClient(command)
    client.start()

    try:
        # Step 1: Capability Negotiation Handshake
        init_resp = client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {"roots": {"listChanged": True}},
            "clientInfo": {"name": "Ashok-RawMCP-Engine", "version": "1.0.0"}
        })
        print("\n=== 1. Handshake Response ===")
        print(json.dumps(init_resp, indent=2))

        # Step 2: Confirm initialized
        client.send_notification("notifications/initialized")

        # Step 3: Discover Tools
        tools_resp = client.send_request("tools/list", {})
        print("\n=== 2. Discovered Tools ===")
        print(json.dumps(tools_resp, indent=2))

        # Step 4: Execute a Tool Call
        call_resp = client.send_request("tools/call", {
            "name": "calculate_hash",
            "arguments": {
                "text": "Low-Level JSON-RPC Wire Test"
            }
        })
        print("\n=== 3. Tool Execution Result ===")
        print(json.dumps(call_resp, indent=2))

        # Step 5: Test Ping
        ping_resp = client.send_request("ping", {})
        print("\n=== 4. Ping Keepalive ===")
        print(json.dumps(ping_resp, indent=2))

    finally:
        client.close()


if __name__ == "__main__":
    main()
