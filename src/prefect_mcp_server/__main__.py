"""Entry point for running the Prefect MCP server."""

from prefect_mcp_server.server import mcp

if __name__ == "__main__":
    # This allows running with: python -m prefect_mcp_server
    # or: uv run fastmcp run src/prefect_mcp_server/server.py
    mcp.run()