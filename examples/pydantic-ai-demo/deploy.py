"""Deploy the PydanticAI demo to Prefect Cloud with managed execution.

This script creates a deployment using Prefect Cloud's managed execution,
which handles all infrastructure automatically - no workers needed!

Before running this script, create the required Prefect resources:

```bash
# Create Prefect variables
prefect variable set fastmcp-server-url "https://your-server.fastmcp.app/mcp"
prefect variable set pydantic-ai-model "anthropic:claude-3-5-sonnet-20241022"

# Create secret blocks for API keys
prefect block register -m prefect.blocks.system

# Using Prefect CLI or Python
from prefect.blocks.system import Secret

# For Anthropic (Claude models)
anthropic_secret = Secret(value="your-anthropic-api-key")
anthropic_secret.save(name="anthropic-api-key")

# For OpenAI models
openai_secret = Secret(value="your-openai-api-key")
openai_secret.save(name="openai-api-key")
```
"""

import asyncio
import sys

from prefect import variables
from prefect.blocks.system import Secret

from demo_flow import run_agent_flow


async def deploy():
    """Deploy the agent flow to Prefect Cloud managed execution."""

    print("🔐 Loading Prefect variables and secrets...")

    # Load FASTMCP server URL from Prefect variable
    try:
        fastmcp_url = await variables.get("fastmcp-server-url")
    except Exception:
        print("❌ Missing required Prefect variable: fastmcp-server-url")
        print("  prefect variable set fastmcp-server-url 'https://your-server.fastmcp.app/mcp'")
        sys.exit(1)

    # Load model from variable (optional, with default)
    model = await variables.get("pydantic-ai-model", default="anthropic:claude-3-5-sonnet-20241022")

    # Try to load API keys from secret blocks
    anthropic_key = None
    openai_key = None

    try:
        anthropic_secret = await Secret.load("anthropic-api-key")
        anthropic_key = anthropic_secret.get()
    except Exception:
        pass

    try:
        openai_secret = await Secret.load("openai-api-key")
        openai_key = openai_secret.get()
    except Exception:
        pass

    if not anthropic_key and not openai_key:
        print("❌ Missing API key secret block. Please create one of:")
        print("  - anthropic-api-key (for Claude models)")
        print("  - openai-api-key (for OpenAI models)")
        print("\nExample:")
        print("  from prefect.blocks.system import Secret")
        print("  secret = Secret(value='your-api-key')")
        print("  secret.save(name='anthropic-api-key')")
        sys.exit(1)

    print(f"✓ Loaded configuration:")
    print(f"  MCP Server: {fastmcp_url}")
    print(f"  Model: {model}")
    print(f"  Anthropic key: {'✓' if anthropic_key else '✗'}")
    print(f"  OpenAI key: {'✓' if openai_key else '✗'}")

    print(f"\n🚀 Deploying to Prefect Cloud with managed execution...")

    # Build environment variables for job
    env_vars = {
        "FASTMCP_SERVER_URL": fastmcp_url,
        "PYDANTIC_AI_MODEL": model,
    }

    # Add the appropriate API key
    if anthropic_key:
        env_vars["ANTHROPIC_API_KEY"] = anthropic_key
    if openai_key:
        env_vars["OPENAI_API_KEY"] = openai_key

    # Deploy the flow with managed execution
    # The work_pool_name="prefect-managed" uses Prefect Cloud's managed infrastructure
    run_agent_flow.deploy(
        name="pydantic-ai-mcp-demo",
        work_pool_name="prefect-managed",
        job_variables={"env": env_vars},
        tags=["pydantic-ai", "mcp", "demo"],
    )

    print(f"\n✅ Deployment created successfully!")
    print(f"\n📊 View in Prefect Cloud:")
    print(f"   https://app.prefect.cloud")
    print(f"\n🎯 Trigger a run:")
    print(f"   prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo'")
    print(f"\n   Or with a custom prompt:")
    print(f"   prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \\")
    print(f"     --param prompt='List my most recent failing flow runs'")
    print(f"\n   Or with a different model:")
    print(f"   prefect deployment run 'pydantic-ai-mcp-demo/pydantic-ai-mcp-demo' \\")
    print(f"     --param model='openai:gpt-4o'")


if __name__ == "__main__":
    run_agent_flow.deploy(
        name="pydantic-ai-mcp-demo",
        work_pool_name="new-managed",
        # job_variables={"env": env_vars},
        tags=["pydantic-ai", "mcp", "demo"],
    )
