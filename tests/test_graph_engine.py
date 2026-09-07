from skilly_core.graph_engine import KnowledgeGraphEngine
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType

def test_graph_engine_metrics_and_clusters():
    engine = KnowledgeGraphEngine()

    nodes = [
        GraphNode(id="file:main.py", label="main.py", type=NodeType.FILE, file_path="main.py"),
        GraphNode(id="class:AuthService", label="AuthService", type=NodeType.CLASS, file_path="auth.py"),
        GraphNode(id="fn:login", label="login", type=NodeType.FUNCTION, file_path="main.py"),
        GraphNode(id="dep:fastapi", label="fastapi", type=NodeType.DEPENDENCY),
    ]

    edges = [
        GraphEdge(source="file:main.py", target="fn:login", type=EdgeType.EXPOSES),
        GraphEdge(source="fn:login", target="class:AuthService", type=EdgeType.CALLS),
        GraphEdge(source="file:main.py", target="dep:fastapi", type=EdgeType.IMPORTS),
    ]

    g_nodes, g_edges, clusters, hubs, cycles = engine.build_graph(nodes, edges)

    assert len(g_nodes) >= 4
    assert len(g_edges) == 3

    # Check PageRank and degrees calculated
    node_map = {n.id: n for n in g_nodes}
    assert node_map["class:AuthService"].in_degree >= 1
    assert node_map["file:main.py"].out_degree >= 2
    assert node_map["class:AuthService"].importance_score > 0

    # Check acyclic
    assert len(cycles) == 0

def test_graph_engine_cycle_detection():
    engine = KnowledgeGraphEngine()
    nodes = [
        GraphNode(id="a", label="A", type=NodeType.FILE),
        GraphNode(id="b", label="B", type=NodeType.FILE),
    ]
    edges = [
        GraphEdge(source="a", target="b", type=EdgeType.IMPORTS),
        GraphEdge(source="b", target="a", type=EdgeType.IMPORTS),
    ]
    g_nodes, g_edges, clusters, hubs, cycles = engine.build_graph(nodes, edges)
    assert len(cycles) >= 1
