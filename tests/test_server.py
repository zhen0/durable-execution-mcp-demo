"""Tests for Prefect MCP server."""

import json
from uuid import UUID

from fastmcp import FastMCP
from fastmcp.client import Client
from prefect.client.orchestration import PrefectClient


async def test_server_has_expected_capabilities(prefect_mcp_server: FastMCP) -> None:
    """Test that the server exposes expected MCP capabilities."""
    async with Client(prefect_mcp_server) as client:
        resources = await client.list_resources()
        resource_uris = [str(r.uri) for r in resources]
        assert "prefect://deployments/list" in resource_uris
        assert "prefect://events/recent" in resource_uris
        assert len(resources) == 2

        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert "run_deployment" in tool_names
        assert "run_deployment_by_name" in tool_names
        assert "read_events" in tool_names
        assert len(tools) == 3


async def test_list_deployments_with_test_data(
    prefect_mcp_server: FastMCP, 
    prefect_client: PrefectClient, 
    test_flow: UUID
) -> None:
    """Test listing deployments returns the deployments we create."""
    deployment_ids = []
    for i in range(3):
        deployment_id = await prefect_client.create_deployment(
            flow_id=test_flow,
            name=f"test-deployment-{i}",
            description=f"Test deployment {i}",
            tags=["test", f"deployment-{i}"],
        )
        deployment_ids.append(deployment_id)

    async with Client(prefect_mcp_server) as client:
        result = await client.read_resource("prefect://deployments/list")

        assert isinstance(result, list)
        assert len(result) == 1
        content = result[0]
        data = json.loads(content.text)

        assert data["success"] is True
        assert data["count"] == 3
        assert len(data["deployments"]) == 3

        deployment_names = [d["name"] for d in data["deployments"]]
        assert "test-deployment-0" in deployment_names
        assert "test-deployment-1" in deployment_names
        assert "test-deployment-2" in deployment_names


async def test_run_deployment_with_valid_id(
    prefect_mcp_server: FastMCP,
    prefect_client: PrefectClient,
    test_flow: UUID
) -> None:
    """Test running a deployment with a valid ID."""
    deployment_id = await prefect_client.create_deployment(
        flow_id=test_flow,
        name="test-deployment",
        description="A test deployment",
        tags=["test"],
    )
    deployment = await prefect_client.read_deployment(deployment_id)

    async with Client(prefect_mcp_server) as client:
        result = await client.call_tool(
            "run_deployment", {"deployment_id": str(deployment.id)}
        )

        assert hasattr(result, "structured_content")
        data = result.structured_content

        assert data["success"] is True
        assert "flow_run" in data
        assert data["flow_run"]["deployment_id"] == str(deployment.id)


async def test_run_deployment_by_name(
    prefect_mcp_server: FastMCP,
    prefect_client: PrefectClient,
    test_flow: UUID
) -> None:
    """Test running a deployment by flow and deployment names."""
    await prefect_client.create_deployment(
        flow_id=test_flow,
        name="test-deployment",
        description="A test deployment",
        tags=["test"],
    )

    async with Client(prefect_mcp_server) as client:
        result = await client.call_tool(
            "run_deployment_by_name",
            {"flow_name": "test-flow", "deployment_name": "test-deployment"},
        )

        assert hasattr(result, "structured_content")
        data = result.structured_content

        assert data["success"] is True
        assert "flow_run" in data
        assert "deployment" in data
        assert data["deployment"]["name"] == "test-deployment"


async def test_run_deployment_with_parameters(
    prefect_mcp_server: FastMCP,
    prefect_client: PrefectClient,
    test_flow: UUID
) -> None:
    """Test running a deployment with parameter overrides."""
    deployment_id = await prefect_client.create_deployment(
        flow_id=test_flow,
        name="param-test-deployment",
        parameters={"x": 42, "y": "default"},
    )
    deployment = await prefect_client.read_deployment(deployment_id)

    async with Client(prefect_mcp_server) as client:
        custom_params = {"x": 99, "y": "custom"}

        result = await client.call_tool(
            "run_deployment",
            {
                "deployment_id": str(deployment.id),
                "parameters": custom_params,
                "name": "Custom test run",
                "tags": ["test-run", "mcp"],
            },
        )

        assert hasattr(result, "structured_content")
        data = result.structured_content

        assert data["success"] is True
        assert data["flow_run"]["parameters"] == custom_params
        assert data["flow_run"]["name"] == "Custom test run"
        assert "test-run" in data["flow_run"]["tags"]


async def test_run_nonexistent_deployment(prefect_mcp_server: FastMCP) -> None:
    """Test error handling when running a non-existent deployment."""
    async with Client(prefect_mcp_server) as client:
        result = await client.call_tool(
            "run_deployment", {"deployment_id": "00000000-0000-0000-0000-000000000000"}
        )

        assert hasattr(result, "structured_content")
        data = result.structured_content

        assert data["success"] is False
        assert "error" in data
        assert data["error"] is not None


async def test_events_resource_structure(prefect_mcp_server: FastMCP) -> None:
    """Test the events resource returns expected structure (without hanging)."""
    async with Client(prefect_mcp_server) as client:
        resources = await client.list_resources()
        events_resource = next(
            (r for r in resources if str(r.uri) == "prefect://events/recent"), None
        )

        assert events_resource is not None
        assert events_resource.name == "get_recent_events"
        assert events_resource.description


async def test_read_events_tool_structure(prefect_mcp_server: FastMCP) -> None:
    """Test the read_events tool exists with correct parameters."""
    async with Client(prefect_mcp_server) as client:
        tools = await client.list_tools()
        read_events = next((t for t in tools if t.name == "read_events"), None)

        assert read_events is not None
        assert read_events.description

        # Input schema contains expected parameters
        schema_str = str(read_events.inputSchema)
        assert "limit" in schema_str
        assert "event_prefix" in schema_str