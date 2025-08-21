"""Settings for Prefect MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Prefect MCP server."""
    
    model_config = SettingsConfigDict(env_file=[".env"], extra="ignore")
    
    # Default limits for resources
    deployments_default_limit: int = Field(
        default=100,
        description="Maximum number of deployments to fetch"
    )
    events_default_limit: int = Field(
        default=50,
        description="Maximum number of events to fetch by default"
    )


settings = Settings()