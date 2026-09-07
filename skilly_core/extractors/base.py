"""
Base interface for extractors in Skilly.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple
from skilly_core.models import Skill, GraphNode, GraphEdge


class BaseExtractor(ABC):
    """Abstract base class for static context and AST extractors."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()

    @abstractmethod
    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        """
        Analyze files and return extracted skills, knowledge graph nodes, and edges.
        Must be purely deterministic and use zero LLM inference.
        """
        pass
