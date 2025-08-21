# prefect-mcp-server

A [FastMCP](https://github.com/jlowin/fastmcp) server for interacting with [Prefect](https://prefect.io) deployments and events through the Model Context Protocol.

## quick start

```bash
# clone and install
git clone https://github.com/prefecthq/prefect-mcp-server.git
cd prefect-mcp-server
uv sync

# run the server  
uv run -m prefect_mcp_server

# from github
uv run git+https://github.com/prefecthq/prefect-mcp-server.git
```

## features

<details>
<summary><b>📚 resources</b> - read deployment and event data</summary>

- `prefect://deployments/list` - list all deployments with their details
- `prefect://events/recent` - get recent events from the prefect instance

</details>

<details>
<summary><b>🔧 tools</b> - trigger deployments and query events</summary>

- `run_deployment` - run a deployment by id
- `run_deployment_by_name` - run a deployment by flow/deployment name  
- `read_events` - read events with filtering options

</details>

## installation

<details open>
<summary><b>from github</b></summary>

```bash
uv add prefect-mcp-server@git+https://github.com/prefecthq/prefect-mcp-server.git
```

</details>

<details>
<summary><b>from source</b></summary>

```bash
git clone https://github.com/prefecthq/prefect-mcp-server.git
cd prefect-mcp-server
uv sync
```

</details>

## configuration

<details open>
<summary><b>environment variables</b></summary>

The Prefect SDK reads these directly from your environment:

**required:**
- `PREFECT_API_URL` - url of your prefect server or cloud workspace
- `PREFECT_API_KEY` - api key for prefect cloud (not required for open source server)

**optional server settings:**
- `DEPLOYMENTS_DEFAULT_LIMIT` - default limit for deployments list (default: 100)
- `EVENTS_DEFAULT_LIMIT` - default limit for events list (default: 50)

<details>
<summary>prefect cloud setup</summary>

```bash
export PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]"
export PREFECT_API_KEY="your-api-key"
```

</details>

<details>
<summary>local prefect server setup</summary>

```bash
export PREFECT_API_URL="http://localhost:4200/api"
```

</details>

</details>

## usage

<details open>
<summary><b>with claude code</b></summary>

Install from source using the FastMCP CLI:

```bash
# clone and install
git clone https://github.com/prefecthq/prefect-mcp-server.git
cd prefect-mcp-server

# install to claude code
fastmcp install claude-code src/prefect_mcp_server/server.py \
  --env PREFECT_API_URL=your-url \
  --env PREFECT_API_KEY=your-key
```

</details>

<details>
<summary><b>standalone server</b></summary>

```bash
# as a python module
uv run -m prefect_mcp_server

# or using fastmcp cli
uv run fastmcp run src/prefect_mcp_server/server.py
```

</details>

<details>
<summary><b>programmatic usage</b></summary>

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

</details>

## examples

<details>
<summary><b>list deployments</b></summary>

```python
deployments = await client.read_resource("prefect://deployments/list")
# returns: {"success": true, "count": 3, "deployments": [...]}
```

</details>

<details>
<summary><b>run deployment by id</b></summary>

```python
result = await client.call_tool(
    "run_deployment",
    {
        "deployment_id": "abc-123-def",
        "parameters": {"key": "value"},
        "name": "custom run name",
        "tags": ["mcp", "automated"]
    }
)
# returns: {"success": true, "flow_run": {...}}
```

</details>

<details>
<summary><b>run deployment by name</b></summary>

```python
result = await client.call_tool(
    "run_deployment_by_name",
    {
        "flow_name": "my-flow",
        "deployment_name": "production",
        "parameters": {"key": "value"}
    }
)
# returns: {"success": true, "flow_run": {...}, "deployment": {...}}
```

</details>

<details>
<summary><b>read events</b></summary>

```python
events = await client.call_tool(
    "read_events",
    {
        "limit": 50,
        "event_prefix": "prefect.flow-run.",
        "occurred_after": "2024-01-01T00:00:00Z"
    }
)
# returns: {"success": true, "count": 10, "events": [...]}
```

</details>

## development

<details>
<summary><b>setup</b></summary>

```bash
# clone the repo
git clone https://github.com/prefecthq/prefect-mcp-server.git
cd prefect-mcp-server

# install with dev dependencies
uv sync --dev

# run tests
uv run pytest

# run with debug logging
DEPLOYMENTS_DEFAULT_LIMIT=10 uv run fastmcp dev src/prefect_mcp_server/server.py
```

</details>

<details>
<summary><b>testing</b></summary>

Tests use an ephemeral prefect database via `prefect_test_harness`:

```bash
# run all tests
uv run pytest

# run with coverage
uv run pytest --cov=src --cov-report=html

# run specific test
uv run pytest tests/test_server.py::test_run_deployment_with_valid_id -xvs
```

</details>

## links

- [FastMCP](https://github.com/jlowin/fastmcp) - the framework powering this server
- [Prefect](https://prefect.io) - modern workflow orchestration
- [Model Context Protocol](https://modelcontextprotocol.io) - the protocol specification