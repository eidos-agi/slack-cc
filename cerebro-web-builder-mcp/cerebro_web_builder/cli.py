"""CLI entry point — cerebro-web-builder serve."""

import sys


def main():
    # Accept `serve` as a subcommand (ignored — always serves)
    args = sys.argv[1:]
    if args and args[0] not in ("serve",):
        print(f"Usage: cerebro-web-builder serve", file=sys.stderr)
        sys.exit(1)

    from .server import mcp
    mcp.run()


if __name__ == "__main__":
    main()
