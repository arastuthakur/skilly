"""
Manifest and project configuration extractor.
Extracts runnable commands, workflows, dependencies, entry points, and environment configs
from package.json, pyproject.toml, Makefile, Cargo.toml, go.mod, Dockerfile, etc.
Zero LLM, purely deterministic parsing.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from skilly_core.extractors.base import BaseExtractor
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType, Skill, SkillCategory

# Try importing tomllib (Python 3.11+) or tomli fallback
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


class ManifestExtractor(BaseExtractor):
    """Parses project manifests, scripts, build configs, and environment templates."""

    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        file_set = {p.resolve(): p for p in file_paths}

        for path in file_paths:
            name = path.name.lower()
            rel = self._rel(path)

            if ".github/workflows" in rel and (name.endswith(".yml") or name.endswith(".yaml")):
                s, n, e = self._parse_github_workflows(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif (rel.startswith("scripts/") or rel.startswith("bin/") or "/scripts/" in rel or "/bin/" in rel) and (name.endswith(".sh") or name.endswith(".py") or name.endswith(".js") or name.endswith(".bash") or name.endswith(".ps1")):
                s, n, e = self._parse_script_file(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "package.json":
                s, n, e = self._parse_package_json(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "pyproject.toml":
                s, n, e = self._parse_pyproject_toml(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "setup.py" or name == "setup.cfg":
                s, n, e = self._parse_setup_py(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in ("requirements.txt", "requirements-dev.txt"):
                s, n, e = self._parse_requirements_txt(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in ("makefile", "gnumakefile"):
                s, n, e = self._parse_makefile(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "cargo.toml":
                s, n, e = self._parse_cargo_toml(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "go.mod":
                s, n, e = self._parse_go_mod(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in ("dockerfile", "docker-compose.yml", "docker-compose.yaml"):
                s, n, e = self._parse_docker(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in (".env.example", ".env.template", ".env.sample"):
                s, n, e = self._parse_env_example(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "pom.xml":
                s, n, e = self._parse_pom_xml(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in ("build.gradle", "build.gradle.kts"):
                s, n, e = self._parse_build_gradle(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "gemfile":
                s, n, e = self._parse_gemfile(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "composer.json":
                s, n, e = self._parse_composer_json(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "cmakelists.txt":
                s, n, e = self._parse_cmake(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name in ("pubspec.yaml", "pubspec.yml"):
                s, n, e = self._parse_pubspec(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "package.swift":
                s, n, e = self._parse_package_swift(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif name == "mix.exs":
                s, n, e = self._parse_mix_exs(path)
                skills.extend(s); nodes.extend(n); edges.extend(e)

        return skills, nodes, edges

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _parse_package_json(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(content)
        except Exception:
            return skills, nodes, edges

        pkg_name = data.get("name", "project")

        # 1. Scripts -> Skills
        scripts = data.get("scripts", {})
        for script_name, cmd in scripts.items():
            category = SkillCategory.WORKFLOW if any(w in script_name.lower() for w in ["build", "test", "lint", "ci", "deploy", "release"]) else SkillCategory.COMMAND
            skill_id = f"npm:{script_name}"
            desc = f"Run npm script '{script_name}': `{cmd}`"
            example = f"npm run {script_name}" if script_name not in ("start", "test") else f"npm {script_name}"

            skills.append(
                Skill(
                    id=skill_id,
                    name=f"npm run {script_name}",
                    category=category,
                    description=desc,
                    location=f"{rel_path}:scripts.{script_name}",
                    signature=cmd,
                    example_usage=example,
                    tags=["npm", "script", script_name],
                    metadata={"command": cmd, "runner": "npm"},
                )
            )

            # Node & Edge
            cmd_node = GraphNode(
                id=f"cmd:{skill_id}",
                label=f"npm run {script_name}",
                type=NodeType.CLI,
                file_path=rel_path,
                description=f"Command: {cmd}",
                metadata={"command": cmd},
            )
            nodes.append(cmd_node)

        # 2. Binaries / CLI exports
        bin_entry = data.get("bin")
        if isinstance(bin_entry, str):
            skills.append(
                Skill(
                    id=f"cli:{pkg_name}",
                    name=f"cli: {pkg_name}",
                    category=SkillCategory.COMMAND,
                    description=f"Executable binary exported by package: {bin_entry}",
                    location=f"{rel_path}:bin",
                    example_usage=f"npx {pkg_name}",
                    tags=["cli", "binary"],
                )
            )
        elif isinstance(bin_entry, dict):
            for bin_cmd, target_path in bin_entry.items():
                skills.append(
                    Skill(
                        id=f"cli:{bin_cmd}",
                        name=f"cli: {bin_cmd}",
                        category=SkillCategory.COMMAND,
                        description=f"Executable binary '{bin_cmd}' -> {target_path}",
                        location=f"{rel_path}:bin.{bin_cmd}",
                        example_usage=f"npx {bin_cmd}",
                        tags=["cli", "binary", bin_cmd],
                    )
                )

        # 3. Dependencies -> Graph Nodes & Edges
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        for dep_name, version in deps.items():
            dep_node_id = f"dep:{dep_name}"
            nodes.append(
                GraphNode(
                    id=dep_node_id,
                    label=dep_name,
                    type=NodeType.DEPENDENCY,
                    file_path=rel_path,
                    description=f"NPM package dependency {dep_name}@{version}",
                    metadata={"version": version, "ecosystem": "npm"},
                )
            )
            edges.append(
                GraphEdge(
                    source=rel_path,
                    target=dep_node_id,
                    type=EdgeType.DEPENDS_ON,
                    label=f"requires {version}",
                )
            )

        return skills, nodes, edges

    def _parse_pyproject_toml(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if tomllib:
                data = tomllib.loads(content)
            else:
                data = self._simple_toml_parse(content)
        except Exception:
            return skills, nodes, edges

        # Scripts / CLI entry points
        project_table = data.get("project", {})
        scripts = project_table.get("scripts", {})
        if not scripts:
            # Poetry scripts
            poetry_table = data.get("tool", {}).get("poetry", {})
            scripts = poetry_table.get("scripts", {})

        for cmd_name, entry in scripts.items():
            skill_id = f"py_cli:{cmd_name}"
            skills.append(
                Skill(
                    id=skill_id,
                    name=f"CLI: {cmd_name}",
                    category=SkillCategory.COMMAND,
                    description=f"Console script entry point: {entry}",
                    location=f"{rel_path}:scripts.{cmd_name}",
                    signature=str(entry),
                    example_usage=f"{cmd_name} --help",
                    tags=["python", "cli", cmd_name],
                    metadata={"entry_point": entry},
                )
            )
            nodes.append(
                GraphNode(
                    id=f"cmd:{skill_id}",
                    label=cmd_name,
                    type=NodeType.CLI,
                    file_path=rel_path,
                    description=f"Entry point: {entry}",
                )
            )

        # Dependencies
        deps = project_table.get("dependencies", [])
        if isinstance(deps, list):
            for dep in deps:
                pkg = re.split(r"[><=~!]", dep)[0].strip()
                if pkg:
                    dep_node_id = f"dep:{pkg}"
                    nodes.append(
                        GraphNode(
                            id=dep_node_id,
                            label=pkg,
                            type=NodeType.DEPENDENCY,
                            file_path=rel_path,
                            description=f"Python dependency {dep}",
                            metadata={"spec": dep, "ecosystem": "pip"},
                        )
                    )
                    edges.append(
                        GraphEdge(
                            source=rel_path,
                            target=dep_node_id,
                            type=EdgeType.DEPENDS_ON,
                            label="requires",
                        )
                    )

        return skills, nodes, edges

    def _parse_setup_py(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return skills, nodes, edges

        # Find entry_points console_scripts
        console_scripts = re.findall(r"['\"](\w+)[\s]*=[\s]*([^'\"]+)['\"]", content)
        for cmd_name, entry in console_scripts:
            if ":" in entry:
                skills.append(
                    Skill(
                        id=f"py_cli:{cmd_name}",
                        name=f"CLI: {cmd_name}",
                        category=SkillCategory.COMMAND,
                        description=f"Console script entry point: {entry}",
                        location=f"{rel_path}",
                        signature=entry,
                        example_usage=f"{cmd_name} --help",
                        tags=["python", "cli", cmd_name],
                    )
                )

        # Find install_requires
        req_match = re.findall(r"['\"]([a-zA-Z0-9_\-\.]+)(?:[><=~!].*)?['\"]", content)
        common_pkgs = {"requests", "fastapi", "flask", "pydantic", "numpy", "pandas", "click", "typer", "pytest"}
        for pkg in set(req_match):
            if pkg.lower() in common_pkgs:
                dep_id = f"dep:{pkg}"
                nodes.append(GraphNode(id=dep_id, label=pkg, type=NodeType.DEPENDENCY, file_path=rel_path))
                edges.append(GraphEdge(source=rel_path, target=dep_id, type=EdgeType.DEPENDS_ON))

        return skills, nodes, edges

    def _parse_requirements_txt(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                pkg = re.split(r"[><=~!#]", line)[0].strip()
                if pkg:
                    dep_id = f"dep:{pkg}"
                    nodes.append(
                        GraphNode(
                            id=dep_id,
                            label=pkg,
                            type=NodeType.DEPENDENCY,
                            file_path=rel_path,
                            description=f"Python dependency: {line}",
                        )
                    )
                    edges.append(
                        GraphEdge(
                            source=rel_path,
                            target=dep_id,
                            type=EdgeType.DEPENDS_ON,
                            label="requires",
                        )
                    )
        except Exception:
            pass

        return skills, nodes, edges

    def _parse_makefile(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            last_comment = ""

            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    last_comment = stripped.lstrip("#").strip()
                    continue

                # Match target: e.g. "build:", "test: lint", etc.
                match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:(?:[^=]|$)", line)
                if match:
                    target = match.group(1)
                    if target.startswith("."):
                        continue
                    desc = last_comment if last_comment else f"Execute Make target '{target}'"
                    category = SkillCategory.WORKFLOW if any(w in target.lower() for w in ["build", "test", "lint", "ci", "deploy", "clean"]) else SkillCategory.COMMAND

                    skill_id = f"make:{target}"
                    skills.append(
                        Skill(
                            id=skill_id,
                            name=f"make {target}",
                            category=category,
                            description=desc,
                            location=f"{rel_path}:{i}",
                            example_usage=f"make {target}",
                            tags=["make", "build-tool", target],
                            metadata={"target": target},
                        )
                    )
                    nodes.append(
                        GraphNode(
                            id=f"cmd:{skill_id}",
                            label=f"make {target}",
                            type=NodeType.CLI,
                            file_path=rel_path,
                            line=i,
                            description=desc,
                        )
                    )
                last_comment = ""
        except Exception:
            pass

        return skills, nodes, edges

    def _parse_cargo_toml(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            # Basic cargo commands
            skills.append(
                Skill(
                    id="cargo:build",
                    name="cargo build",
                    category=SkillCategory.WORKFLOW,
                    description="Compile the Rust project and its dependencies",
                    location=rel_path,
                    example_usage="cargo build --release",
                    tags=["rust", "cargo", "build"],
                )
            )
            skills.append(
                Skill(
                    id="cargo:test",
                    name="cargo test",
                    category=SkillCategory.WORKFLOW,
                    description="Execute Rust unit and integration test suites",
                    location=rel_path,
                    example_usage="cargo test",
                    tags=["rust", "cargo", "test"],
                )
            )
            # Find dependencies
            dep_matches = re.findall(r"^([a-zA-Z0-9_\-]+)\s*=\s*(?:\"([^\"]+)\"|{)", content, re.MULTILINE)
            for dep_name, version in dep_matches:
                if dep_name in ("package", "dependencies", "dev-dependencies", "build-dependencies"):
                    continue
                dep_id = f"dep:{dep_name}"
                nodes.append(
                    GraphNode(
                        id=dep_id,
                        label=dep_name,
                        type=NodeType.DEPENDENCY,
                        file_path=rel_path,
                        description=f"Crate dependency {dep_name}",
                    )
                )
                edges.append(GraphEdge(source=rel_path, target=dep_id, type=EdgeType.DEPENDS_ON))
        except Exception:
            pass

        return skills, nodes, edges

    def _parse_go_mod(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            skills.append(
                Skill(
                    id="go:build",
                    name="go build",
                    category=SkillCategory.WORKFLOW,
                    description="Compile Go packages and dependencies",
                    location=rel_path,
                    example_usage="go build ./...",
                    tags=["go", "build"],
                )
            )
            skills.append(
                Skill(
                    id="go:test",
                    name="go test",
                    category=SkillCategory.WORKFLOW,
                    description="Run Go automated package tests",
                    location=rel_path,
                    example_usage="go test ./... -v",
                    tags=["go", "test"],
                )
            )

            # Dependencies
            req_matches = re.findall(r"^\s*([a-zA-Z0-9_\-\.\/]+)\s+v([0-9a-zA-Z\.\-]+)", content, re.MULTILINE)
            for dep_mod, ver in req_matches:
                dep_id = f"dep:{dep_mod}"
                nodes.append(
                    GraphNode(
                        id=dep_id,
                        label=dep_mod.split("/")[-1],
                        type=NodeType.DEPENDENCY,
                        file_path=rel_path,
                        description=f"Go module dependency {dep_mod} v{ver}",
                        metadata={"module": dep_mod, "version": ver},
                    )
                )
                edges.append(GraphEdge(source=rel_path, target=dep_id, type=EdgeType.DEPENDS_ON))
        except Exception:
            pass

        return skills, nodes, edges

    def _parse_docker(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            name = path.name.lower()
            if "compose" in name:
                skills.append(
                    Skill(
                        id="docker:compose:up",
                        name="docker compose up",
                        category=SkillCategory.WORKFLOW,
                        description="Start containerized services defined in docker-compose",
                        location=rel_path,
                        example_usage="docker compose up -d",
                        tags=["docker", "compose", "containers"],
                    )
                )
            else:
                skills.append(
                    Skill(
                        id="docker:build",
                        name="docker build",
                        category=SkillCategory.WORKFLOW,
                        description="Build Docker container image from Dockerfile",
                        location=rel_path,
                        example_usage="docker build -t app .",
                        tags=["docker", "container", "build"],
                    )
                )
        except Exception:
            pass

        return skills, nodes, edges

    def _parse_env_example(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rel_path = self._rel(path)

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            env_vars: List[Dict[str, str]] = []
            for i, line in enumerate(content.splitlines(), 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    var_name = k.strip()
                    env_vars.append({"name": var_name, "default": v.strip(), "line": str(i)})
                    cfg_node = GraphNode(
                        id=f"cfg:{var_name}",
                        label=var_name,
                        type=NodeType.CONFIG,
                        file_path=rel_path,
                        line=i,
                        description=f"Environment configuration variable {var_name}",
                    )
                    nodes.append(cfg_node)
                    edges.append(GraphEdge(source=rel_path, target=cfg_node.id, type=EdgeType.CONFIGURES))

            if env_vars:
                var_names = [v["name"] for v in env_vars]
                skills.append(
                    Skill(
                        id=f"config:{rel_path}",
                        name=f"Configuration Environment ({len(env_vars)} variables)",
                        category=SkillCategory.CONFIG,
                        description=f"Required environment configuration defined in {rel_path}: {', '.join(var_names[:6])}{'...' if len(var_names) > 6 else ''}",
                        location=rel_path,
                        parameters=env_vars,
                        tags=["config", "environment", "env"],
                    )
                )
        except Exception:
            pass

        return skills, nodes, edges

    def _simple_toml_parse(self, content: str) -> Dict[str, Any]:
        """Fallback naive parser when tomllib is unavailable."""
        result: Dict[str, Any] = {}
        current_section = result
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                sec_name = line[1:-1].strip()
                parts = sec_name.split(".")
                curr = result
                for p in parts:
                    curr = curr.setdefault(p, {})
                current_section = curr
            elif "=" in line:
                k, _, v = line.partition("=")
                current_section[k.strip()] = v.strip().strip('"').strip("'")
        return result

    def _parse_pom_xml(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="mvn:compile", name="mvn compile", category=SkillCategory.WORKFLOW, description="Compile Java source code with Maven", location=rel_path, example_usage="mvn clean compile", tags=["maven", "java", "build"]))
        skills.append(Skill(id="mvn:test", name="mvn test", category=SkillCategory.WORKFLOW, description="Run Maven test suite", location=rel_path, example_usage="mvn test", tags=["maven", "java", "test"]))
        skills.append(Skill(id="mvn:package", name="mvn package", category=SkillCategory.WORKFLOW, description="Package Java application into JAR/WAR", location=rel_path, example_usage="mvn package -DskipTests", tags=["maven", "java", "package"]))
        nodes.append(GraphNode(id="cmd:mvn:compile", label="mvn compile", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_build_gradle(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="gradle:build", name="gradle build", category=SkillCategory.WORKFLOW, description="Assemble and test Gradle project", location=rel_path, example_usage="./gradlew build", tags=["gradle", "build"]))
        skills.append(Skill(id="gradle:test", name="gradle test", category=SkillCategory.WORKFLOW, description="Run Gradle test verification tasks", location=rel_path, example_usage="./gradlew test", tags=["gradle", "test"]))
        nodes.append(GraphNode(id="cmd:gradle:build", label="gradle build", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_gemfile(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="bundle:install", name="bundle install", category=SkillCategory.WORKFLOW, description="Install Ruby Gem dependencies", location=rel_path, example_usage="bundle install", tags=["ruby", "gem", "bundle"]))
        skills.append(Skill(id="bundle:exec", name="bundle exec", category=SkillCategory.COMMAND, description="Execute Ruby command in context of bundle", location=rel_path, example_usage="bundle exec rspec", tags=["ruby", "bundle"]))
        nodes.append(GraphNode(id="cmd:bundle:install", label="bundle install", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_composer_json(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            scripts = data.get("scripts", {})
            for name, cmd in scripts.items():
                if isinstance(cmd, str):
                    skills.append(Skill(id=f"composer:{name}", name=f"composer {name}", category=SkillCategory.COMMAND, description=f"Run Composer script: {cmd}", location=rel_path, example_usage=f"composer {name}", tags=["php", "composer"]))
            deps = {**data.get("require", {}), **data.get("require-dev", {})}
            for dep in deps:
                if "/" in dep:
                    nodes.append(GraphNode(id=f"dep:{dep}", label=dep, type=NodeType.DEPENDENCY, file_path=rel_path))
                    edges.append(GraphEdge(source=rel_path, target=f"dep:{dep}", type=EdgeType.DEPENDS_ON))
        except Exception:
            pass
        return skills, nodes, edges

    def _parse_cmake(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="cmake:build", name="cmake build", category=SkillCategory.WORKFLOW, description="Configure and build C/C++ project with CMake", location=rel_path, example_usage="cmake -B build && cmake --build build", tags=["cmake", "cpp", "c", "build"]))
        nodes.append(GraphNode(id="cmd:cmake:build", label="cmake build", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_pubspec(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="flutter:run", name="flutter run", category=SkillCategory.WORKFLOW, description="Run Flutter / Dart application", location=rel_path, example_usage="flutter run", tags=["dart", "flutter"]))
        skills.append(Skill(id="flutter:test", name="flutter test", category=SkillCategory.WORKFLOW, description="Execute Flutter automated tests", location=rel_path, example_usage="flutter test", tags=["dart", "flutter", "test"]))
        nodes.append(GraphNode(id="cmd:flutter:run", label="flutter run", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_package_swift(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="swift:build", name="swift build", category=SkillCategory.WORKFLOW, description="Build Swift package targets", location=rel_path, example_usage="swift build", tags=["swift", "build"]))
        skills.append(Skill(id="swift:test", name="swift test", category=SkillCategory.WORKFLOW, description="Run Swift package tests", location=rel_path, example_usage="swift test", tags=["swift", "test"]))
        nodes.append(GraphNode(id="cmd:swift:build", label="swift build", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_mix_exs(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        skills.append(Skill(id="mix:compile", name="mix compile", category=SkillCategory.WORKFLOW, description="Compile Elixir project with Mix", location=rel_path, example_usage="mix compile", tags=["elixir", "mix", "build"]))
        skills.append(Skill(id="mix:test", name="mix test", category=SkillCategory.WORKFLOW, description="Run Elixir unit test suite", location=rel_path, example_usage="mix test", tags=["elixir", "mix", "test"]))
        nodes.append(GraphNode(id="cmd:mix:compile", label="mix compile", type=NodeType.CLI, file_path=rel_path))
        return skills, nodes, edges

    def _parse_github_workflows(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            m_name = re.search(r"^name:\s*['\"]?([^'\"\n]+)['\"]?", content, re.MULTILINE)
            workflow_name = m_name.group(1).strip() if m_name else path.stem
            clean_id = re.sub(r"[^a-zA-Z0-9_-]", "_", workflow_name.lower())

            skill_id = f"workflow:{clean_id}"
            skills.append(
                Skill(
                    id=skill_id,
                    name=f"CI Workflow: {workflow_name}",
                    category=SkillCategory.WORKFLOW,
                    description=f"GitHub Actions CI workflow defined in {rel_path}",
                    location=rel_path,
                    example_usage=f"gh workflow run {path.name}",
                    tags=["ci", "github-actions", "workflow"],
                )
            )
            nodes.append(
                GraphNode(
                    id=f"cmd:{skill_id}",
                    label=f"ci:{workflow_name}",
                    type=NodeType.CLI,
                    file_path=rel_path,
                    description=f"CI Workflow: {workflow_name}",
                )
            )

            run_commands = re.findall(r"^\s+run:\s*['\"]?([^\n|'\"]+)['\"]?", content, re.MULTILINE)
            for raw_cmd in set(run_commands):
                cmd = raw_cmd.strip()
                if cmd and not cmd.startswith("$") and not cmd.startswith("#") and len(cmd) < 80:
                    cmd_id = re.sub(r"[^a-zA-Z0-9_-]", "_", cmd.lower())[:40]
                    skills.append(
                        Skill(
                            id=f"ci_step:{clean_id}:{cmd_id}",
                            name=f"CI Step: {cmd}",
                            category=SkillCategory.COMMAND,
                            description=f"Command executed in CI workflow {workflow_name} ({rel_path})",
                            location=rel_path,
                            example_usage=cmd,
                            tags=["ci", "command", "github-actions"],
                        )
                    )
        except Exception:
            pass
        return skills, nodes, edges

    def _parse_script_file(self, path: Path) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []
        rel_path = self._rel(path)
        script_name = path.name
        clean_id = re.sub(r"[^a-zA-Z0-9_-]", "_", script_name.lower())
        skill_id = f"script:{clean_id}"

        usage = f"python {rel_path}" if path.suffix == ".py" else (f"node {rel_path}" if path.suffix in (".js", ".mjs") else f"./{rel_path}")

        skills.append(
            Skill(
                id=skill_id,
                name=f"Script: {script_name}",
                category=SkillCategory.COMMAND,
                description=f"Executable project script at {rel_path}",
                location=rel_path,
                example_usage=usage,
                tags=["script", path.suffix.lstrip(".") or "sh"],
            )
        )
        nodes.append(
            GraphNode(
                id=f"cmd:{skill_id}",
                label=script_name,
                type=NodeType.CLI,
                file_path=rel_path,
                description=f"Executable script: {rel_path}",
            )
        )
        return skills, nodes, edges
