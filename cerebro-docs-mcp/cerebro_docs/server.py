"""cerebro-docs — the Cerebro ecosystem map.

Progressive reveal: agents start here to learn which MCP to use,
how they work together, and how to accomplish specific workflows.

Level 0: overview()     — routing table, one line per MCP
Level 1: explain(name)  — deep dive on one MCP
Level 2: workflow(name) — multi-MCP workflow guide
Level 3: route(task)    — "I want to do X" → which MCP + tool
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "cerebro-docs",
    instructions=(
        "cerebro-docs is the ecosystem map for all Cerebro MCPs. "
        "Start here when you don't know which MCP to use. "
        "Use `overview` for a quick routing table, "
        "`explain` for a deep dive on one MCP, "
        "`workflow` for multi-MCP workflow guides, "
        "`route` to find the right tool for a task."
    ),
)


@mcp.tool()
def overview() -> dict:
    """Quick map of every Cerebro MCP — one line each.

    Start here. This tells you which MCP answers which question.
    """
    from .knowledge import ALL_MCPS

    return {
        "ecosystem": "Cerebro MCP",
        "count": len(ALL_MCPS),
        "mcps": {
            name: {
                "purpose": m.purpose,
                "question": m.question,
                "tool_count": len(m.tools),
            }
            for name, m in ALL_MCPS.items()
        },
        "hint": "Use explain('<name>') for tool details, workflow('<name>') for multi-MCP patterns, route('<task>') to find the right tool.",
    }


@mcp.tool()
def explain(name: str) -> dict:
    """Deep dive on one MCP — every tool, what it depends on, when to use it.

    Args:
        name: MCP name (e.g. "cerebro-verifier", "cerebro-web-builder")
    """
    from .knowledge import ALL_MCPS

    m = ALL_MCPS.get(name)
    if not m:
        return {
            "error": f"Unknown MCP: {name}",
            "available": list(ALL_MCPS.keys()),
        }

    return {
        "name": m.name,
        "purpose": m.purpose,
        "question": m.question,
        "tools": [
            {
                "name": t.name,
                "summary": t.summary,
                **({"args": t.args} if t.args else {}),
                **({"example": t.example} if t.example else {}),
            }
            for t in m.tools
        ],
        "depends_on": m.depends_on,
        "tool_count": len(m.tools),
    }


@mcp.tool()
def workflow(name: str = "") -> dict:
    """Multi-MCP workflow guide — which MCPs to call in what order.

    Without a name, lists all workflows. With a name, shows the full flow.

    Args:
        name: Workflow name (e.g. "ship_to_staging", "verify_data_correctness")
    """
    from .knowledge import WORKFLOWS

    if not name.strip():
        return {
            "workflows": {
                k: v["summary"] for k, v in WORKFLOWS.items()
            },
            "hint": "Use workflow('<name>') for the full step-by-step flow.",
        }

    wf = WORKFLOWS.get(name)
    if not wf:
        return {
            "error": f"Unknown workflow: {name}",
            "available": list(WORKFLOWS.keys()),
        }

    result = {
        "name": name,
        "summary": wf["summary"],
        "mcps_involved": wf["mcps"],
        "steps": wf["flow"],
    }

    if "example" in wf:
        result["example"] = wf["example"]

    return result


@mcp.tool()
def route(task: str) -> dict:
    """Find the right MCP and tool for a task.

    Describe what you want to do in plain language.

    Args:
        task: What you want to accomplish (e.g. "check if revenue numbers are correct")
    """
    from .knowledge import ALL_MCPS, ROUTING_TABLE

    task_lower = task.lower()

    # Check routing table for keyword matches
    matches = []
    for keyword, mcp_name in ROUTING_TABLE.items():
        if keyword in task_lower:
            matches.append(mcp_name)

    if matches:
        # Deduplicate, preserve order
        seen = set()
        unique = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                unique.append(m)

        results = []
        for mcp_name in unique:
            m = ALL_MCPS[mcp_name]
            # Find relevant tools
            relevant_tools = []
            for t in m.tools:
                if any(
                    word in t.summary.lower() or word in t.name.lower()
                    for word in task_lower.split()
                ):
                    relevant_tools.append({"name": t.name, "summary": t.summary})

            results.append({
                "mcp": mcp_name,
                "purpose": m.purpose,
                "relevant_tools": relevant_tools or [{"name": t.name, "summary": t.summary} for t in m.tools[:3]],
            })

        return {"task": task, "recommendations": results}

    # No keyword match — return overview
    return {
        "task": task,
        "recommendations": [],
        "hint": "No direct match. Here's the full ecosystem:",
        "mcps": {
            name: m.question for name, m in ALL_MCPS.items()
        },
    }
