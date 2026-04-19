"""CLI entry point."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        from .server import mcp
        mcp.run(transport="stdio")
    else:
        print("Usage: cerebro-data-engineer serve")
        sys.exit(1)
