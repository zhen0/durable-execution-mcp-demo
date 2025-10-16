# PydanticAI + PrefectAgent + Prefect MCP Demo

A demo showcasing [PydanticAI](https://ai.pydantic.dev) with [PrefectAgent](https://ai.pydantic.dev/durable_execution/prefect/) for durable execution, connected to the [Prefect MCP server](https://github.com/PrefectHQ/prefect-mcp-server).

## What This Demonstrates

- **Durable Execution**: Model requests and MCP tool calls tracked as Prefect tasks with automatic retries
- **Prefect Native Configuration**: Uses Prefect variables and secret blocks instead of environment variables
- **Code Storage**: Deploys from GitHub repo using `flow.from_source()`
- **MCP Integration**: Connect to Prefect MCP server to query and manage Prefect resources
- **Managed Execution**: No infrastructure to manage with Prefect's managed work pools
- **Optional Observability**: Logfire integration for detailed traces

## Prerequisites

1. **Prefect Cloud account** - [Sign up](https://app.prefect.cloud)
2. **Model API key** - Choose one:
   - [Anthropic API key](https://console.anthropic.com/) (Claude)
   - [OpenAI API key](https://platform.openai.com/api-keys) (GPT)
3. **Python 3.10+**

## Setup

### 1. Create Prefect Variables

```bash
# MCP server URL (required)
prefect variable set fastmcp-server-url "https://your-mcp-server-url/mcp"

# Model to use (optional, defaults to Claude 3.5 Sonnet)
prefect variable set pydantic-ai-model "anthropic:claude-3-5-sonnet-20241022"
```

### 2. Create Prefect Secret Blocks

```bash
# Register the secret block type
prefect block register -m prefect.blocks.system
```

Then create secrets using Python:

```python
from prefect.blocks.system import Secret

# For Anthropic Claude models (required if using Claude)
anthropic_secret = Secret(value="your-anthropic-api-key")
anthropic_secret.save(name="anthropic-api-key")

# For OpenAI models (required if using OpenAI)
openai_secret = Secret(value="your-openai-api-key")
openai_secret.save(name="openai-api-key")

# For Logfire observability (optional)
logfire_secret = Secret(value="your-logfire-token")
logfire_secret.save(name="logfire-token")
```

### 3. Deploy to Prefect Cloud

```bash
cd examples/pydantic-ai-demo
python deploy.py
```

This will:
- Pull code from GitHub using `flow.from_source()`
- Load configuration from Prefect variables and secrets
- Create a deployment using Prefect managed execution
- No workers needed!

## Usage

### Trigger a Run

```bash
# Run with default prompt (dashboard overview)
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo'

# Run with a custom prompt
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \
  --param prompt='List my most recent failing flow runs'

# Run with a different model
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \
  --param model='openai:gpt-4o'
```

### Example Prompts

```bash
# Dashboard overview
--param prompt='Show me a dashboard overview of my Prefect instance'

# Debug failing runs
--param prompt='List my most recent failing flow runs and tell me what failed'

# Check deployments
--param prompt='Show me all my active deployments'

# Work pool status
--param prompt='Show me the status of my work pools including active workers'
```

### View Results

**Prefect Cloud UI**: View flow execution, task breakdown, and logs at https://app.prefect.cloud

You'll see:
- `create-prefect-mcp-agent` task (agent creation with API key loading)
- `prefect-assistant_model_request` tasks (LLM calls)
- `prefect-assistant_mcp_[tool_name]` tasks (MCP tool calls)

**Logfire UI** (if configured): View detailed traces of agent execution, model calls, and tool usage

## Configuration

### Variables

- **fastmcp-server-url** (required): URL of your MCP server
- **pydantic-ai-model** (optional): Model to use (defaults to `anthropic:claude-3-5-sonnet-20241022`)

### Secret Blocks

- **anthropic-api-key** (required for Claude): Anthropic API key
- **openai-api-key** (required for OpenAI): OpenAI API key
- **logfire-token** (optional): Logfire token for observability

The flow automatically loads the appropriate API key based on the model provider (anthropic: or openai:).

## Supported Models

### Anthropic (Claude)
- `anthropic:claude-3-5-sonnet-20241022` (default, recommended)
- `anthropic:claude-3-opus-20240229`
- `anthropic:claude-3-sonnet-20240229`

### OpenAI (GPT)
- `openai:gpt-4o`
- `openai:gpt-4o-mini`
- `openai:gpt-4-turbo`

## Local Testing (Optional)

For local development, you can set environment variables:

```bash
export FASTMCP_SERVER_URL='https://your-server.fastmcp.app/mcp'
export ANTHROPIC_API_KEY='sk-ant-...'

python demo_flow.py
```

Note: When deployed, the flow loads configuration from Prefect variables and secrets, not environment variables.

## Architecture

```
┌─────────────────────┐
│  Prefect Cloud      │
│  (Managed Execution)│
│                     │
│  ┌───────────────┐  │
│  │ PydanticAI    │  │
│  │ Agent Flow    │  │
│  │ + PrefectAgent│  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
           │ MCP Protocol
           │
           ▼
┌─────────────────────┐
│  Prefect MCP Server │
│                     │
│  Tools:             │
│  - get_dashboard    │
│  - get_flow_runs    │
│  - get_deployments  │
│  - get_work_pools   │
│  - etc.             │
└─────────────────────┘
           │
           │ Prefect API
           │
           ▼
┌─────────────────────┐
│  Prefect Cloud API  │
└─────────────────────┘
```

## Key Features

1. **Durable Execution**: Every model request and tool call is a tracked Prefect task with automatic retries
2. **Native Configuration**: Uses Prefect variables and secrets for secure configuration management
3. **Code Storage**: Deploys from GitHub, no local code packaging needed
4. **Automatic Key Loading**: Flow loads the correct API key based on model provider
5. **Optional Observability**: Add Logfire token for detailed traces
6. **Managed Infrastructure**: No workers to run or containers to build

## Resources

- [PydanticAI Documentation](https://ai.pydantic.dev)
- [PrefectAgent Guide](https://ai.pydantic.dev/durable_execution/prefect/)
- [Prefect Documentation](https://docs.prefect.io)
- [Prefect MCP Server](https://github.com/PrefectHQ/prefect-mcp-server)
- [Logfire Documentation](https://logfire.pydantic.dev)
