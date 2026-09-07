"""
Core Analyzer Orchestrator for Skilly.
Walks codebase, coordinates AST and manifest extractors, runs graph engine,
and generates skills.md, knowledge_graph.html, knowledge_graph.json, and knowledge_graph.md.
Purely deterministic, zero LLM dependencies.
"""

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from skilly_core.extractors.manifest_extractor import ManifestExtractor
from skilly_core.extractors.python_extractor import PythonASTExtractor
from skilly_core.extractors.javascript_extractor import JavaScriptExtractor
from skilly_core.extractors.polyglot_extractor import PolyglotExtractor
from skilly_core.extractors.universal_engine import UniversalPolyglotExtractor
from skilly_core.graph_engine import KnowledgeGraphEngine
from skilly_core.generators.skills_generator import SkillsGenerator
from skilly_core.generators.graph_markdown_generator import GraphMarkdownGenerator
from skilly_core.generators.html_visualizer import HTMLVisualizer
from skilly_core.models import (
    GraphEdge,
    GraphNode,
    ProjectAnalysisResult,
    ProjectSummary,
    Skill,
)

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    "target",
    "bin",
    "obj",
    ".idea",
    ".vscode",
    "coverage",
    ".turbo",
    ".cache",
}

LANGUAGE_EXTENSIONS = {
    # Scripting & Web
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".php": "PHP",
    ".rb": "Ruby",
    ".lua": "Lua",
    ".jl": "Julia",
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".ps1": "PowerShell",
    # Systems & Native
    ".c": "C",
    ".h": "C Header",
    ".cpp": "C++",
    ".hpp": "C++ Header",
    ".cc": "C++",
    ".cxx": "C++",
    ".rs": "Rust",
    ".go": "Go",
    ".zig": "Zig",
    ".nim": "Nim",
    # Managed & Enterprise
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".cs": "C#",
    ".scala": "Scala",
    ".swift": "Swift",
    ".dart": "Dart",
    # Functional & Dynamic
    ".ex": "Elixir",
    ".exs": "Elixir Script",
    ".erl": "Erlang",
    ".clj": "Clojure",
    ".hs": "Haskell",
    ".r": "R",
    # Schemas & Smart Contracts
    ".sol": "Solidity",
    ".sql": "SQL",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".proto": "Protobuf",
    ".prisma": "Prisma",
}


from concurrent.futures import ThreadPoolExecutor
from skilly_core.config import SkillyConfig
from skilly_core.cache import AnalysisCache
from skilly_core.extractors.manifest_extractor import ManifestExtractor
from skilly_core.extractors.python_extractor import PythonASTExtractor
from skilly_core.extractors.javascript_extractor import JavaScriptExtractor
from skilly_core.extractors.polyglot_extractor import PolyglotExtractor
from skilly_core.extractors.universal_engine import UniversalPolyglotExtractor
from skilly_core.graph_engine import KnowledgeGraphEngine
from skilly_core.generators.skills_generator import SkillsGenerator
from skilly_core.generators.graph_markdown_generator import GraphMarkdownGenerator
from skilly_core.generators.html_visualizer import HTMLVisualizer
from skilly_core.models import (
    GraphEdge,
    GraphNode,
    ProjectAnalysisResult,
    ProjectSummary,
    Skill,
)


