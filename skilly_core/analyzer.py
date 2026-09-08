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
    "fixtures",
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

        ALLOWED_DOT_DIRS = {".github", ".circleci", ".gitlab", ".agents", ".claude"}

        for root, dirs, files in os.walk(self.target_dir):
            # Prune ignored directories in-place (preserve CI dirs like .github)
            dirs[:] = [
                d for d in dirs
                if d not in custom_ignores and d not in DEFAULT_IGNORE_DIRS and (not d.startswith(".") or d in ALLOWED_DOT_DIRS)
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

        # Deduplicate skills deterministically (merge richest descriptions/metadata)
        unique_skills: Dict[str, Skill] = {}
        for s in all_skills:
            if s.id not in unique_skills:
                unique_skills[s.id] = s
            else:
                existing = unique_skills[s.id]
                if len(s.description or "") > len(existing.description or ""):
                    unique_skills[s.id] = s
        all_skills = list(unique_skills.values())

        # Detect Frameworks from skills and dependencies
        frameworks = self._detect_frameworks(all_skills, all_nodes)

        # 3. Knowledge Graph Engine
        engine = KnowledgeGraphEngine()
        nodes, edges, clusters, hubs, cycles = engine.build_graph(all_nodes, all_edges)
        health = engine.compute_health_report(all_skills, clusters, cycles)

        # Determine clean project name without exposing host directory names
        proj_name = self.target_dir.name or "Project"
        pyproject_file = self.target_dir / "pyproject.toml"
        package_json = self.target_dir / "package.json"
        if pyproject_file.exists():
            try:
                import tomllib
                pyproj_data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
                found_name = pyproj_data.get("project", {}).get("name")
                if found_name:
                    proj_name = found_name
            except Exception:
                pass
        elif package_json.exists():
            try:
                pkg_data = json.loads(package_json.read_text(encoding="utf-8"))
                found_name = pkg_data.get("name")
                if found_name:
                    proj_name = found_name
            except Exception:
                pass

        summary = ProjectSummary(
            name=proj_name,
            root_path=".",
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
        include_skills: bool = True,
        include_graph: bool = True,
        inject_ai: Optional[bool] = None,
    ) -> Dict[str, Path]:
        """Generates and writes artifacts selectively to the output directory."""
        out_path = Path(output_dir).resolve() if output_dir else self.target_dir
        out_path.mkdir(parents=True, exist_ok=True)

        paths: Dict[str, Path] = {}

        # 1. skills.md
        if include_skills:
            skills_gen = SkillsGenerator()
            skills_content = skills_gen.generate(result)
            p_skills = out_path / skills_file
            p_skills.write_text(skills_content, encoding="utf-8")
            paths["skills_md"] = p_skills

        # 2-4. Knowledge Graph Artifacts
        if include_graph:
            html_gen = HTMLVisualizer()
            html_content = html_gen.generate(result)
            p_html = out_path / graph_html_file
            p_html.write_text(html_content, encoding="utf-8")
            paths["graph_html"] = p_html

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

            md_gen = GraphMarkdownGenerator()
            graph_md_content = md_gen.generate(result)
            p_md = out_path / graph_md_file
            p_md.write_text(graph_md_content, encoding="utf-8")
            paths["graph_md"] = p_md

        # 5. AI Assistant Auto-Injection (Claude, Copilot, Cursor, Antigravity, Codex, Windsurf, Cline)
        should_inject = inject_ai if inject_ai is not None else getattr(self.config, "inject_ai", True)
        if should_inject and include_skills:
            from skilly_core.injectors.ai_injector import AIInjector
            targets = getattr(self.config, "ai_targets", ["all"])
            injector = AIInjector(targets=targets)
            target_injection_dir = out_path if output_dir else self.target_dir
            injected = injector.inject_all(target_injection_dir, result)
            for k, p in injected.items():
                paths[f"ai:{k}"] = p

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
        from skilly_core.models import NodeType
        dep_labels = {n.label.lower() for n in nodes if getattr(n, "type", None) == NodeType.DEPENDENCY}
        dep_ids = {n.id.lower() for n in nodes if getattr(n, "type", None) == NodeType.DEPENDENCY}
        skill_tags = {t.lower() for s in skills for t in s.tags}

        # Tag-based framework triggers (explicitly labeled by AST extractors)
        tag_frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "express": "Express.js",
            "nextjs": "Next.js",
            "next": "Next.js",
            "react": "React",
            "vue": "Vue",
            "svelte": "Svelte",
            "gin": "Gin (Go)",
            "spring": "Spring Boot",
            "click": "Click CLI",
            "typer": "Typer CLI",
            "pydantic": "Pydantic",
            "sqlalchemy": "SQLAlchemy",
            "prisma": "Prisma ORM",
            "docker": "Docker",
            "make": "Make",
            "cmake": "CMake",
            "pytest": "Pytest",
            "jest": "Jest",
            "vitest": "Vitest",
            "mocha": "Mocha",
        }
        for tag, name in tag_frameworks.items():
            if tag in skill_tags:
                detected.add(name)

        # Manifest dependency triggers (exact package names)
        dep_frameworks = {
            "fastapi": "FastAPI",
            "starlette": "Starlette",
            "uvicorn": "Uvicorn",
            "flask": "Flask",
            "django": "Django",
            "tornado": "Tornado",
            "sanic": "Sanic",
            "litestar": "Litestar",
            "express": "Express.js",
            "fastify": "Fastify",
            "koa": "Koa",
            "@nestjs/core": "NestJS",
            "nestjs": "NestJS",
            "next": "Next.js",
            "react": "React",
            "vue": "Vue",
            "svelte": "Svelte",
            "@angular/core": "Angular",
            "angular": "Angular",
            "gin": "Gin (Go)",
            "gin-gonic/gin": "Gin (Go)",
            "github.com/gin-gonic/gin": "Gin (Go)",
            "labstack/echo": "Echo (Go)",
            "github.com/labstack/echo": "Echo (Go)",
            "fiber": "Fiber (Go)",
            "gofiber/fiber": "Fiber (Go)",
            "github.com/gofiber/fiber": "Fiber (Go)",
            "actix": "Actix (Rust)",
            "actix-web": "Actix (Rust)",
            "axum": "Axum (Rust)",
            "rocket": "Rocket (Rust)",
            "spring-boot": "Spring Boot",
            "rails": "Ruby on Rails",
            "laravel": "Laravel (PHP)",
            "symfony": "Symfony (PHP)",
            "pytest": "Pytest",
            "jest": "Jest",
            "click": "Click CLI",
            "typer": "Typer CLI",
            "pydantic": "Pydantic",
            "sqlalchemy": "SQLAlchemy",
            "prisma": "Prisma ORM",
        }
        for dep_key, name in dep_frameworks.items():
            if any(dep_key == d or dep_key in d or f"dep:{dep_key}" in dep_ids for d in dep_labels):
                detected.add(name)

        return sorted(detected)
