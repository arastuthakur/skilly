"""
Data models and schema definitions for Skilly.
Structured representation of extracted skills, knowledge graph nodes, and edges.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillCategory(str, Enum):
    COMMAND = "command"              # CLI commands, npm/make/cargo scripts, dev tools
    API_ENDPOINT = "api_endpoint"    # REST, GraphQL, WebSocket, RPC routes
    DOMAIN_SERVICE = "domain_service"# Key classes, controllers, business services
    DATA_MODEL = "data_model"        # Schemas, ORM models, entities, dataclasses
    CORE_FUNCTION = "core_function"  # Exported core utility/algorithmic functions
    WORKFLOW = "workflow"            # Build, test, deployment, CI, pipelines
    CONFIG = "config"                # Config definitions, environment variables


class NodeType(str, Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    ENDPOINT = "endpoint"
    CLI = "cli"
    DATA_MODEL = "data_model"
    DEPENDENCY = "dependency"
    CONFIG = "config"


class EdgeType(str, Enum):
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    EXPOSES = "exposes"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    CONFIGURES = "configures"


@dataclass
class Skill:
    id: str
    name: str
    category: SkillCategory
    description: str
    location: str  # e.g., "app/api/auth.py:25" or "package.json:scripts.test"
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    example_usage: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "location": self.location,
            "signature": self.signature,
            "parameters": self.parameters,
            "return_type": self.return_type,
            "example_usage": self.example_usage,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class GraphNode:
    id: str
    label: str
    type: NodeType
    file_path: Optional[str] = None
    line: Optional[int] = None
    description: Optional[str] = None
    importance_score: float = 0.0  # PageRank score
    in_degree: int = 0
    out_degree: int = 0
    cluster: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type.value if isinstance(self.type, NodeType) else str(self.type),
            "file_path": self.file_path,
            "line": self.line,
            "description": self.description,
            "importance_score": round(self.importance_score, 5),
            "in_degree": self.in_degree,
            "out_degree": self.out_degree,
            "cluster": self.cluster or "default",
            "metadata": self.metadata,
        }


@dataclass
class GraphEdge:
    source: str
    target: str
    type: EdgeType
    label: Optional[str] = None
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.value if isinstance(self.type, EdgeType) else str(self.type),
            "label": self.label or (self.type.value if isinstance(self.type, EdgeType) else str(self.type)),
            "weight": self.weight,
        }


@dataclass
class ProjectSummary:
    name: str
    root_path: str
    languages: Dict[str, int] = field(default_factory=dict)  # language -> file count
    frameworks: List[str] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    total_skills: int = 0
    total_nodes: int = 0
    total_edges: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "root_path": self.root_path,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "total_skills": self.total_skills,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
        }


@dataclass
class HealthReport:
    grade: str = "A"
    score: int = 95
    modularity_score: float = 0.85
    doc_coverage_percent: float = 80.0
    circular_count: int = 0
    summary_text: str = "Well-structured modular architecture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grade": self.grade,
            "score": self.score,
            "modularity_score": round(self.modularity_score, 2),
            "doc_coverage_percent": round(self.doc_coverage_percent, 1),
            "circular_count": self.circular_count,
            "summary_text": self.summary_text,
        }


@dataclass
class ProjectAnalysisResult:
    summary: ProjectSummary
    skills: List[Skill] = field(default_factory=list)
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    clusters: Dict[str, List[str]] = field(default_factory=dict)
    hubs: List[GraphNode] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    health: HealthReport = field(default_factory=HealthReport)