class ProjectAnalyzer:
    """Orchestrates whole-project capability extraction and knowledge graph synthesis."""

    def __init__(self, target_dir: Path | str, config: Optional[SkillyConfig] = None):
        self.target_dir = Path(target_dir).resolve()
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Target directory does not exist: {self.target_dir}")
        self.config = config or SkillyConfig.load(self.target_dir)
        self.cache = AnalysisCache(self.target_dir / self.config.cache_dir) if self.config.use_cache else None

    def scan_files(self) -> List[Path]:
        """Walks the directory and collects all relevant source and manifest files."""
        matched_files: List[Path] = []
        gitignore_patterns = self._load_gitignore() if self.config.respect_gitignore else []
        custom_ignores = set(self.config.ignore_patterns)

        for root, dirs, files in os.walk(self.target_dir):
            # Prune ignored directories in-place
            dirs[:] = [
                d for d in dirs
                if d not in custom_ignores and d not in DEFAULT_IGNORE_DIRS and not d.startswith(".")
            ]

            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(self.target_dir)

                if self._is_ignored(rel_path, gitignore_patterns):
                    continue

                # File size guard (skip minified bundles or massive files)
                try:
                    size_kb = full_path.stat().st_size / 1024
                    if size_kb > self.config.max_file_size_kb:
                        continue
                except Exception:
                    pass

                matched_files.append(full_path)

        return matched_files

    def analyze(self) -> ProjectAnalysisResult:
        """Runs all extractors and graph algorithms to produce ProjectAnalysisResult."""
        files = self.scan_files()

        # 1. Summary Statistics
        languages: Dict[str, int] = defaultdict(int)
        total_lines = 0

        for f in files:
            ext = f.suffix.lower()
            if ext in LANGUAGE_EXTENSIONS:
                languages[LANGUAGE_EXTENSIONS[ext]] += 1
            try:
                lines = sum(1 for _ in open(f, "rb"))
                total_lines += lines
            except Exception:
                pass

        # 2. Extractors
        extractors = [
            ManifestExtractor(self.target_dir),
            PythonASTExtractor(self.target_dir),
            JavaScriptExtractor(self.target_dir),
            PolyglotExtractor(self.target_dir),
            UniversalPolyglotExtractor(self.target_dir),
        ]

        all_skills: List[Skill] = []
        all_nodes: List[GraphNode] = []
        all_edges: List[GraphEdge] = []

        if self.config.parallel and len(files) > 20:
            workers = self.config.max_workers or min(8, max(2, os.cpu_count() or 4))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(ext.extract, files) for ext in extractors]
                for fut in futures:
                    try:
                        s, n, e = fut.result()
                        all_skills.extend(s); all_nodes.extend(n); all_edges.extend(e)
                    except Exception:
                        pass
        else:
            for ext in extractors:
                try:
                    s, n, e = ext.extract(files)
                    all_skills.extend(s); all_nodes.extend(n); all_edges.extend(e)
                except Exception:
                    pass

        # Save cache
        if self.cache:
            self.cache.save()

        # Detect Frameworks from skills and dependencies
        frameworks = self._detect_frameworks(all_skills, all_nodes)

        # 3. Knowledge Graph Engine
        engine = KnowledgeGraphEngine()
        nodes, edges, clusters, hubs, cycles = engine.build_graph(all_nodes, all_edges)
        health = engine.compute_health_report(all_skills, clusters, cycles)

        summary = ProjectSummary(
            name=self.target_dir.name or "Project",
            root_path=str(self.target_dir),
            languages=dict(languages),
            frameworks=frameworks,
            total_files=len(files),
            total_lines=total_lines,
            total_skills=len(all_skills),
            total_nodes=len(nodes),
            total_edges=len(edges),
        )

        return ProjectAnalysisResult(
            summary=summary,
            skills=all_skills,
            nodes=nodes,
            edges=edges,
            clusters=clusters,
            hubs=hubs,
            circular_dependencies=cycles,
            health=health,
        )

    def write_artifacts(
        self,
        result: ProjectAnalysisResult,
        output_dir: Optional[Path | str] = None,
        skills_file: str = "skills.md",
        graph_html_file: str = "knowledge_graph.html",
        graph_json_file: str = "knowledge_graph.json",
        graph_md_file: str = "knowledge_graph.md",
    ) -> Dict[str, Path]:
        """Generates and writes all artifacts to the output directory (defaults to project dir)."""
        out_path = Path(output_dir).resolve() if output_dir else self.target_dir
        out_path.mkdir(parents=True, exist_ok=True)

        paths: Dict[str, Path] = {}

        # 1. skills.md
        skills_gen = SkillsGenerator()
        skills_content = skills_gen.generate(result)
        p_skills = out_path / skills_file
        p_skills.write_text(skills_content, encoding="utf-8")
        paths["skills_md"] = p_skills

        # 2. knowledge_graph.html
        html_gen = HTMLVisualizer()
        html_content = html_gen.generate(result)
        p_html = out_path / graph_html_file
        p_html.write_text(html_content, encoding="utf-8")
        paths["graph_html"] = p_html

        # 3. knowledge_graph.json
        graph_data = {
            "summary": result.summary.to_dict(),
            "nodes": [n.to_dict() for n in result.nodes],
            "edges": [e.to_dict() for e in result.edges],
            "clusters": result.clusters,
            "hubs": [h.to_dict() for h in result.hubs],
            "circular_dependencies": result.circular_dependencies,
        }
        p_json = out_path / graph_json_file
        p_json.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
        paths["graph_json"] = p_json

        # 4. knowledge_graph.md
        md_gen = GraphMarkdownGenerator()
        graph_md_content = md_gen.generate(result)
        p_md = out_path / graph_md_file
        p_md.write_text(graph_md_content, encoding="utf-8")
        paths["graph_md"] = p_md

        return paths

    def _load_gitignore(self) -> List[str]:
        gi = self.target_dir / ".gitignore"
        patterns = []
        if gi.exists():
            try:
                for line in gi.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line.rstrip("/"))
            except Exception:
                pass
        return patterns

    def _is_ignored(self, rel_path: Path, patterns: List[str]) -> bool:
        rel_str = str(rel_path).replace("\\", "/")
        for p in patterns:
            if p in rel_str or rel_str.startswith(p):
                return True
        return False

    def _detect_frameworks(self, skills: List[Skill], nodes: List[GraphNode]) -> List[str]:
        detected = set()
        labels_lower = {n.label.lower() for n in nodes}
        skill_tags = {t.lower() for s in skills for t in s.tags}

        framework_signatures = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "express": "Express.js",
            "next": "Next.js",
            "react": "React",
            "vue": "Vue",
            "svelte": "Svelte",
            "gin": "Gin (Go)",
            "echo": "Echo (Go)",
            "fiber": "Fiber (Go)",
            "actix": "Actix (Rust)",
            "axum": "Axum (Rust)",
            "rocket": "Rocket (Rust)",
            "spring": "Spring Boot",
            "rails": "Ruby on Rails",
            "laravel": "Laravel (PHP)",
            "symfony": "Symfony (PHP)",
            "aspnet": "ASP.NET Core",
            "flutter": "Flutter",
            "phoenix": "Phoenix (Elixir)",
            "pytest": "Pytest",
            "jest": "Jest",
            "click": "Click CLI",
            "typer": "Typer CLI",
            "pydantic": "Pydantic",
            "sqlalchemy": "SQLAlchemy",
            "prisma": "Prisma ORM",
            "docker": "Docker",
            "make": "Make",
            "cmake": "CMake",
            "maven": "Maven",
            "gradle": "Gradle",
        }

        for key, name in framework_signatures.items():
            if key in labels_lower or key in skill_tags:
                detected.add(name)

        return sorted(detected)
