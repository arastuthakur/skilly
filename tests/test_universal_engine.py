from pathlib import Path
from skilly_core.extractors.universal_engine import UniversalPolyglotExtractor
from skilly_core.analyzer import ProjectAnalyzer
from skilly_core.models import SkillCategory

def test_universal_polyglot_extractor():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_polyglot_app"
    extractor = UniversalPolyglotExtractor(fixture_dir)
    files = list(fixture_dir.glob("*.*"))
    skills, nodes, edges = extractor.extract(files)

    skill_names = [s.name for s in skills]

    # 1. C structs & functions
    assert "Point3D" in skill_names or any("Point" in n for n in skill_names)
    assert "calculate_distance" in skill_names or any("calculate_distance" in n for n in skill_names)

    # 2. Ruby classes & methods
    assert "PriceCalculator" in skill_names or any("PriceCalculator" in n for n in skill_names)
    assert "calculate_discount" in skill_names or any("calculate_discount" in n for n in skill_names)

    # 3. Solidity smart contracts & methods
    assert "TokenVault" in skill_names or any("TokenVault" in n for n in skill_names)
    assert "deposit" in skill_names or any("deposit" in n for n in skill_names)

    # 4. Java Spring REST route
    assert any("catalog/items" in s.name for s in skills)

def test_polyglot_project_analysis():
    fixture_dir = Path(__file__).parent / "fixtures" / "sample_polyglot_app"
    analyzer = ProjectAnalyzer(fixture_dir)
    result = analyzer.analyze()

    assert result.summary.total_skills >= 5
    assert len(result.summary.languages) >= 3
    # Check framework recognition
    assert "Spring Boot" in result.summary.frameworks or "C" in result.summary.languages
