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

def test_framework_detection_no_false_positives():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a file with a helper named 'echo' - should NOT detect Go Echo framework
        helper = tmp_path / "helper.py"
        helper.write_text("def echo(msg):\n    return msg\n", encoding="utf-8")
        reqs = tmp_path / "requirements.txt"
        reqs.write_text("starlette>=0.30.0\n", encoding="utf-8")

        analyzer = ProjectAnalyzer(tmp_path)
        report = analyzer.analyze()

        frameworks = report.summary.frameworks
        assert "Echo (Go)" not in frameworks
        assert "Starlette" in frameworks

def test_javascript_relative_import_edges():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        a_js = tmp_path / "src" / "index.js"
        b_js = tmp_path / "src" / "utils.js"
        a_js.parent.mkdir(parents=True, exist_ok=True)

        b_js.write_text("export function format(s) { return s.trim(); }\n", encoding="utf-8")
        a_js.write_text("import { format } from './utils';\nexport const run = () => format(' hello ');\n", encoding="utf-8")

        analyzer = ProjectAnalyzer(tmp_path)
        report = analyzer.analyze()

        edge_targets = [e.target for e in report.edges if e.source == "file:src/index.js"]
        assert "file:src/utils.js" in edge_targets

def test_python_relative_and_package_imports():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        pkg = tmp_path / "mypkg"
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "sub.py").write_text("def compute(): return 42\n", encoding="utf-8")
        (pkg / "main.py").write_text("from .sub import compute\n\ndef run():\n    return compute()\n", encoding="utf-8")

        analyzer = ProjectAnalyzer(tmp_path)
        report = analyzer.analyze()

        edge_targets = [e.target for e in report.edges if e.source == "file:mypkg/main.py"]
        assert "file:mypkg/sub.py" in edge_targets

def test_github_workflows_and_scripts_skills():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        wf = tmp_path / ".github" / "workflows" / "build.yml"
        wf.parent.mkdir(parents=True, exist_ok=True)
        wf.write_text("""name: Build and Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run Pytest
        run: pytest tests/ -v
""", encoding="utf-8")

        script = tmp_path / "scripts" / "release.sh"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("#!/bin/bash\necho 'releasing'\n", encoding="utf-8")

        analyzer = ProjectAnalyzer(tmp_path)
        report = analyzer.analyze()

        skill_ids = [s.id for s in report.skills]
        assert "workflow:build_and_test" in skill_ids
        assert "script:release_sh" in skill_ids

