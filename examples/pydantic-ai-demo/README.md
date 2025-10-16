# PydanticAI + PrefectAgent + Prefect MCP Demo

A comprehensive demo showcasing [PydanticAI](https://ai.pydantic.dev) with [PrefectAgent](https://ai.pydantic.dev/durable_execution/prefect/) for durable execution, connected to the [Prefect MCP server](https://github.com/PrefectHQ/prefect-mcp-server) via [FastMCP Cloud](https://fastmcp.cloud).

## What This Demonstrates

### PrefectAgent Durability
- **Model requests** tracked as Prefect tasks with automatic retries
- **MCP tool calls** tracked as Prefect tasks with idempotency
- **Task-level observability** in Prefect Cloud UI
- **Managed execution** - no infrastructure to manage

### MCP Integration
- Connect to MCP servers via **streamable HTTP** transport
- Use **Prefect MCP tools** to query and manage Prefect resources
- Real **Prefect-to-Prefect integration** (agent managing Prefect via MCP)

### FastMCP Cloud Deployment
- Deploy MCP server to FastMCP Cloud
- Push updates via git
- View logs in FastMCP Cloud dashboard

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
           │ Streamable HTTP
           │
           ▼
┌─────────────────────┐
│  FastMCP Cloud      │
│                     │
│  ┌───────────────┐  │
│  │ Prefect MCP   │  │
│  │ Server        │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
           │ Prefect API
           │
           ▼
┌─────────────────────┐
│  Prefect Cloud API  │
│  (Your workspace)   │
└─────────────────────┘
```

## Prerequisites

1. **Prefect Cloud account** - [Sign up](https://app.prefect.cloud)
2. **FastMCP Cloud account** - [Sign up](https://fastmcp.cloud)
3. **Model API key** - Choose one:
   - [Anthropic API key](https://console.anthropic.com/) (Claude - default)
   - [OpenAI API key](https://platform.openai.com/api-keys) (GPT models)
4. **Python 3.10+**

## Setup

### 1. Deploy Prefect MCP Server to FastMCP Cloud

First, deploy the Prefect MCP server so your agent can connect to it:

```bash
# Fork the prefect-mcp-server repo
gh repo fork PrefectHQ/prefect-mcp-server

# Go to https://fastmcp.cloud and create a new server:
# - Connect your forked GitHub repo
# - Server path: src/prefect_mcp_server/server.py
# - Requirements: pyproject.toml
# - Environment variables:
#   - PREFECT_API_URL=https://api.prefect.cloud/api/accounts/[ACCOUNT_ID]/workspaces/[WORKSPACE_ID]
#   - PREFECT_API_KEY=pnu_your-prefect-api-key

# Copy your FastMCP server URL for the next step
# Example: https://your-server-name.fastmcp.app/mcp
```

### 2. Install Dependencies

```bash
# Clone this repo if you haven't already
cd examples/pydantic-ai-demo

# Install dependencies
pip install -e .
# or with uv:
uv pip install -e .
```

### 3. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your values:
# - FASTMCP_SERVER_URL: Your FastMCP Cloud URL from step 1
# - ANTHROPIC_API_KEY or OPENAI_API_KEY: Your model provider API key
# - PYDANTIC_AI_MODEL: (optional) Model to use (defaults to Claude 3.5 Sonnet)
# - PREFECT_API_URL: Your Prefect Cloud workspace URL
# - PREFECT_API_KEY: Your Prefect Cloud API key

# Load the environment variables
source .env
```

### 4. Deploy to Prefect Cloud

```bash
# Deploy the agent flow to Prefect Cloud managed execution
python deploy.py
```

This will:
- Create a deployment named `pydantic-ai-mcp-demo`
- Configure it to use Prefect Cloud's managed execution
- Pass all necessary environment variables
- No workers needed - fully managed!

## Usage

### Trigger a Run

```bash
# Run with default prompt (dashboard overview)
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo'

# Run with a custom prompt
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \
  --param prompt='List my most recent failing flow runs and tell me what failed'

# Run with a different model
prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \
  --param model='openai:gpt-4o' \
  --param prompt='Show me the status of my work pools'
```

### Example Prompts

Try these example prompts that leverage the Prefect MCP tools:

```bash
# Dashboard overview
--param prompt='Show me a dashboard overview of my Prefect instance'

# Debug failing runs
--param prompt='List my most recent failing flow runs and tell me what failed'

# Check deployments
--param prompt='Show me all my active deployments'

# Work pool status
--param prompt='Show me the status of my work pools including active workers'

# Debug specific flow run
--param prompt='Help me debug flow run [FLOW_RUN_ID]'

# Check concurrency limits
--param prompt='Are any of my deployments hitting concurrency limits?'
```

### View Results

After triggering a run:

1. **Prefect Cloud UI** - View flow execution, task breakdown, logs:
   ```
   https://app.prefect.cloud
   ```

2. **Flow Run Details** - See:
   - `create-prefect-mcp-agent` task (agent creation)
   - `prefect-assistant_model_request` tasks (LLM calls)
   - `prefect-assistant_mcp_[tool_name]` tasks (MCP tool calls)

3. **Task-Level Observability** - Each task shows:
   - Duration
   - Retries (if any)
   - Logs
   - State history

### Local Testing (Optional)

You can also test locally before deploying:

```bash
# Set environment variables
export FASTMCP_SERVER_URL='https://your-server.fastmcp.app/mcp'
export ANTHROPIC_API_KEY='sk-ant-...'

# Run locally
python demo_flow.py
```

## Updating the MCP Server

When you make changes to the Prefect MCP server:

```bash
# In your forked prefect-mcp-server repo
git add .
git commit -m "Update MCP server"
git push

# FastMCP Cloud will automatically rebuild and deploy your changes
# Your deployed agent will use the updated server on its next run
```

## Observability

### Prefect Cloud UI

View comprehensive flow execution details:
- Flow run duration and state
- Task-level breakdown
- Individual model requests and tool calls
- Logs from each task
- Retry history

### FastMCP Cloud Dashboard

View MCP server logs:
- Tool call requests
- Response times
- Errors and debugging info

## Model Providers

This demo supports multiple AI providers:

### Anthropic (Claude) - Default
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
export PYDANTIC_AI_MODEL='anthropic:claude-3-5-sonnet-20241022'
```

Available models:
- `anthropic:claude-3-5-sonnet-20241022` (recommended)
- `anthropic:claude-3-opus-20240229`
- `anthropic:claude-3-sonnet-20240229`

### OpenAI (GPT)
```bash
export OPENAI_API_KEY='sk-...'
export PYDANTIC_AI_MODEL='openai:gpt-4o'
```

Available models:
- `openai:gpt-4o`
- `openai:gpt-4o-mini`
- `openai:gpt-4-turbo`

## Key Features Demonstrated

### 1. Durable Execution with PrefectAgent
Every operation is tracked as a Prefect task with:
- **Automatic retries** on failures
- **Idempotency** - safe to re-run
- **State tracking** - full execution history
- **Observable** - see exactly what happened

### 2. MCP Integration via Streamable HTTP
Connect to MCP servers over HTTP:
```python
mcp_server = MCPServerStreamableHTTP(mcp_server_url)
agent = Agent(model, toolsets=[mcp_server])
```

### 3. Managed Execution
No infrastructure to manage:
- No workers to run
- No containers to build
- No servers to maintain
- Just deploy and run!

### 4. Multi-Provider Support
Flexible model configuration:
- Use Anthropic Claude
- Use OpenAI GPT
- Switch models per-run
- Easy to add other providers

## Troubleshooting

### "FASTMCP_SERVER_URL environment variable must be set"
Make sure you've:
1. Deployed the Prefect MCP server to FastMCP Cloud
2. Set the `FASTMCP_SERVER_URL` environment variable
3. Loaded the environment variables (`source .env`)

### "Missing API key"
Set either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` depending on which model you want to use.

### "Connection refused" or timeout errors
Check that:
1. Your FastMCP server is running (check FastMCP Cloud dashboard)
2. The URL is correct and includes `/mcp` at the end
3. Your Prefect API credentials in FastMCP are correct

### Agent runs but doesn't use MCP tools
The model might not be choosing to use the tools. Try:
1. More explicit prompts that clearly need Prefect data
2. Different models (some are better at tool use)
3. Check the task logs to see the model's reasoning

## Next Steps

- **Add more MCP servers** - Connect to additional MCP servers for more capabilities
- **Custom tools** - Add your own tools to the agent
- **Scheduled runs** - Set up schedules for regular checks
- **Alerts** - Use Prefect automations to alert on agent failures
- **Custom prompts** - Create domain-specific prompts for your use cases

## Resources

- [PydanticAI Documentation](https://ai.pydantic.dev)
- [PrefectAgent Guide](https://ai.pydantic.dev/durable_execution/prefect/)
- [MCP Client Documentation](https://ai.pydantic.dev/mcp/client/)
- [Prefect Documentation](https://docs.prefect.io)
- [FastMCP Cloud](https://fastmcp.cloud)
- [Prefect MCP Server](https://github.com/PrefectHQ/prefect-mcp-server)
