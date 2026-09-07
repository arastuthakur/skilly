"""
Knowledge Graph Markdown Generator for Skilly.
Produces `knowledge_graph.md` containing architectural topology, Mermaid diagrams,
PageRank hub rankings, community clusters, and dependency analysis.
"""

from typing import List
from skilly_core.models import ProjectAnalysisResult


class GraphMarkdownGenerator:
    """Generates knowledge_graph.md from graph analysis results."""

    def generate(self, result: ProjectAnalysisResult) -> str:
        summary = result.summary
        lines: List[str] = []

        lines.append(f"# Knowledge Graph Architecture: {summary.name}\n")
        lines.append("> Structural and semantic topology extracted deterministically via AST and import graphs.\n")

        # Key Metrics
        lines.append("## 📈 Graph Metrics")
        lines.append(f"- **Total Entities (Nodes)**: `{len(result.nodes)}`")
        lines.append(f"- **Total Relationships (Edges)**: `{len(result.edges)}`")
        lines.append(f"- **Architectural Clusters**: `{len(result.clusters)}`")
        lines.append(f"- **Circular Dependency Cycles**: `{len(result.circular_dependencies)}`\n")

        # Circular Dependencies Warning
        if result.circular_dependencies:
            lines.append("### ⚠️ Circular Dependencies Detected")
            lines.append("The following circular reference cycles were identified in the codebase:\n")
            for cycle in result.circular_dependencies:
                cycle_str = " ➔ ".join(f"`{c}`" for c in cycle + [cycle[0]])
                lines.append(f"- {cycle_str}")
            lines.append("")
        else:
            lines.append("**No circular dependency cycles detected.** Codebase dependency graph is acyclic.\n")

        # Architectural Clusters / Subdomains
        lines.append("## Architectural Clusters & Subdomains\n")
        for cluster_name, member_ids in result.clusters.items():
            lines.append(f"### {cluster_name} (`{len(member_ids)}` components)")
            # Sample up to 10 nodes
            sample = [nid.split(":")[-1] for nid in member_ids[:10]]
            lines.append(f"- **Key Components**: {', '.join(f'`{s}`' for s in sample)}")
            if len(member_ids) > 10:
                lines.append(f"- _...and {len(member_ids) - 10} more components_")
            lines.append("")

        # Mermaid High-Level Architecture Diagram
        lines.append("## High-Level Module Architecture Diagram\n")
        lines.append("```mermaid")
        lines.append("graph TD")
        # Build mermaid nodes for top hubs and file/module nodes
        top_node_ids = {n.id for n in result.hubs[:10]}
        rendered_nodes = set()

        for node in result.nodes:
            if node.id in top_node_ids or (node.type.value in ("file", "module") and len(rendered_nodes) < 15):
                safe_id = node.id.replace(":", "_").replace("/", "_").replace(".", "_").replace("-", "_")
                safe_label = node.label.replace('"', "'")
                lines.append(f'    {safe_id}["{safe_label} ({node.type.value})"]')
                rendered_nodes.add(node.id)

        # Edges between rendered nodes
        edge_count = 0
        for edge in result.edges:
            if edge.source in rendered_nodes and edge.target in rendered_nodes:
                src_safe = edge.source.replace(":", "_").replace("/", "_").replace(".", "_").replace("-", "_")
                tgt_safe = edge.target.replace(":", "_").replace("/", "_").replace(".", "_").replace("-", "_")
                lines.append(f'    {src_safe} -->|{edge.type.value}| {tgt_safe}')
                edge_count += 1
                if edge_count >= 25:
                    break
        lines.append("```\n")

        # Top Central Architectural Hubs
        lines.append("## Central Architectural Hubs (PageRank)\n")
        lines.append("| Rank | Symbol / Module | Type | PageRank | In-Degree | Out-Degree | Impact / Blast Radius |")
        lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for idx, hub in enumerate(result.hubs, 1):
            impact = "Critical Choke Point" if hub.in_degree > 3 else "High Importance"
            score_fmt = f"{hub.importance_score:.4f}"
            lines.append(f"| #{idx} | `{hub.label}` | `{hub.type.value}` | `{score_fmt}` | `{hub.in_degree}` | `{hub.out_degree}` | {impact} |")
        lines.append("")

        # Detailed Relationships Breakdown
        lines.append("## Relationship Types Distribution\n")
        edge_types_count = {}
        for e in result.edges:
            t = e.type.value if hasattr(e.type, "value") else str(e.type)
            edge_types_count[t] = edge_types_count.get(t, 0) + 1

        lines.append("| Relationship Type | Count | Description |")
        lines.append("| :--- | :--- | :--- |")
        for et, count in sorted(edge_types_count.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| `{et}` | `{count}` | Inter-component connection |")
        lines.append("")

        lines.append("---\n*Interactive visual graph available in `knowledge_graph.html`*")
        return "\n".join(lines)
