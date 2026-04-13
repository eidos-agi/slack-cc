"""CLI entry point — serve the MCP server."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        from .server import mcp
        mcp.run(transport="stdio")
    else:
        print("Usage: cerebro-github serve")
        print("  Starts the MCP server on stdio.")
        sys.exit(1)
