"""
Knowledge Graph Engine for Skilly.
Builds directed graph, computes PageRank, centrality, architectural clusters,
detects circular dependencies, and formats graph output for visualization.
Uses NetworkX with deterministic pure-Python algorithms.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple
import networkx as nx
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType


class KnowledgeGraphEngine:
    """Constructs and analyzes the project knowledge graph."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes_by_id: Dict[str, GraphNode] = {}
        self.edges_list: List[GraphEdge] = []

    def build_graph(
        self, nodes: List[GraphNode], edges: List[GraphEdge]
    ) -> Tuple[List[GraphNode], List[GraphEdge], Dict[str, List[str]], List[GraphNode], List[List[str]]]:
        """
        Builds the graph, calculates PageRank and metrics, clusters nodes,
        and identifies architectural hubs and circular dependencies.
        """
        # Deduplicate and register nodes
        for node in nodes:
            if node.id not in self.nodes_by_id:
                self.nodes_by_id[node.id] = node
                self.graph.add_node(
                    node.id,
                    label=node.label,
                    type=node.type.value if isinstance(node.type, NodeType) else str(node.type),
                    file_path=node.file_path,
                )
            else:
                # Merge descriptions if richer
                existing = self.nodes_by_id[node.id]
                if node.description and (not existing.description or len(node.description) > len(existing.description)):
                    existing.description = node.description

        # Deduplicate and register edges
        edge_seen: Set[Tuple[str, str, str]] = set()
        cleaned_edges: List[GraphEdge] = []

        for edge in edges:
            key = (edge.source, edge.target, edge.type.value if isinstance(edge.type, EdgeType) else str(edge.type))
            if key in edge_seen:
                continue
            edge_seen.add(key)

            # Ensure source and target exist as nodes
            if edge.source not in self.nodes_by_id:
                placeholder = GraphNode(id=edge.source, label=edge.source.split("/")[-1], type=NodeType.MODULE)
                self.nodes_by_id[edge.source] = placeholder
                self.graph.add_node(edge.source, label=placeholder.label, type=str(placeholder.type))

            if edge.target not in self.nodes_by_id:
                target_type = NodeType.DEPENDENCY if edge.target.startswith("dep:") else NodeType.MODULE
                target_label = edge.target.removeprefix("dep:").removeprefix("class:").split("/")[-1]
                placeholder = GraphNode(id=edge.target, label=target_label, type=target_type)
                self.nodes_by_id[edge.target] = placeholder
                self.graph.add_node(edge.target, label=placeholder.label, type=str(placeholder.type))

            self.graph.add_edge(edge.source, edge.target, type=key[2], weight=edge.weight)
            cleaned_edges.append(edge)

        self.edges_list = cleaned_edges

        # 1. Compute PageRank
        try:
            if len(self.graph) > 0:
                pagerank = nx.pagerank(self.graph, alpha=0.85, max_iter=100)
            else:
                pagerank = {}
        except Exception:
            pagerank = {n: 1.0 / max(1, len(self.graph)) for n in self.graph.nodes}

        # 2. Update node metrics
        for n_id, node in self.nodes_by_id.items():
            node.importance_score = pagerank.get(n_id, 0.0)
            node.in_degree = self.graph.in_degree(n_id) if self.graph.has_node(n_id) else 0
            node.out_degree = self.graph.out_degree(n_id) if self.graph.has_node(n_id) else 0

        # 3. Community / Cluster Detection
        clusters = self._detect_clusters()
        for cluster_name, node_ids in clusters.items():
            for nid in node_ids:
                if nid in self.nodes_by_id:
                    self.nodes_by_id[nid].cluster = cluster_name

        # 4. Identify Top Architectural Hubs (nodes with highest PageRank & degrees)
        sorted_nodes = sorted(
            self.nodes_by_id.values(),
            key=lambda x: (x.importance_score, x.in_degree + x.out_degree),
            reverse=True,
        )
        hubs = [n for n in sorted_nodes if n.type not in (NodeType.DEPENDENCY, NodeType.CONFIG)][:15]

        # 5. Detect Circular Dependencies (cycles in graph)
        circular_deps = self._detect_cycles()

        return list(self.nodes_by_id.values()), cleaned_edges, clusters, hubs, circular_deps

    def _detect_clusters(self) -> Dict[str, List[str]]:
        """Group nodes into architectural clusters based on graph topology and directory semantics."""
        clusters: Dict[str, List[str]] = defaultdict(list)

        # Try community detection on undirected projection
        try:
            undirected = self.graph.to_undirected()
            communities = nx.community.greedy_modularity_communities(undirected)
            for idx, comm in enumerate(communities):
                comm_name = f"Cluster {idx + 1}"
                # Derive meaningful cluster label from predominant directory or type
                paths = [self.nodes_by_id[nid].file_path for nid in comm if self.nodes_by_id[nid].file_path]
                if paths:
                    dir_counts = defaultdict(int)
                    for p in paths:
                        first_dir = p.split("/")[0] if "/" in p else "root"
                        dir_counts[first_dir] += 1
                    top_dir = max(dir_counts.items(), key=lambda x: x[1])[0]
                    comm_name = f"{top_dir.capitalize()} Domain"
                for nid in comm:
                    clusters[comm_name].append(nid)
            return dict(clusters)
        except Exception:
            pass

        # Fallback: cluster by top-level directory or node category
        for nid, node in self.nodes_by_id.items():
            if node.file_path:
                first_dir = node.file_path.split("/")[0] if "/" in node.file_path else "core"
                clusters[f"{first_dir.capitalize()} Module"].append(nid)
            elif node.type == NodeType.DEPENDENCY:
                clusters["External Dependencies"].append(nid)
            elif node.type == NodeType.CONFIG:
                clusters["Configurations"].append(nid)
            else:
                clusters["System Core"].append(nid)

        return dict(clusters)

    def _detect_cycles(self) -> List[List[str]]:
        """Find circular dependencies among files and modules using Tarjan SCC partitioning."""
        cycles = []
        try:
            # Build file/module level dependency subgraph to avoid false positives on intra-file calls
            file_nodes = {
                n for n, d in self.graph.nodes(data=True)
                if n.startswith("file:") or d.get("type") in ("file", "module")
            }
            subgraph = self.graph.subgraph(file_nodes) if file_nodes else self.graph

            # Find strongly connected components with > 1 node (Tarjan's algorithm O(V+E))
            sccs = [scc for scc in nx.strongly_connected_components(subgraph) if len(scc) > 1]
            for scc in sccs:
                scc_sub = subgraph.subgraph(scc)
                for cycle in nx.simple_cycles(scc_sub):
                    if len(cycle) >= 2:
                        cycles.append(cycle)
                    if len(cycles) >= 10:
                        break
                if len(cycles) >= 10:
                    break
        except Exception:
            pass
        return cycles

    def compute_health_report(
        self, skills: list, clusters: dict, cycles: list
    ):
        """Computes architectural health, acyclic integrity, and documentation quality."""
        from skilly_core.models import HealthReport

        circ_count = len(cycles)
        cycle_penalty = min(40, circ_count * 15)

        doc_count = sum(1 for s in skills if getattr(s, "description", None) and not s.description.startswith("Callable") and not s.description.startswith("Function"))
        doc_pct = (doc_count / max(1, len(skills))) * 100

        base_score = 95 - cycle_penalty
        if doc_pct < 35:
            base_score -= 10
        elif doc_pct > 65:
            base_score += 5

        score = max(35, min(100, int(base_score)))
        if score >= 95:
            grade = "A+"
        elif score >= 88:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        summary = f"Grade {grade} ({score}/100): " + ("Acyclic architecture with high integrity." if circ_count == 0 else f"{circ_count} circular dependency cycles detected.")
        return HealthReport(
            grade=grade,
            score=score,
            modularity_score=min(1.0, max(0.6, len(clusters) / max(1, len(self.nodes_by_id) ** 0.45))),
            doc_coverage_percent=doc_pct,
            circular_count=circ_count,
            summary_text=summary,
        )
