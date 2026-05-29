"""Generate interactive HTML and static image visualizations of reasoning graphs."""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

_TYPE_COLOR = {
    "hypothesis": "#4A90D9",
    "deduction": "#27AE60",
    "backtrack": "#E74C3C",
    "verification": "#F39C12",
    "conclusion": "#8E44AD",
}


class GraphVisualizer:
    def to_html(self, G: nx.DiGraph, output_path: str) -> str:
        """Render an interactive PyVis HTML file. Returns the output path."""
        net = Network(
            height="600px", width="100%", directed=True, notebook=False
        )
        net.barnes_hut()

        for node, data in G.nodes(data=True):
            label = f"Step {data.get('step_id', node)}"
            title = (
                f"<b>{data.get('step_type', '')}</b><br>"
                f"<pre>{data.get('content', '')[:300]}</pre>"
            )
            color = data.get("color", "#95A5A6")
            conf = data.get("confidence", 0.5)
            size = 15 + conf * 25
            net.add_node(node, label=label, title=title, color=color, size=size)

        for src, tgt, data in G.edges(data=True):
            rel = data.get("relation_type", "extends")
            color = data.get("color", "#BDC3C7")
            dashes = data.get("style") == "dashed"
            net.add_edge(
                src, tgt, label=rel, color=color, dashes=dashes, arrows="to"
            )

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        net.save_graph(output_path)
        return output_path

    def to_image(self, G: nx.DiGraph, output_path: str) -> str:
        """Render a static matplotlib image. Returns the output path."""
        fig, ax = plt.subplots(figsize=(14, 8))

        if G.number_of_nodes() == 0:
            ax.text(0.5, 0.5, "Empty graph", ha="center", va="center")
            fig.savefig(output_path, bbox_inches="tight", dpi=150)
            plt.close(fig)
            return output_path

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            pos = nx.spring_layout(G, seed=42)

        node_colors = [G.nodes[n].get("color", "#95A5A6") for n in G.nodes]
        sizes = [200 + G.nodes[n].get("confidence", 0.5) * 400 for n in G.nodes]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=sizes, ax=ax)
        nx.draw_networkx_labels(
            G, pos, labels={n: str(n) for n in G.nodes}, font_size=8, ax=ax
        )

        solid_edges = [
            (u, v) for u, v, d in G.edges(data=True) if d.get("style") != "dashed"
        ]
        dashed_edges = [
            (u, v) for u, v, d in G.edges(data=True) if d.get("style") == "dashed"
        ]

        if solid_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=solid_edges, edge_color="#BDC3C7", ax=ax
            )
        if dashed_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=dashed_edges, style="dashed", edge_color="#E74C3C", ax=ax
            )

        import matplotlib.patches as mpatches

        legend_handles = [
            mpatches.Patch(color=c, label=t) for t, c in _TYPE_COLOR.items()
        ]
        ax.legend(handles=legend_handles, loc="upper right", fontsize=8)
        ax.set_title("Reasoning Trace Graph", fontsize=14)
        ax.axis("off")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        return output_path
