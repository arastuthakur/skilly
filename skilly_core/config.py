"""
Configuration management for Skilly.
Supports `.skilly.json`, `.skilly.yaml`, pyproject.toml [tool.skilly],
and environment variable overrides.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


@dataclass
class SkillyConfig:
    """Production configuration options for Skilly."""
    # File discovery
    ignore_patterns: List[str] = field(default_factory=lambda: [
        ".git", ".svn", ".hg", "node_modules", "venv", ".venv", "env",
        "__pycache__", ".pytest_cache", "dist", "build", "target", "bin",
        ".next", ".nuxt", "coverage", ".turbo", ".cache", "vendor"
    ])
    max_file_size_kb: int = 1500  # Skip files larger than 1.5MB to avoid memory spikes
    respect_gitignore: bool = True

    # Performance
    parallel: bool = True
    max_workers: Optional[int] = None  # Defaults to os.cpu_count()
    use_cache: bool = True
    cache_dir: str = ".skilly_cache"

    # Quality Gates & CI
    fail_on_grade: Optional[str] = None  # e.g., "B", "C" - fail CI if below
    fail_on_cycles: bool = False         # Exit with code 2 if cycles found
    min_doc_coverage: float = 0.0        # e.g., 50.0%

    # Custom Cluster Mappings (folder prefix -> cluster name)
    custom_clusters: Dict[str, str] = field(default_factory=dict)

    # AI Assistant Auto-Injection
    inject_ai: bool = True
    ai_targets: List[str] = field(default_factory=lambda: ["all"])

    # Output defaults
    output_dir: Optional[str] = None
    skills_filename: str = "skills.md"
    graph_html_filename: str = "knowledge_graph.html"
    graph_json_filename: str = "knowledge_graph.json"
    graph_md_filename: str = "knowledge_graph.md"

    @classmethod
    def load(cls, project_root: Path | str, explicit_config_path: Optional[str] = None) -> SkillyConfig:
        """Loads configuration from project root or explicit path with sensible defaults."""
        root = Path(project_root).resolve()

        config_files = []
        if explicit_config_path:
            config_files.append(Path(explicit_config_path).resolve())
        else:
            config_files.extend([
                root / ".skilly.json",
                root / ".skilly.yaml",
                root / ".skilly.yml",
            ])

        for cfg_path in config_files:
            if cfg_path.exists() and cfg_path.is_file():
                try:
                    content = cfg_path.read_text(encoding="utf-8", errors="ignore")
                    if cfg_path.suffix in (".yaml", ".yml") and HAVE_YAML:
                        data = yaml.safe_load(content) or {}
                    else:
                        data = json.loads(content) or {}
                    return cls.from_dict(data)
                except Exception:
                    pass

        return cls()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkillyConfig:
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ignore_patterns": self.ignore_patterns,
            "max_file_size_kb": self.max_file_size_kb,
            "respect_gitignore": self.respect_gitignore,
            "parallel": self.parallel,
            "max_workers": self.max_workers,
            "use_cache": self.use_cache,
            "cache_dir": self.cache_dir,
            "fail_on_grade": self.fail_on_grade,
            "fail_on_cycles": self.fail_on_cycles,
            "min_doc_coverage": self.min_doc_coverage,
            "custom_clusters": self.custom_clusters,
            "output_dir": self.output_dir,
        }
