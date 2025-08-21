"""Type definitions for Prefect MCP server."""

from typing import Any, TypedDict


class DeploymentInfo(TypedDict):
    """Information about a single deployment."""
    
    id: str
    name: str
    description: str | None
    tags: list[str]
    flow_name: str | None
    is_schedule_active: bool | None
    created: str | None
    updated: str | None
    schedules: list[dict[str, Any]] | None


class DeploymentsResult(TypedDict):
    """Result of listing deployments."""
    
    success: bool
    count: int
    deployments: list[DeploymentInfo]
    error: str | None


class EventsResult(TypedDict):
    """Result of reading events."""
    
    success: bool
    count: int
    events: list[dict[str, Any]]  # Raw event objects from the API
    error: str | None
    total: int  # Total number of events available


class FlowRunInfo(TypedDict):
    """Information about a flow run."""
    
    id: str
    name: str | None
    deployment_id: str | None
    flow_id: str | None
    state: dict[str, Any] | None
    created: str | None
    tags: list[str] | None
    parameters: dict[str, Any] | None


class RunDeploymentResult(TypedDict):
    """Result of running a deployment."""
    
    success: bool
    flow_run: FlowRunInfo | None
    deployment: dict[str, Any] | None
    error: str | None
    error_type: str | None