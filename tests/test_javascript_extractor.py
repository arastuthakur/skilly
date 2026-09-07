from pathlib import Path
from skilly_core.extractors.javascript_extractor import JavaScriptExtractor
from skilly_core.models import SkillCategory, NodeType

def test_javascript_extractor():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_node_app"
    extractor = JavaScriptExtractor(fixture_dir)
    js_files = list(fixture_dir.glob("*.js"))
    skills, nodes, edges = extractor.extract(js_files)

    # Check Express API routes
    ep_skills = [s for s in skills if s.category == SkillCategory.API_ENDPOINT]
    ep_names = [s.name for s in ep_skills]
    assert "API: GET /api/users" in ep_names
    assert "API: POST /api/users" in ep_names

    # Check exported function
    fn_skills = [s for s in skills if s.category == SkillCategory.CORE_FUNCTION]
    fn_names = [s.name for s in fn_skills]
    assert "calculateTax" in fn_names
