"""
Polyglot static extractor for Go, Rust, Java, and C#.
Extracts public functions, structs, interfaces, REST routes (Gin, Actix, Axum, Spring),
types, and package imports without using LLMs.
"""

import re
from pathlib import Path
from typing import List, Tuple
from skilly_core.extractors.base import BaseExtractor
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType, Skill, SkillCategory


class PolyglotExtractor(BaseExtractor):
    """Analyzes Go, Rust, Java, and C# files for skills, exports, and relationships."""

    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for path in file_paths:
            ext = path.suffix.lower()
            rel_parts = path.parts
            if any(p in ("vendor", "target", "build", ".gradle", "bin", "obj") for p in rel_parts):
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = self._rel(path)
            file_node_id = f"file:{rel_path}"

            if ext == ".go":
                s, n, e = self._analyze_go(content, path, rel_path, file_node_id)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif ext == ".rs":
                s, n, e = self._analyze_rust(content, path, rel_path, file_node_id)
                skills.extend(s); nodes.extend(n); edges.extend(e)
            elif ext in (".java", ".kt"):
                s, n, e = self._analyze_java_kotlin(content, path, rel_path, file_node_id)
                skills.extend(s); nodes.extend(n); edges.extend(e)

        return skills, nodes, edges

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _analyze_go(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []

        # Add file node
        nodes.append(
            GraphNode(
                id=file_node_id,
                label=path.name,
                type=NodeType.FILE,
                file_path=rel_path,
                description=f"Go source file {path.name}",
                metadata={"lines": len(content.splitlines())},
            )
        )

        # 1. Imports
        import_matches = re.findall(r"['\"]([a-zA-Z0-9_\-\.\/]+)['\"]", content)
        for imp in import_matches:
            if "/" in imp and not imp.startswith("."):
                dep_name = imp.split("/")[-1]
                edges.append(
                    GraphEdge(
                        source=file_node_id,
                        target=f"dep:{dep_name}",
                        type=EdgeType.IMPORTS,
                        label=f"imports {imp}",
                    )
                )

        # 2. Public Functions (Starts with uppercase letter in Go)
        # func FuncName(params) returns
        # func (r *Receiver) FuncName(params) returns
        fn_pattern = re.compile(
            r"func\s+(?:\([^\)]+\)\s+)?([A-Z][a-zA-Z0-9_]*)\s*\(([^)]*)\)(?:\s+([^{]+))?"
        )
        for match in fn_pattern.finditer(content):
            fn_name = match.group(1)
            params = match.group(2) or ""
            ret_type = match.group(3) or ""
            line_num = content[: match.start()].count("\n") + 1

            fn_id = f"{rel_path}:{fn_name}"
            sig = f"func {fn_name}({params.strip()})" + (f" {ret_type.strip()}" if ret_type else "")
            skills.append(
                Skill(
                    id=f"skill:{fn_id}",
                    name=fn_name,
                    category=SkillCategory.CORE_FUNCTION,
                    description=f"Exported Go function `{fn_name}` in {path.name}",
                    location=f"{rel_path}:{line_num}",
                    signature=sig,
                    example_usage=f"result := {fn_name}(...)",
                    tags=["go", "function", "exported"],
                )
            )
            fn_node = GraphNode(
                id=fn_id,
                label=fn_name,
                type=NodeType.FUNCTION,
                file_path=rel_path,
                line=line_num,
                description=f"Go function {fn_name}",
            )
            nodes.append(fn_node)
            edges.append(GraphEdge(source=file_node_id, target=fn_id, type=EdgeType.EXPOSES))

        # 3. Public Types / Structs
        type_pattern = re.compile(r"type\s+([A-Z][a-zA-Z0-9_]*)\s+(struct|interface)")
        for match in type_pattern.finditer(content):
            type_name = match.group(1)
            kind = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            t_id = f"{rel_path}:{type_name}"

            category = SkillCategory.DATA_MODEL if kind == "struct" else SkillCategory.DOMAIN_SERVICE
            skills.append(
                Skill(
                    id=f"skill:{t_id}",
                    name=type_name,
                    category=category,
                    description=f"Exported Go {kind} `{type_name}`",
                    location=f"{rel_path}:{line_num}",
                    signature=f"type {type_name} {kind}",
                    tags=["go", kind],
                )
            )
            nodes.append(
                GraphNode(
                    id=t_id,
                    label=type_name,
                    type=NodeType.DATA_MODEL if kind == "struct" else NodeType.CLASS,
                    file_path=rel_path,
                    line=line_num,
                    description=f"Go {kind} {type_name}",
                )
            )
            edges.append(GraphEdge(source=file_node_id, target=t_id, type=EdgeType.EXPOSES))

        # 4. Gin / HTTP routes
        route_pattern = re.compile(r"\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
        for match in route_pattern.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            skill_id = f"go_api:{method}:{route_path}"
            skills.append(
                Skill(
                    id=skill_id,
                    name=f"API: {method} {route_path}",
                    category=SkillCategory.API_ENDPOINT,
                    description=f"Go HTTP route handler {method} {route_path}",
                    location=f"{rel_path}:{line_num}",
                    signature=f"{method} {route_path}",
                    example_usage=f"curl -X {method} http://localhost:8080{route_path}",
                    tags=["go", "api", method.lower()],
                )
            )
            ep_node = GraphNode(
                id=f"endpoint:{skill_id}",
                label=f"{method} {route_path}",
                type=NodeType.ENDPOINT,
                file_path=rel_path,
                line=line_num,
                description=f"Go endpoint {method} {route_path}",
            )
            nodes.append(ep_node)
            edges.append(GraphEdge(source=file_node_id, target=ep_node.id, type=EdgeType.EXPOSES))

        return skills, nodes, edges

    def _analyze_rust(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []

        nodes.append(
            GraphNode(
                id=file_node_id,
                label=path.name,
                type=NodeType.FILE,
                file_path=rel_path,
                description=f"Rust source file {path.name}",
            )
        )

        # 1. Pub functions
        fn_pattern = re.compile(
            r"pub\s+(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)(?:\s*->\s*([^{]+))?"
        )
        for match in fn_pattern.finditer(content):
            fn_name = match.group(1)
            params = match.group(2) or ""
            ret_type = match.group(3) or ""
            line_num = content[: match.start()].count("\n") + 1

            fn_id = f"{rel_path}:{fn_name}"
            sig = f"pub fn {fn_name}({params.strip()})" + (f" -> {ret_type.strip()}" if ret_type else "")
            skills.append(
                Skill(
                    id=f"skill:{fn_id}",
                    name=fn_name,
                    category=SkillCategory.CORE_FUNCTION,
                    description=f"Public Rust function `{fn_name}` in {path.name}",
                    location=f"{rel_path}:{line_num}",
                    signature=sig,
                    example_usage=f"let result = {fn_name}(...);",
                    tags=["rust", "function", "pub"],
                )
            )
            nodes.append(
                GraphNode(
                    id=fn_id,
                    label=fn_name,
                    type=NodeType.FUNCTION,
                    file_path=rel_path,
                    line=line_num,
                    description=f"Rust function {fn_name}",
                )
            )
            edges.append(GraphEdge(source=file_node_id, target=fn_id, type=EdgeType.EXPOSES))

        # 2. Pub Structs / Enums / Traits
        item_pattern = re.compile(r"pub\s+(struct|enum|trait)\s+([a-zA-Z0-9_]+)")
        for match in item_pattern.finditer(content):
            kind = match.group(1)
            name = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            item_id = f"{rel_path}:{name}"

            category = SkillCategory.DATA_MODEL if kind in ("struct", "enum") else SkillCategory.DOMAIN_SERVICE
            skills.append(
                Skill(
                    id=f"skill:{item_id}",
                    name=name,
                    category=category,
                    description=f"Public Rust {kind} `{name}`",
                    location=f"{rel_path}:{line_num}",
                    signature=f"pub {kind} {name}",
                    tags=["rust", kind],
                )
            )
            nodes.append(
                GraphNode(
                    id=item_id,
                    label=name,
                    type=NodeType.DATA_MODEL if kind in ("struct", "enum") else NodeType.CLASS,
                    file_path=rel_path,
                    line=line_num,
                    description=f"Rust {kind} {name}",
                )
            )
            edges.append(GraphEdge(source=file_node_id, target=item_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges

    def _analyze_java_kotlin(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills, nodes, edges = [], [], []

        nodes.append(
            GraphNode(
                id=file_node_id,
                label=path.name,
                type=NodeType.FILE,
                file_path=rel_path,
                description=f"Java/Kotlin source {path.name}",
            )
        )

        # Spring annotations: @GetMapping("/users"), @PostMapping("/items")
        spring_pattern = re.compile(
            r"@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?['\"]([^'\"]+)['\"]",
            re.IGNORECASE,
        )
        for match in spring_pattern.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            skill_id = f"spring_api:{method}:{route_path}"
            skills.append(
                Skill(
                    id=skill_id,
                    name=f"API: {method} {route_path}",
                    category=SkillCategory.API_ENDPOINT,
                    description=f"Spring REST controller mapping {method} {route_path}",
                    location=f"{rel_path}:{line_num}",
                    signature=f"@{method}Mapping(\"{route_path}\")",
                    example_usage=f"curl -X {method} http://localhost:8080{route_path}",
                    tags=["java", "spring", "api", method.lower()],
                )
            )
            ep_node = GraphNode(
                id=f"endpoint:{skill_id}",
                label=f"{method} {route_path}",
                type=NodeType.ENDPOINT,
                file_path=rel_path,
                line=line_num,
                description=f"Spring endpoint {method} {route_path}",
            )
            nodes.append(ep_node)
            edges.append(GraphEdge(source=file_node_id, target=ep_node.id, type=EdgeType.EXPOSES))

        # Public classes
        class_pattern = re.compile(r"public\s+(?:abstract\s+)?(class|interface|record)\s+([a-zA-Z0-9_]+)")
        for match in class_pattern.finditer(content):
            kind = match.group(1)
            name = match.group(2)
            line_num = content[: match.start()].count("\n") + 1
            cls_id = f"{rel_path}:{name}"

            skills.append(
                Skill(
                    id=f"skill:{cls_id}",
                    name=name,
                    category=SkillCategory.DOMAIN_SERVICE if kind != "record" else SkillCategory.DATA_MODEL,
                    description=f"Java {kind} `{name}`",
                    location=f"{rel_path}:{line_num}",
                    signature=f"public {kind} {name}",
                    tags=["java", kind],
                )
            )
            nodes.append(
                GraphNode(
                    id=cls_id,
                    label=name,
                    type=NodeType.CLASS if kind != "record" else NodeType.DATA_MODEL,
                    file_path=rel_path,
                    line=line_num,
                    description=f"Java {kind} {name}",
                )
            )
            edges.append(GraphEdge(source=file_node_id, target=cls_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges
