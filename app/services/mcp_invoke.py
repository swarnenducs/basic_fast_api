"""Generic FastMCP client invoke. Connection details come from config."""

from typing import Any

from fastmcp import Client

from app.core.config import settings


class MCPInvoke:
    def __init__(self):
        self.endpoint = settings.mcp_endpoint
        self.transport = settings.mcp_transport
        self.server_name = settings.mcp_server_name
        self.tool_name = settings.mcp_tool_name
        self.timeout_seconds = float(settings.mcp_timeout_seconds)

    async def invoke_mcp(
        self,
        tool_name: str | None = None,
        arguments: dict[str, Any] | None = None,
        resource_uri: str | None = None,
    ) -> Any:
        """Generic FastMCP invoke.

        Reads endpoint, transport, default tool, and timeout from config.
        - tool_name / arguments: call_tool
        - resource_uri: read_resource
        - neither: list_tools
        Skips the network call when MCP_ENDPOINT is empty.
        """
        if not self.endpoint:
            return None

        name = tool_name or self.tool_name
        args = arguments or {}

        try:
            async with Client(
                self.endpoint,
                timeout=self.timeout_seconds,
                init_timeout=min(5.0, self.timeout_seconds),
            ) as client:
                if resource_uri:
                    return await client.read_resource(resource_uri)
                if name:
                    result = await client.call_tool(
                        name, args, timeout=self.timeout_seconds
                    )
                    return getattr(result, "data", result)
                tools = await client.list_tools()
                return [getattr(tool, "name", str(tool)) for tool in tools]
        except Exception:
            return None
