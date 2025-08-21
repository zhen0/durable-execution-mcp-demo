# prefect-mcp-server

a [FastMCP](https://github.com/jlowin/fastmcp) server for interacting with [`prefect`](https://github.com/prefecthq/prefect) resources.

## quick start

```bash
# from github
uvx prefect-mcp-server@git+https://github.com/prefecthq/prefect-mcp-server.git
```

```bash
# clone and install
gh repo clone prefecthq/prefect-mcp-server && cd prefect-mcp-server
uv run prefect-mcp-server
```

## features

**resources** - read deployment and event data
- `prefect://deployments/list` - list all deployments with their details
- `prefect://events/recent` - get recent events from the prefect instance

**tools** - trigger deployments and query events
- `run_deployment` - run a deployment by id
- `run_deployment_by_name` - run a deployment by flow/deployment name  
- `read_events` - read events with filtering options

## installation

```bash
# from github
uv add prefect-mcp-server@git+https://github.com/prefecthq/prefect-mcp-server.git

# or from source
gh repo clone prefecthq/prefect-mcp-server && cd prefect-mcp-server
uv sync
```

## configuration

the prefect sdk reads these directly from your environment:

**required:**
- `PREFECT_API_URL` - url of your prefect server or cloud workspace
- `PREFECT_API_KEY` - api key for prefect cloud (not required for open source server)

**optional:**
- `DEPLOYMENTS_DEFAULT_LIMIT` - default limit for deployments list (default: 100)
- `EVENTS_DEFAULT_LIMIT` - default limit for events list (default: 50)

```bash
# prefect cloud
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]"
export PREFECT_API_KEY="your-api-key"

# local prefect server
export PREFECT_API_URL="http://localhost:4200/api"
```

## usage

### with claude code

```bash
# add to claude code
claude mcp add prefect \
  -e PREFECT_API_URL=your-url \
  -e PREFECT_API_KEY=your-key \
  -- uvx prefect-mcp-server@git+https://github.com/prefecthq/prefect-mcp-server.git
```

### standalone server

```bash
# as a python module
uv run prefect-mcp-server

# or using fastmcp cli
uv run fastmcp run src/prefect_mcp_server/server.py
```

### programmatic usage

```python
from fastmcp import Client

async def main():
    async with Client("prefect-mcp-server") as client:
        # list deployments
        deployments = await client.read_resource("prefect://deployments/list")
        
        # run a deployment
        result = await client.call_tool(
            "run_deployment",
            {"deployment_id": "abc-123-def"}
        )
        
        # read events
        events = await client.call_tool(
            "read_events",
            {"limit": 50, "event_prefix": "prefect.flow-run."}
        )
```

## examples

```python
# list deployments
deployments = await client.read_resource("prefect://deployments/list")
# returns: {"success": true, "count": 3, "deployments": [...]}

# run deployment by id  
result = await client.call_tool(
    "run_deployment",
    {
        "deployment_id": "abc-123-def",
        "parameters": {"key": "value"},
        "name": "custom run name",
        "tags": ["mcp", "automated"]
    }
)

# run deployment by name
result = await client.call_tool(
    "run_deployment_by_name",
    {
        "flow_name": "my-flow",
        "deployment_name": "production",
        "parameters": {"key": "value"}
    }
)

# read events
events = await client.call_tool(
    "read_events",
    {
        "limit": 50,
        "event_prefix": "prefect.flow-run.",
        "occurred_after": "2024-01-01T00:00:00Z"
    }
)
```

## development

<details>
<summary>setup & testing</summary>

```bash
# clone the repo
gh repo clone prefecthq/prefect-mcp-server && cd prefect-mcp-server

# install with dev dependencies
uv sync --dev

# run tests (uses ephemeral prefect database via prefect_test_harness)
uv run pytest

# run with coverage
uv run pytest --cov=src --cov-report=html

# run with debug logging
DEPLOYMENTS_DEFAULT_LIMIT=10 uv run fastmcp dev src/prefect_mcp_server/server.py
```

</details>

## links

- [FastMCP](https://github.com/jlowin/fastmcp) - the easiest way to build an MCP server
- [Prefect](https://prefect.io) - the easiest way to build workflows