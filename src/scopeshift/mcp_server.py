"""Two scoped official-SDK stdio servers. No paths or identities in tool arguments."""

import argparse
import asyncio
import threading

from mcp.server.fastmcp import FastMCP

from scopeshift.effects import execute
from scopeshift.storage import Store


def create_server(database: str, channel: str, concurrent_parties=0) -> FastMCP:
    server = FastMCP(f"scopeshift-{channel}")
    store = Store(database)
    gate = threading.Barrier(concurrent_parties) if concurrent_parties else None
    actions = (
        ("read_document", "search_documents")
        if channel == "documents"
        else ("get_record", "update_record", "send_message")
    )

    def add(action):
        async def invoke(request_id: str) -> dict:
            """Execute a host-registered, authorized request in this run only."""
            return await asyncio.to_thread(execute, store, request_id, action, gate)

        server.tool(name=action)(invoke)

    for action in actions:
        add(action)
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--channel", choices=["documents", "records"], required=True)
    parser.add_argument("--concurrent-parties", type=int, choices=[0, 2], default=0)
    args = parser.parse_args()
    create_server(args.database, args.channel, args.concurrent_parties).run(transport="stdio")


if __name__ == "__main__":
    main()
