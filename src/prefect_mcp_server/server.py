"""Prefect MCP Server - Clean implementation following FastMCP patterns."""

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from prefect_mcp_server import _prefect_client
from prefect_mcp_server.settings import settings
from prefect_mcp_server.types import (
    DeploymentsResult,
    EventsResult,
    RunDeploymentResult,
)

mcp = FastMCP("Prefect MCP Server")


# Resources - read-only operations
@mcp.resource("prefect://deployments/list")
async def list_deployments() -> DeploymentsResult:
    """List all deployments in the Prefect instance.
    
    Returns deployment information including name, flow name, schedule, and tags.
    """
    return await _prefect_client.fetch_deployments()


@mcp.resource("prefect://events/recent") 
async def get_recent_events() -> EventsResult:
    """Get recent events from the Prefect instance.
    
    Returns recent events as a snapshot in time. This is a read-only
    operation that queries the Prefect events API.
    """
    return await _prefect_client.fetch_events(
        limit=settings.events_default_limit
    )


# Tools - actions that modify state
@mcp.tool
async def run_deployment_by_name(
    flow_name: Annotated[
        str, 
        Field(description="The name of the flow")
    ],
    deployment_name: Annotated[
        str,
        Field(description="The name of the deployment")
    ],
    parameters: Annotated[
        dict[str, Any] | None,
        Field(description="Optional parameter overrides for the flow run")
    ] = None,
    name: Annotated[
        str | None,
        Field(description="Optional custom name for the flow run")
    ] = None,
    tags: Annotated[
        list[str] | None,
        Field(description="Optional tags to add to the flow run")
    ] = None,
) -> RunDeploymentResult:
    """Run a deployment by its flow and deployment names.
    
    Examples:
        - Simple run: run_deployment_by_name("my-flow", "production")
        - With parameters: run_deployment_by_name("etl-flow", "daily", parameters={"date": "2024-01-01"})
    """
    return await _prefect_client.run_deployment_by_name(
        flow_name=flow_name,
        deployment_name=deployment_name,
        parameters=parameters,
        name=name,
        tags=tags,
    )


