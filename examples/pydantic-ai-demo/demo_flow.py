"""Demo of PydanticAI with PrefectAgent and MCP integration.

This demo showcases:
- PydanticAI agent with PrefectAgent wrapper for durability
- Connection to Prefect MCP server via streamable HTTP (FastMCP Cloud)
- Automatic task-level instrumentation in Prefect Cloud
- Model requests and tool calls tracked as Prefect tasks
"""

import os
from typing import Annotated

from prefect import flow, task, variables
from prefect.blocks.system import Secret
from pydantic import Field
from pydantic_ai import Agent
from pydantic_ai.durable_exec.prefect import PrefectAgent
from pydantic_ai.mcp import MCPServerStreamableHTTP


# Example prompts that use Prefect MCP tools
EXAMPLE_PROMPTS = {
    "dashboard": "Show me a dashboard overview of my Prefect instance",
    "failing_runs": "List my most recent failing flow runs and tell me what failed",
    "deployments": "Show me all my active deployments",
    "debug": "Help me debug the most recent failed flow run",
    "work_pools": "Show me the status of my work pools including active workers",
}


@task(name="create-agent", task_run_name="create-prefect-mcp-agent")
async def create_agent(mcp_server_url: str, model: str) -> PrefectAgent:
    """Create a PydanticAI agent with Prefect MCP server connection.

    Args:
        mcp_server_url: URL of the Prefect MCP server on FastMCP Cloud
        model: Model identifier (e.g., 'anthropic:claude-3-5-sonnet-20241022', 'openai:gpt-4o')

    Returns:
        PrefectAgent wrapping the configured agent
    """
    # Load API key from secret block and set in environment
    # PydanticAI looks for API keys in environment variables
    if model.startswith("anthropic:"):
        try:
            secret = await Secret.load("anthropic-api-key")
            api_key = secret.get()
            os.environ["ANTHROPIC_API_KEY"] = api_key
            print("✓ Loaded Anthropic API key from secret block")
        except Exception as e:
            raise ValueError(f"Failed to load anthropic-api-key secret: {e}")
    elif model.startswith("openai:"):
        try:
            secret = await Secret.load("openai-api-key")
            api_key = secret.get()
            os.environ["OPENAI_API_KEY"] = api_key
            print("✓ Loaded OpenAI API key from secret block")
        except Exception as e:
            raise ValueError(f"Failed to load openai-api-key secret: {e}")
    else:
        raise ValueError(f"Unsupported model provider: {model}")

    # Connect to Prefect MCP server via streamable HTTP
    mcp_server = MCPServerStreamableHTTP(mcp_server_url)

    # Create PydanticAI agent with instructions
    agent = Agent(
        model,
        name="prefect-assistant",
        instructions="""You are a helpful assistant for managing Prefect workflows.

You have access to Prefect MCP tools that let you:
- View dashboard overviews (flow runs, work pools, concurrency limits)
- Query deployments, flow runs, task runs, and work pools
- Retrieve detailed execution logs
- Debug failed runs and deployment issues
- Track events across the workflow ecosystem

Always provide clear, actionable insights when analyzing Prefect data.
When debugging failures, look at logs and task run details to identify root causes.
""",
        toolsets=[mcp_server],
    )

    # Wrap with PrefectAgent for durability and observability
    # This makes model requests and tool calls visible as Prefect tasks
    prefect_agent = PrefectAgent(agent)

    return prefect_agent


@flow(
    name="pydantic-ai-mcp-demo",
    description="Demo of PydanticAI agent with Prefect MCP integration",
    log_prints=True,
)
async def run_agent_flow(
    prompt: Annotated[
        str,
        Field(
            description="The prompt to send to the agent",
            examples=list(EXAMPLE_PROMPTS.values()),
        ),
    ] = EXAMPLE_PROMPTS["dashboard"],
    mcp_server_url: Annotated[
        str | None,
        Field(
            description="URL of Prefect MCP server on FastMCP Cloud",
            examples=["https://your-server.fastmcp.app/mcp"],
        ),
    ] = None,
    model: Annotated[
        str | None,
        Field(
            description="Model identifier (provider:model-name)",
            examples=[
                "anthropic:claude-3-5-sonnet-20241022",
                "openai:gpt-4o",
                "openai:gpt-4o-mini",
            ],
        ),
    ] = None,
) -> str:
    """Run the PydanticAI agent with a prompt.

    This flow demonstrates PrefectAgent's durability features:
    - Model requests are tracked as Prefect tasks
    - MCP tool calls are tracked as Prefect tasks
    - Retries and idempotency built-in
    - Full observability in Prefect Cloud UI

    Args:
        prompt: The question/instruction to send to the agent
        mcp_server_url: URL of the Prefect MCP server (defaults to Prefect variable)
        model: Model identifier (defaults to Prefect variable or anthropic:claude-3-5-sonnet-20241022)

    Returns:
        The agent's response
    """
    # Configure Logfire if token is available
    try:
        import logfire

        logfire_secret = await Secret.load("logfire-token")
        logfire_token = logfire_secret.get()
        logfire.configure(token=logfire_token)
        print("✓ Configured Logfire observability")
    except Exception as e:
        print(f"ℹ️  Logfire not configured: {e}")

    # Get MCP server URL from parameter or Prefect variable
    if mcp_server_url:
        server_url = mcp_server_url
    else:
        server_url = await variables.get("fastmcp-server-url", default=None)
        if not server_url:
            raise ValueError(
                "MCP server URL must be provided as parameter or set as Prefect variable 'fastmcp-server-url'"
            )

    # Get model from parameter or Prefect variable, with sensible default
    if model:
        model_name = model
    else:
        model_name = await variables.get("pydantic-ai-model", default="anthropic:claude-3-5-sonnet-20241022")

    print(f"🤖 Creating agent connected to: {server_url}")
    print(f"🧠 Using model: {model_name}")

    # Create the agent (as a tracked task)
    prefect_agent = await create_agent(server_url, model_name)

    print(f"💬 Running prompt: {prompt}")

    # Run the agent - this will create tasks for:
    # - Model request(s)
    # - MCP tool call(s)
    # Each is retryable and independently tracked
    async with prefect_agent:
        result = await prefect_agent.run(prompt)

    response = result.output
    print(f"✅ Agent response:\n{response}")

    return response


# Example usage for local testing
if __name__ == "__main__":
    import asyncio

    # For local testing, you can run different example prompts
    prompt = EXAMPLE_PROMPTS["dashboard"]

    # Run the flow
    asyncio.run(run_agent_flow(prompt=prompt))
