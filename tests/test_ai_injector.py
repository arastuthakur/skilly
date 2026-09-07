"""
Tests for AI Assistant Auto-Injection in Skilly.
Validates injection into Claude, GitHub Copilot, Cursor, Antigravity, Codex, Windsurf, and Cline.
"""

from pathlib import Path
from skilly_core.analyzer import ProjectAnalyzer
from skilly_core.config import SkillyConfig
from skilly_core.injectors.ai_injector import AIInjector, START_MARKER, END_MARKER


def test_ai_injector_fresh_files(tmp_path: Path):
    """Test injecting Skilly context into a brand new directory creates all AI configs."""
    # Create dummy app
    (tmp_path / "app.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    analyzer = ProjectAnalyzer(tmp_path)
    result = analyzer.analyze()

    injector = AIInjector()
    injected = injector.inject_all(tmp_path, result)

    # Validate all 7 AI ecosystems are injected
    expected_files = [
        tmp_path / "CLAUDE.md",
        tmp_path / ".github" / "copilot-instructions.md",
        tmp_path / ".cursorrules",
        tmp_path / ".cursor" / "rules" / "skilly.mdc",
        tmp_path / "AGENTS.md",
        tmp_path / "GEMINI.md",
        tmp_path / ".agents" / "rules" / "skilly.md",
        tmp_path / "CODEX.md",
        tmp_path / ".windsurfrules",
        tmp_path / ".clinerules",
    ]

    for p in expected_files:
        assert p.is_file(), f"Expected AI instruction file missing: {p}"
        content = p.read_text(encoding="utf-8")
        assert START_MARKER in content
        assert END_MARKER in content
        assert "skills.md" in content
        assert "knowledge_graph.md" in content
        assert "Arastu Thakur" in content


def test_ai_injector_preserves_existing_user_content(tmp_path: Path):
    """Test that existing user instructions are preserved non-destructively."""
    claude_file = tmp_path / "CLAUDE.md"
    original_content = "# My Custom Claude Rules\n\n- Always use Python 3.12 type hints\n- Never touch production DB\n"
    claude_file.write_text(original_content, encoding="utf-8")

    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")
    analyzer = ProjectAnalyzer(tmp_path)
    result = analyzer.analyze()

    injector = AIInjector(targets=["claude"])
    injector.inject_all(tmp_path, result)

    updated_content = claude_file.read_text(encoding="utf-8")

    # User rules still intact
    assert "# My Custom Claude Rules" in updated_content
    assert "Always use Python 3.12 type hints" in updated_content
    assert "Never touch production DB" in updated_content

    # Skilly directive added
    assert START_MARKER in updated_content
    assert END_MARKER in updated_content


def test_ai_injector_idempotency(tmp_path: Path):
    """Test that running injector multiple times does not duplicate the block."""
    (tmp_path / "main.py").write_text("def add(a, b): return a + b", encoding="utf-8")
    analyzer = ProjectAnalyzer(tmp_path)
    result = analyzer.analyze()

    injector = AIInjector(targets=["claude", "cursor"])
    injector.inject_all(tmp_path, result)

    # First injection
    claude_file = tmp_path / "CLAUDE.md"
    content_run_1 = claude_file.read_text(encoding="utf-8")
    assert content_run_1.count(START_MARKER) == 1
    assert content_run_1.count(END_MARKER) == 1

    # Second injection
    injector.inject_all(tmp_path, result)
    content_run_2 = claude_file.read_text(encoding="utf-8")
    assert content_run_2.count(START_MARKER) == 1
    assert content_run_2.count(END_MARKER) == 1
    assert content_run_1 == content_run_2


def test_ai_injector_selective_targets(tmp_path: Path):
    """Test that targeting specific assistants only touches those files."""
    (tmp_path / "main.py").write_text("x = 1", encoding="utf-8")
    analyzer = ProjectAnalyzer(tmp_path)
    result = analyzer.analyze()

    injector = AIInjector(targets=["copilot"])
    injected = injector.inject_all(tmp_path, result)

    assert (tmp_path / ".github" / "copilot-instructions.md").is_file()
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "CODEX.md").exists()
    assert not (tmp_path / ".cursorrules").exists()


def test_analyzer_write_artifacts_respects_no_inject(tmp_path: Path):
    """Test that analyzer respects inject_ai=False config."""
    (tmp_path / "main.py").write_text("x = 1", encoding="utf-8")
    config = SkillyConfig(inject_ai=False)
    analyzer = ProjectAnalyzer(tmp_path, config=config)
    result = analyzer.analyze()

    artifacts = analyzer.write_artifacts(result, output_dir=tmp_path)

    # Core artifacts exist
    assert (tmp_path / "skills.md").is_file()
    assert (tmp_path / "knowledge_graph.html").is_file()

    # AI configs NOT injected
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "CODEX.md").exists()
    assert not any(k.startswith("ai:") for k in artifacts.keys())
