"""
Skilly: Autonomous, LLM-free project capability analyzer and knowledge graph generator.
Converts any codebase into skills.md and interactive knowledge graphs.
"""

from skilly_core.analyzer import ProjectAnalyzer
from skilly_core.models import ProjectAnalysisResult, Skill, SkillCategory, GraphNode, GraphEdge

__version__ = "1.0.3"

def analyze_project(target_dir: str = ".") -> ProjectAnalysisResult:
    """Convenience function to analyze a project directory."""
    analyzer = ProjectAnalyzer(target_dir)
    return analyzer.analyze()

__all__ = [
    "ProjectAnalyzer",
    "ProjectAnalysisResult",
    "Skill",
    "SkillCategory",
    "GraphNode",
    "GraphEdge",
    "analyze_project",
    "__version__",
]
