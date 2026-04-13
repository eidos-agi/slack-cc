"""Builder documentation — searchable knowledge the agent can query.

Docs live as markdown files in ../docs/ with YAML frontmatter (title, tags).
The docs() tool searches by keyword against titles, tags, and content,
returning the most relevant documents.

This is how the builder "understands" — not through docstrings humans
read, but through knowledge the agent can actually retrieve.
"""

import re
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"


def _parse_doc(path: Path) -> dict:
    """Parse a doc file into title, tags, and content."""
    text = path.read_text()

    title = path.stem.replace("-", " ").title()
    tags = []
    content = text

    # Parse YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2].strip()

            for line in frontmatter.strip().split("\n"):
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("tags:"):
                    # Parse [tag1, tag2, tag3]
                    tag_str = line.split(":", 1)[1].strip()
                    tags = [t.strip().strip("\"'") for t in re.findall(r"[\w-]+", tag_str)]

    return {
        "path": str(path.relative_to(DOCS_DIR)),
        "title": title,
        "tags": tags,
        "content": content,
    }


def _score_doc(doc: dict, query_terms: list[str]) -> int:
    """Score a doc against query terms. Higher = more relevant."""
    score = 0
    title_lower = doc["title"].lower()
    tags_lower = [t.lower() for t in doc["tags"]]
    content_lower = doc["content"].lower()

    for term in query_terms:
        term = term.lower()
        # Title match — strongest signal
        if term in title_lower:
            score += 10
        # Tag match — strong signal
        if term in tags_lower:
            score += 5
        # Content match — weak signal (just proves relevance)
        if term in content_lower:
            score += 1

    return score


def _extract_references(content: str, terms: list[str]) -> list[str]:
    """Pull lines where query terms appear — the back-of-book index."""
    refs = []
    for i, line in enumerate(content.split("\n"), 1):
        line_lower = line.lower().strip()
        if not line_lower or line_lower.startswith("---"):
            continue
        for term in terms:
            if term.lower() in line_lower:
                refs.append(f"L{i}: {line.strip()}")
                break
    return refs[:10]  # cap at 10 references per doc


def search_docs(query: str) -> list[dict]:
    """Search docs by keyword. Returns matching docs sorted by relevance."""
    if not DOCS_DIR.exists():
        return []

    docs = []
    for path in DOCS_DIR.glob("*.md"):
        try:
            docs.append(_parse_doc(path))
        except Exception:
            continue

    if not docs:
        return []

    # Split query into terms
    terms = [t for t in re.split(r"[\s,]+", query.strip()) if t]
    if not terms:
        # No query — return all docs (table of contents)
        return [{"title": d["title"], "path": d["path"], "tags": d["tags"]} for d in docs]

    # Score and rank
    scored = [(doc, _score_doc(doc, terms)) for doc in docs]
    scored = [(doc, s) for doc, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = [
        {
            "title": doc["title"],
            "path": doc["path"],
            "tags": doc["tags"],
            "score": score,
            "references": _extract_references(doc["content"], terms),
            "content": doc["content"],
        }
        for doc, score in scored
    ]

    # Mark surfaced docs as read — the implicit feedback signal.
    # If Ariadne surfaced a doc and the agent later searches for it,
    # that behavioral signal means the nudge worked.
    try:
        from .ariadne import mark_doc_read
        for r in results:
            mark_doc_read(r["title"])
    except ImportError:
        pass

    return results


def list_docs() -> list[dict]:
    """List all available docs (title + tags, no content)."""
    if not DOCS_DIR.exists():
        return []

    docs = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        try:
            doc = _parse_doc(path)
            docs.append({"title": doc["title"], "path": doc["path"], "tags": doc["tags"]})
        except Exception:
            continue
    return docs
