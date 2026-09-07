import json
import tempfile
from pathlib import Path
import pytest
from skilly_core.config import SkillyConfig
from skilly_core.cache import AnalysisCache
from skilly_core.analyzer import ProjectAnalyzer
from skilly_core.cli import main

def test_skilly_config_defaults_and_overrides():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cfg_file = tmp_path / ".skilly.json"
        cfg_file.write_text(json.dumps({
            "max_file_size_kb": 500,
            "fail_on_grade": "A",
            "fail_on_cycles": True,
            "custom_clusters": {"src/api": "API Gateway"}
        }), encoding="utf-8")

        loaded = SkillyConfig.load(tmp_path)
        assert loaded.max_file_size_kb == 500
        assert loaded.fail_on_grade == "A"
        assert loaded.fail_on_cycles is True
        assert loaded.custom_clusters.get("src/api") == "API Gateway"

def test_analysis_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        cache = AnalysisCache(tmp_path)

        dummy_file = tmp_path / "dummy.py"
        dummy_file.write_text("def test(): pass", encoding="utf-8")
        h = AnalysisCache.compute_file_hash(dummy_file)
        assert len(h) == 64  # SHA256 hex length

        # Store dummy extraction
        cache.store("dummy.py", h, [], [], [])
        cache.save()

        # Reload cache
        cache2 = AnalysisCache(tmp_path)
        cached = cache2.get_cached("dummy.py", h)
        assert cached is not None
        skills, nodes, edges = cached
        assert len(skills) == 0

def test_file_size_guard():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        small_file = tmp_path / "small.py"
        small_file.write_text("def ok(): pass\n", encoding="utf-8")

        huge_file = tmp_path / "huge.py"
        # Write 200KB file
        huge_file.write_text("x = 1\n" * 30000, encoding="utf-8")

        # Config max size 50KB
        config = SkillyConfig(max_file_size_kb=50)
        analyzer = ProjectAnalyzer(tmp_path, config=config)
        scanned = analyzer.scan_files()

        scanned_names = [f.name for f in scanned]
        assert "small.py" in scanned_names
        assert "huge.py" not in scanned_names

def test_ci_fail_on_cycles_cli():
    circ_dir = Path(__file__).parent / "fixtures" / "sample_circular_app"
    # Should exit with code 2 when circular dependencies exist
    with pytest.raises(SystemExit) as exc_info:
        main([str(circ_dir), "--fail-on-cycles", "--quiet"])
    assert exc_info.value.code == 2

def test_json_summary_flag(capsys):
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_python_app"
    main([str(fixture_dir), "--json-summary", "--quiet"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "summary" in data
    assert "health" in data
    assert "artifacts" in data

def test_pep561_py_typed_exists():
    py_typed = Path(__file__).parent.parent / "skilly_core" / "py.typed"
    assert py_typed.exists()
