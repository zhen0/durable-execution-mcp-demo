# Prefect MCP Server

An MCP (Model Context Protocol) server for interacting with Prefect deployments and events. This server provides programmatic access to Prefect functionality for AI agents and other MCP clients, following best practices from the FastMCP framework.

## Features

### Resources (Read-only)
- **`prefect://deployments`** - List all deployments with their details
- **`prefect://events/recent`** - Get recent events from the Prefect instance

### Tools (Actions)
- **`run_deployment`** - Run a deployment by ID
- **`run_deployment_by_name`** - Run a deployment by flow/deployment name
- **`read_events`** - Read events with filtering options

## Installation

```bash
uv add prefect-mcp-server
```

Or install from source:
```bash
git clone https://github.com/prefecthq/prefect-mcp-server.git
cd prefect-mcp-server
uv sync
```

## Configuration

The server uses environment variables for configuration. Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

### Environment Variables

The Prefect SDK reads these directly from your environment:
- `PREFECT_API_URL` - URL of your Prefect server or Prefect Cloud workspace  
- `PREFECT_API_KEY` - API key for Prefect Cloud (optional for local server)

Optional MCP server settings (can be set in `.env`):
- `DEPLOYMENTS_DEFAULT_LIMIT` - Default limit for deployments list (default: 100)
- `EVENTS_DEFAULT_LIMIT` - Default limit for events list (default: 50)

### For Prefect Cloud:
```bash
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]"
export PREFECT_API_KEY="your-api-key"
```

### For Local Prefect Server:
```bash
export PREFECT_API_URL="http://localhost:4200/api"
```

## Usage

### Running the Server

```bash
# Using FastMCP CLI
uv run fastmcp run src/prefect_mcp_server/server.py

# Or as a module
uv run python -m prefect_mcp_server
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "prefect": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "prefect-mcp-server",
        "fastmcp",
        "run",
        "path/to/prefect-mcp-server/src/prefect_mcp_server/server.py"
      ],
      "env": {
        "PREFECT_API_URL": "your-prefect-api-url",
        "PREFECT_API_KEY": "your-api-key-if-needed"
      }
    }
  }
}
```

## Examples

### List Deployments
```python
# MCP clients can call the resource
deployments = await client.read_resource("prefect://deployments")
```

### Run a Deployment
```python
# Run by ID
result = await client.call_tool("run_deployment", {
    "deployment_id": "abc-123-def",
    "parameters": {"key": "value"}
})

# Run by name
result = await client.call_tool("run_deployment_by_name", {
    "flow_name": "my-flow",
    "deployment_name": "production",
    "parameters": {"key": "value"}
})
```

### Read Events
```python
# Get flow run events
events = await client.call_tool("read_events", {
    "limit": 50,
    "event_prefix": "prefect.flow-run."
})
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest
```