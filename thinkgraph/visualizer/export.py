"""Export reasoning graphs to plain-text formats: DOT, Mermaid, JSON.

Unlike the HTML/image renderers next door, these exports carry no heavy
dependencies (networkx + stdlib only), so they run anywhere — CI, notebooks,
docs generation. Mermaid output is designed to be pasted straight into a
Markdown file; DOT feeds GraphViz; JSON keeps every attribute untouched
for downstream tooling.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

import networkx as nx

# Fill colors per step type, kept in sync with _TYPE_COLOR in graph_viz.py.
_TYPE_FILL = {
    "hypothesis": "#4A90D9",
    "deduction": "#27AE60",
    "backtrack": "#E74C3C",
    "verification": "#F39C12",
    "conclusion": "#8E44AD",
}
_DEFAULT_FILL = "#95A5A6"

_LABEL_MAX = 48

# Characters that break Mermaid label syntax or DOT quoting are dropped,
# not escaped — these are display labels; to_json keeps the raw content.
_UNSAFE_LABEL_CHARS = re.compile(r'["<>\[\]|`\\{}]')


def _safe_label(text: Any, limit: int = _LABEL_MAX) -> str:
    cleaned = _UNSAFE_LABEL_CHARS.sub(" ", str(text))
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit]


def _node_label(node: Any, data: Dict[str, Any]) -> str:
    sid = data.get("step_id", node)
    stype = data.get("step_type", "deduction")
    conf = data.get("confidence")
    label = f"Step {sid} · {stype}"
    if conf is not None:
        label += f" · {conf:.2f}"
    return _safe_label(label)


def _write(path: Optional[str], text: str) -> None:
    if path is not None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def to_dot(G: nx.DiGraph, path: Optional[str] = None) -> str:
    """Serialize the graph in GraphViz DOT. Returns the DOT text."""
    lines = ["strict digraph reasoning {"]
    for node, data in G.nodes(data=True):
        stype = data.get("step_type", "deduction")
        fill = _TYPE_FILL.get(stype, _DEFAULT_FILL)
        lines.append(
            f'    "{node}" [label="{_node_label(node, data)}", '
            f'fillcolor="{fill}", style="filled"];'
        )
    for src, tgt, data in G.edges(data=True):
        rel = _safe_label(data.get("relation_type", "extends"), 20)
        lines.append(f'    "{src}" -> "{tgt}" [label="{rel}"];')
    lines.append("}")
    dot = "\n".join(lines) + "\n"
    _write(path, dot)
    return dot


def to_mermaid(G: nx.DiGraph, path: Optional[str] = None) -> str:
    """Serialize the graph as a Mermaid flowchart. Returns the Mermaid text.

    Node ids are prefixed with ``n`` because Mermaid ids must be plain
    identifiers while step ids may be anything.
    """
    lines = ["flowchart TD"]
    for node, data in G.nodes(data=True):
        stype = data.get("step_type", "deduction")
        lines.append(f'    n{node}["{_node_label(node, data)}"]:::{stype}')
    for src, tgt, data in G.edges(data=True):
        rel = _safe_label(data.get("relation_type", "extends"), 20)
        lines.append(f"    n{src} -->|{rel}| n{tgt}")
    for stype, fill in _TYPE_FILL.items():
        if any(d.get("step_type") == stype for _, d in G.nodes(data=True)):
            lines.append(f"    classDef {stype} fill:{fill},stroke:#333,color:#fff;")
    mermaid = "\n".join(lines) + "\n"
    _write(path, mermaid)
    return mermaid


def to_json(G: nx.DiGraph, path: Optional[str] = None) -> str:
    """Serialize every node/edge attribute verbatim. Returns the JSON text."""
    payload: Dict[str, Any] = {
        "directed": G.is_directed(),
        "multigraph": G.is_multigraph(),
        "nodes": [
            {"id": node, **{k: v for k, v in data.items()}}
            for node, data in G.nodes(data=True)
        ],
        "edges": [
            {"source": src, "target": tgt, **{k: v for k, v in data.items()}}
            for src, tgt, data in G.edges(data=True)
        ],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    _write(path, text)
    return text
