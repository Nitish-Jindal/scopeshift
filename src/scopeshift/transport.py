"""Actual two-server MCP sessions with strictly host-bound database locations."""

import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPTransport:
    def __init__(self, database, concurrent_parties=0):
        self.database = str(Path(database).resolve())
        self.concurrent_parties = concurrent_parties
        self.sessions = {}
        self.stack = AsyncExitStack()

    async def __aenter__(self):
        await self.stack.__aenter__()
        try:
            for channel in ("documents", "records"):
                params = StdioServerParameters(
                    command=sys.executable,
                    args=[
                        "-m",
                        "scopeshift.mcp_server",
                        "--database",
                        self.database,
                        "--channel",
                        channel,
                        "--concurrent-parties",
                        str(self.concurrent_parties),
                    ],
                )
                read, write = await self.stack.enter_async_context(stdio_client(params))
                session = await self.stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.sessions[channel] = session
            return self
        except BaseException:
            await self.stack.__aexit__(*sys.exc_info())
            raise

    async def __aexit__(self, *args):
        return await self.stack.__aexit__(*args)

    async def list_tools(self):
        tools = []
        for session in self.sessions.values():
            tools.extend((await session.list_tools()).tools)
        return tools

    async def call(self, action, request_id):
        channel = "documents" if action in ("read_document", "search_documents") else "records"
        result = await self.sessions[channel].call_tool(action, {"request_id": request_id})
        if result.isError:
            raise RuntimeError(f"MCP tool error: {result.content}")
        return json.loads(result.content[0].text)
