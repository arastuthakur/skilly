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
