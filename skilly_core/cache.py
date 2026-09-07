"""
Production incremental cache for Skilly.
Tracks content hashes to bypass unchanged files across runs.
"""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from skilly_core.models import (
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
    Skill,
    SkillCategory,
)


class AnalysisCache:
    """Manages file hashes and cached extraction results."""

    def __init__(self, cache_dir: Path | str):
        self.cache_dir = Path(cache_dir).resolve()
        self.cache_file = self.cache_dir / "extraction_cache.json"
        self._cache_data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                content = self.cache_file.read_text(encoding="utf-8", errors="ignore")
                self._cache_data = json.loads(content)
            except Exception:
                self._cache_data = {}

    def save(self):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file.write_text(json.dumps(self._cache_data, indent=2), encoding="utf-8")
        except Exception:
            pass

    @staticmethod
    def compute_file_hash(path: Path) -> str:
        """Computes fast SHA256 of file contents."""
        try:
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def get_cached(
        self, rel_path: str, current_hash: str
    ) -> Optional[Tuple[List[Skill], List[GraphNode], List[GraphEdge]]]:
        """Returns cached extraction if file hash matches."""
        entry = self._cache_data.get(rel_path)
        if not entry or entry.get("hash") != current_hash:
            return None

        try:
            skills = [
                Skill(
                    id=s["id"],
                    name=s["name"],
                    category=SkillCategory(s["category"]),
                    description=s["description"],
                    location=s["location"],
                    signature=s.get("signature"),
                    parameters=s.get("parameters", []),
                    return_type=s.get("return_type"),
                    example_usage=s.get("example_usage"),
                    tags=s.get("tags", []),
                    metadata=s.get("metadata", {}),
                )
                for s in entry.get("skills", [])
            ]

            nodes = [
                GraphNode(
                    id=n["id"],
                    label=n["label"],
                    type=NodeType(n["type"]) if n["type"] in [e.value for e in NodeType] else NodeType.MODULE,
                    file_path=n.get("file_path"),
                    line=n.get("line"),
                    description=n.get("description"),
                    importance_score=n.get("importance_score", 0.0),
                    in_degree=n.get("in_degree", 0),
                    out_degree=n.get("out_degree", 0),
                    cluster=n.get("cluster"),
                    metadata=n.get("metadata", {}),
                )
                for n in entry.get("nodes", [])
            ]

            edges = [
                GraphEdge(
                    source=e["source"],
                    target=e["target"],
                    type=EdgeType(e["type"]) if e["type"] in [t.value for t in EdgeType] else EdgeType.IMPORTS,
                    label=e.get("label"),
                    weight=e.get("weight", 1.0),
                )
                for e in entry.get("edges", [])
            ]

            return skills, nodes, edges
        except Exception:
            return None

    def store(
        self,
        rel_path: str,
        file_hash: str,
        skills: List[Skill],
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ):
        """Stores extracted results for file."""
        self._cache_data[rel_path] = {
            "hash": file_hash,
            "skills": [s.to_dict() for s in skills],
            "nodes": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in edges],
        }
