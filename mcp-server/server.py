"""Standalone MCP Server entrypoint."""
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.mcp.server import local_mcp_server


def main():
    """Stdio JSON-RPC server loop."""
    print("AURA MCP Server running on stdio...", file=sys.stderr)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            resp = local_mcp_server.handle_json_rpc(req)
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            print(json.dumps(err), flush=True)


if __name__ == "__main__":
    main()
