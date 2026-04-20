"""CLI entry point — cerebro-docs serve."""

import sys


def main():
    args = sys.argv[1:]
    if args and args[0] not in ("serve",):
        print("Usage: cerebro-docs serve", file=sys.stderr)
        sys.exit(1)

    from .server import mcp
    mcp.run()


if __name__ == "__main__":
    main()
