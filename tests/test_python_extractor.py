from pathlib import Path
from skilly_core.extractors.python_extractor import PythonASTExtractor
from skilly_core.models import SkillCategory, NodeType

def test_python_ast_extractor():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_python_app"
    extractor = PythonASTExtractor(fixture_dir)
    py_files = list(fixture_dir.glob("*.py"))
    skills, nodes, edges = extractor.extract(py_files)

    # 1. API route extraction
    api_skills = [s for s in skills if s.category == SkillCategory.API_ENDPOINT]
    api_names = [s.name for s in api_skills]
    assert "API: POST /api/v1/auth/login" in api_names
    assert "API: GET /api/v1/health" in api_names

    # 2. CLI command extraction
    cli_skills = [s for s in skills if s.category == SkillCategory.COMMAND]
    cli_names = [s.name for s in cli_skills]
    assert "CLI: run-server" in cli_names

    # 3. Data models and services
    model_skills = [s for s in skills if s.category == SkillCategory.DATA_MODEL]
    model_names = [s.name for s in model_skills]
    assert "UserLoginRequest" in model_names
    assert "AuthToken" in model_names

    service_skills = [s for s in skills if s.category == SkillCategory.DOMAIN_SERVICE]
    service_names = [s.name for s in service_skills]
    assert "AuthService" in service_names

    # 4. Graph nodes and edges
    node_labels = [n.label for n in nodes]
    assert "login_endpoint" in node_labels
    assert "AuthService" in node_labels
    assert "UserLoginRequest" in node_labels
