from pathlib import Path
from skilly_core.extractors.manifest_extractor import ManifestExtractor
from skilly_core.models import SkillCategory, NodeType

def test_manifest_extractor_package_json():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_node_app"
    extractor = ManifestExtractor(fixture_dir)
    files = list(fixture_dir.glob("*"))
    skills, nodes, edges = extractor.extract(files)

    # Check extracted npm scripts
    script_names = [s.name for s in skills]
    assert "npm run start" in script_names
    assert "npm run dev" in script_names
    assert "npm run test" in script_names

    # Check dependencies in nodes
    node_labels = [n.label for n in nodes]
    assert "express" in node_labels
    assert "cors" in node_labels

def test_manifest_extractor_makefile_and_env():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_python_app"
    extractor = ManifestExtractor(fixture_dir)
    files = list(fixture_dir.glob("*"))
    skills, nodes, edges = extractor.extract(files)

    skill_names = [s.name for s in skills]
    assert "make run" in skill_names
    assert "make test" in skill_names
    assert any("Configuration Environment" in s.name for s in skills)

    # Verify requirements.txt
    node_labels = [n.label for n in nodes]
    assert "fastapi" in node_labels
    assert "pydantic" in node_labels

def test_manifest_extractor_skill_md(tmp_path):
    skill_file = tmp_path / "skills" / "pentest" / "SKILL.md"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text("""---
name: pentest-audit
description: Autonomous penetration testing skill for web and API targets.
license: Apache-2.0
---

# Pentest Audit

```bash
strix -t https://example.com --max-budget 10
```
""", encoding="utf-8")

    extractor = ManifestExtractor(tmp_path)
    skills, nodes, edges = extractor.extract([skill_file])

    assert len(skills) == 1
    skill = skills[0]
    assert skill.id == "agent_skill:pentest-audit"
    assert skill.name == "Agent Skill: pentest-audit"
    assert "Autonomous penetration testing" in skill.description
    assert "strix -t" in skill.example_usage
    assert any(n.label == "pentest-audit" for n in nodes)

