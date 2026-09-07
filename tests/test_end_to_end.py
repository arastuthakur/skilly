import json
import tempfile
from pathlib import Path
from skilly_core.analyzer import ProjectAnalyzer

def test_end_to_end_analysis():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_python_app"
    analyzer = ProjectAnalyzer(fixture_dir)
    result = analyzer.analyze()

    assert result.summary.total_skills > 0
    assert result.summary.total_nodes > 0
    assert result.summary.total_edges > 0
    assert "FastAPI" in result.summary.frameworks
    assert "Click CLI" in result.summary.frameworks

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        written = analyzer.write_artifacts(result, output_dir=tmp_path)

        # Verify all 4 expected artifacts exist
        assert written["skills_md"].exists()
        assert written["graph_html"].exists()
        assert written["graph_json"].exists()
        assert written["graph_md"].exists()

        # Check skills.md content
        skills_text = written["skills_md"].read_text(encoding="utf-8")
        assert "# Project Skills & Capabilities" in skills_text
        assert "API: POST /api/v1/auth/login" in skills_text
        assert "CLI: run-server" in skills_text
        assert "AuthService" in skills_text

        # Check knowledge_graph.json
        graph_json = json.loads(written["graph_json"].read_text(encoding="utf-8"))
        assert "nodes" in graph_json
        assert "edges" in graph_json
        assert len(graph_json["nodes"]) > 0

        # Check knowledge_graph.html
        html_text = written["graph_html"].read_text(encoding="utf-8")
        assert "<canvas id=\"graphCanvas\">" in html_text
        assert "DATA =" in html_text

        # Check knowledge_graph.md
        md_text = written["graph_md"].read_text(encoding="utf-8")
        assert "# Knowledge Graph Architecture" in md_text
        assert "```mermaid" in md_text
