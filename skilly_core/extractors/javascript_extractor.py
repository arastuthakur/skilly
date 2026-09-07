"""
JavaScript and TypeScript extractor for Skilly.
Extracts REST routes (Express, Fastify, Next.js App Router), exported functions,
classes, interfaces, types, imports, and JSDoc comments.
Purely deterministic, zero LLM.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from skilly_core.extractors.base import BaseExtractor
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType, Skill, SkillCategory

# Try importing tree_sitter if available
try:
    from tree_sitter import Language, Parser
    import tree_sitter_javascript as ts_js
    import tree_sitter_typescript as ts_ts
    HAVE_TREE_SITTER = True
except Exception:
    HAVE_TREE_SITTER = False


class JavaScriptExtractor(BaseExtractor):
    """Analyzes JS/TS files for skills, exports, API routes, and dependency graphs."""

    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        js_exts = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
        target_files = [p for p in file_paths if p.suffix.lower() in js_exts]

        for path in target_files:
            # Skip node_modules, build outputs, or dist if accidentally passed
            rel_parts = path.parts
            if any(p in ("node_modules", "dist", "build", ".next", "out", "coverage") for p in rel_parts):
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            rel_path = self._rel(path)
            file_node_id = f"file:{rel_path}"

            # File node
            nodes.append(
                GraphNode(
                    id=file_node_id,
                    label=path.name,
                    type=NodeType.FILE,
                    file_path=rel_path,
                    description=f"JavaScript/TypeScript source {path.name}",
                    metadata={"lines": len(content.splitlines())},
                )
            )

            file_skills, file_nodes, file_edges = self._analyze_content(content, path, rel_path, file_node_id)
            skills.extend(file_skills)
            nodes.extend(file_nodes)
            edges.extend(file_edges)

        return skills, nodes, edges

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _analyze_content(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        is_test = any(w in path.name.lower() for w in (".test.", ".spec.", "_test", "-test"))

        # 1. Extract Imports (ESM & CommonJS)
        import_edges = self._extract_imports(content, file_node_id)
        edges.extend(import_edges)

        # 2. Extract Next.js App Router handlers (app/api/.../route.ts or page.tsx)
        if "app" in rel_path.split("/") and ("route." in path.name or "page." in path.name):
            next_skills, next_nodes = self._detect_nextjs_routes(content, path, rel_path, file_node_id)
            skills.extend(next_skills)
            nodes.extend(next_nodes)

        # 3. Extract Express / Fastify / Koa routes (e.g. app.get('/path', ...))
        route_skills, route_nodes, route_edges = self._detect_express_routes(content, path, rel_path, file_node_id)
        skills.extend(route_skills)
        nodes.extend(route_nodes)
        edges.extend(route_edges)

        # 4. Extract Exported Functions
        fn_skills, fn_nodes, fn_edges = self._extract_exported_functions(content, path, rel_path, file_node_id, is_test)
        skills.extend(fn_skills)
        nodes.extend(fn_nodes)
        edges.extend(fn_edges)

        # 5. Extract Exported Classes and Interfaces / Types
        cls_skills, cls_nodes, cls_edges = self._extract_exported_classes_and_types(content, path, rel_path, file_node_id, is_test)
        skills.extend(cls_skills)
        nodes.extend(cls_nodes)
        edges.extend(cls_edges)

        return skills, nodes, edges

    def _extract_imports(self, content: str, file_node_id: str) -> List[GraphEdge]:
        edges = []
        # ESM: import ... from 'package'
        esm_matches = re.findall(r"import\s+(?:[\w\s{},*]+)\s+from\s+['\"]([^'\"]+)['\"]", content)
        # CommonJS: require('package')
        cjs_matches = re.findall(r"require\(\s*['\"]([^'\"]+)['\"]\s*\)", content)

        all_imports = set(esm_matches + cjs_matches)
        for imp in all_imports:
            if imp.startswith("."):
                # Internal relative import
                continue
            pkg = imp.split("/")[0] if not imp.startswith("@") else "/".join(imp.split("/")[:2])
            edges.append(
                GraphEdge(
                    source=file_node_id,
                    target=f"dep:{pkg}",
                    type=EdgeType.IMPORTS,
                    label=f"imports {pkg}",
                )
            )
        return edges

    def _detect_nextjs_routes(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode]]:
        skills = []
        nodes = []
        # In Next.js app router: export async function GET(req)
        http_verbs = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]
        for verb in http_verbs:
            pattern = rf"export\s+(?:async\s+)?function\s+{verb}\s*\("
            if re.search(pattern, content):
                # Infer route path from file directory
                route_dir = rel_path.split("app")[-1].rsplit("/", 1)[0]
                if not route_dir:
                    route_dir = "/"
                skill_id = f"next_api:{verb}:{route_dir}"
                skills.append(
                    Skill(
                        id=skill_id,
                        name=f"API: {verb} {route_dir}",
                        category=SkillCategory.API_ENDPOINT,
                        description=f"Next.js App Router API endpoint for {verb} {route_dir}",
                        location=f"{rel_path}",
                        signature=f"export async function {verb}(request: Request)",
                        example_usage=f"fetch('{route_dir}', {{ method: '{verb}' }})",
                        tags=["api", "nextjs", verb.lower()],
                        metadata={"framework": "nextjs", "method": verb, "route": route_dir},
                    )
                )
                nodes.append(
                    GraphNode(
                        id=f"endpoint:{skill_id}",
                        label=f"{verb} {route_dir}",
                        type=NodeType.ENDPOINT,
                        file_path=rel_path,
                        description=f"Next.js {verb} handler",
                    )
                )
        return skills, nodes

    def _detect_express_routes(
        self, content: str, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills = []
        nodes = []
        edges = []

        # Matches: app.get('/api/users', ...), router.post('/login', ...)
        route_pattern = re.compile(
            r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
            re.IGNORECASE,
        )

        for match in route_pattern.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            line_num = content[: match.start()].count("\n") + 1

            skill_id = f"api:{method}:{route_path}"
            skills.append(
                Skill(
                    id=skill_id,
                    name=f"API: {method} {route_path}",
                    category=SkillCategory.API_ENDPOINT,
                    description=f"Express/Node route handler for {method} {route_path}",
                    location=f"{rel_path}:{line_num}",
                    signature=f"{method.lower()}('{route_path}', handler)",
                    example_usage=f"curl -X {method} http://localhost:3000{route_path}",
                    tags=["api", "express", method.lower()],
                    metadata={"framework": "express", "method": method, "path": route_path},
                )
            )

            ep_node = GraphNode(
                id=f"endpoint:{skill_id}",
                label=f"{method} {route_path}",
                type=NodeType.ENDPOINT,
                file_path=rel_path,
                line=line_num,
                description=f"REST endpoint {method} {route_path}",
            )
            nodes.append(ep_node)
            edges.append(GraphEdge(source=file_node_id, target=ep_node.id, type=EdgeType.EXPOSES))

        return skills, nodes, edges

    def _extract_exported_functions(
        self, content: str, path: Path, rel_path: str, file_node_id: str, is_test: bool
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills = []
        nodes = []
        edges = []

        # Matches:
        # export function foo(a, b)
        # export async function foo(a, b)
        # export const foo = (a, b) =>
        # export const foo = async (a, b) =>
        fn_pattern = re.compile(
            r"(?:\/\*\*([\s\S]*?)\*\/[\s\n]*)?export\s+(?:default\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_$]+)\s*\(([^)]*)\)"
        )
        arrow_pattern = re.compile(
            r"(?:\/\*\*([\s\S]*?)\*\/[\s\n]*)?export\s+const\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>"
        )

        matches = list(fn_pattern.finditer(content)) + list(arrow_pattern.finditer(content))

        for match in matches:
            jsdoc_raw = match.group(1) or ""
            fn_name = match.group(2)
            params_raw = match.group(3)
            line_num = content[: match.start()].count("\n") + 1

            if fn_name.startswith("_") or is_test:
                continue

            jsdoc_desc = ""
            if jsdoc_raw:
                # clean up jsdoc comments
                cleaned_lines = [
                    re.sub(r"^\s*\*?\s?", "", l).strip()
                    for l in jsdoc_raw.splitlines()
                    if not l.strip().startswith("@") and re.sub(r"^\s*\*?\s?", "", l).strip()
                ]
                jsdoc_desc = " ".join(cleaned_lines)

            fn_id = f"{rel_path}:{fn_name}"
            sig = f"export function {fn_name}({params_raw.strip()})"
            desc = jsdoc_desc or f"Exported function `{fn_name}` in {path.name}"

            # Parameters breakdown
            params_list = []
            for p in params_raw.split(","):
                p = p.strip()
                if p:
                    p_name = p.split(":")[0].strip()
                    p_type = p.split(":")[1].strip() if ":" in p else None
                    params_list.append({"name": p_name, "type": p_type})

            skills.append(
                Skill(
                    id=f"skill:{fn_id}",
                    name=fn_name,
                    category=SkillCategory.CORE_FUNCTION,
                    description=desc,
                    location=f"{rel_path}:{line_num}",
                    signature=sig,
                    parameters=params_list,
                    example_usage=f"import {{ {fn_name} }} from './{path.stem}';\nconst result = {fn_name}(...);",
                    tags=["javascript", "typescript", "function"],
                    metadata={"jsdoc": jsdoc_desc},
                )
            )

            fn_node = GraphNode(
                id=fn_id,
                label=fn_name,
                type=NodeType.FUNCTION,
                file_path=rel_path,
                line=line_num,
                description=desc,
            )
            nodes.append(fn_node)
            edges.append(GraphEdge(source=file_node_id, target=fn_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges

    def _extract_exported_classes_and_types(
        self, content: str, path: Path, rel_path: str, file_node_id: str, is_test: bool
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills = []
        nodes = []
        edges = []

        # Classes: export class AuthService extends BaseService
        cls_pattern = re.compile(
            r"(?:\/\*\*([\s\S]*?)\*\/[\s\n]*)?export\s+(?:default\s+)?class\s+([a-zA-Z0-9_$]+)(?:\s+extends\s+([a-zA-Z0-9_$]+))?"
        )
        for match in cls_pattern.finditer(content):
            jsdoc_raw = match.group(1) or ""
            cls_name = match.group(2)
            base_cls = match.group(3)
            line_num = content[: match.start()].count("\n") + 1

            if is_test:
                continue

            desc = f"Class {cls_name}" + (f" extending {base_cls}" if base_cls else "")
            cls_id = f"{rel_path}:{cls_name}"

            skills.append(
                Skill(
                    id=f"skill:{cls_id}",
                    name=cls_name,
                    category=SkillCategory.DOMAIN_SERVICE,
                    description=desc,
                    location=f"{rel_path}:{line_num}",
                    signature=f"class {cls_name}" + (f" extends {base_cls}" if base_cls else ""),
                    example_usage=f"import {{ {cls_name} }} from './{path.stem}';\nconst instance = new {cls_name}();",
                    tags=["class", "service"],
                )
            )

            node = GraphNode(
                id=cls_id,
                label=cls_name,
                type=NodeType.CLASS,
                file_path=rel_path,
                line=line_num,
                description=desc,
            )
            nodes.append(node)
            edges.append(GraphEdge(source=file_node_id, target=cls_id, type=EdgeType.EXPOSES))
            if base_cls:
                edges.append(GraphEdge(source=cls_id, target=f"class:{base_cls}", type=EdgeType.INHERITS))

        # TypeScript Interfaces & Types: export interface User / export type Config
        type_pattern = re.compile(r"export\s+(?:interface|type)\s+([a-zA-Z0-9_$]+)")
        for match in type_pattern.finditer(content):
            type_name = match.group(1)
            line_num = content[: match.start()].count("\n") + 1
            t_id = f"{rel_path}:{type_name}"

            skills.append(
                Skill(
                    id=f"skill:{t_id}",
                    name=type_name,
                    category=SkillCategory.DATA_MODEL,
                    description=f"TypeScript data model / type interface '{type_name}'",
                    location=f"{rel_path}:{line_num}",
                    signature=f"export type/interface {type_name}",
                    tags=["typescript", "interface", "schema"],
                )
            )

            node = GraphNode(
                id=t_id,
                label=type_name,
                type=NodeType.DATA_MODEL,
                file_path=rel_path,
                line=line_num,
                description=f"Type interface {type_name}",
            )
            nodes.append(node)
            edges.append(GraphEdge(source=file_node_id, target=t_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges
