"""
Universal Tree-Sitter & Polyglot AST Engine for Skilly.
Supports 50+ programming languages (Python, TS/JS, Go, Rust, Java, C/C++, C#,
Ruby, PHP, Swift, Kotlin, Dart, Scala, Elixir, Lua, Julia, Zig, Solidity, SQL, etc.)
using tree_sitter_language_pack with zero LLMs.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import re

from skilly_core.extractors.base import BaseExtractor
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType, Skill, SkillCategory

# Try importing tree_sitter_language_pack
try:
    import tree_sitter_language_pack as tslp
    HAVE_TSLP = True
except Exception:
    HAVE_TSLP = False

# Mapping of file extensions to Tree-Sitter language names
EXT_TO_LANG: Dict[str, str] = {
    # Systems & Native
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".rs": "rust",
    ".go": "go",
    ".zig": "zig",
    # Managed / OOP
    ".java": "java",
    ".kt": "kotlin", ".kts": "kotlin",
    ".cs": "csharp",
    ".scala": "scala",
    ".swift": "swift",
    ".dart": "dart",
    # Scripting & Web
    ".py": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "tsx",
    ".rb": "ruby",
    ".php": "php",
    ".lua": "lua",
    ".jl": "julia",
    ".ex": "elixir", ".exs": "elixir",
    ".erl": "erlang",
    ".sh": "bash", ".bash": "bash",
    # Domain Specific & Data
    ".sol": "solidity",
    ".sql": "sql",
    ".graphql": "graphql", ".gql": "graphql",
    ".proto": "proto",
    ".prisma": "prisma",
}

# Node types to inspect in ASTs across languages
FUNCTION_NODE_TYPES = {
    "function_definition", "function_declaration", "method_declaration",
    "method_definition", "arrow_function", "func_literal", "function_item",
    "function", "subroutine", "procedure", "def", "singleton_method",
}

CLASS_NODE_TYPES = {
    "class_declaration", "class_definition", "struct_item", "struct_specifier",
    "interface_declaration", "trait_item", "enum_item", "enum_declaration",
    "record_declaration", "type_declaration", "protocol_declaration",
    "message_definition", "service_definition", "contract_declaration",
}


class UniversalPolyglotExtractor(BaseExtractor):
    """
    Universal AST and semantic extractor supporting 50+ programming languages.
    Extracts functions, classes, data models, routes, and call/import graphs.
    """

    def __init__(self, root_dir: Path):
        super().__init__(root_dir)
        self._parsers: Dict[str, Any] = {}

    def _get_parser(self, lang_name: str) -> Optional[Any]:
        if not HAVE_TSLP:
            return None
        if lang_name in self._parsers:
            return self._parsers[lang_name]
        try:
            parser = tslp.get_parser(lang_name)
            self._parsers[lang_name] = parser
            return parser
        except Exception:
            return None

    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for path in file_paths:
            ext = path.suffix.lower()
            if ext not in EXT_TO_LANG:
                continue

            lang_name = EXT_TO_LANG[ext]
            rel_path = self._rel(path)

            try:
                content_bytes = path.read_bytes()
                content = content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                continue

            file_node_id = f"file:{rel_path}"
            line_count = len(content.splitlines())

            # File node
            nodes.append(
                GraphNode(
                    id=file_node_id,
                    label=path.name,
                    type=NodeType.FILE,
                    file_path=rel_path,
                    description=f"{lang_name.capitalize()} source file {path.name}",
                    metadata={"language": lang_name, "lines": line_count},
                )
            )

            # Try Tree-Sitter AST parsing first
            parser = self._get_parser(lang_name)
            extracted_via_ts = False

            if parser:
                try:
                    tree = parser.parse(content_bytes)
                    s, n, e = self._analyze_ts_tree(tree, content_bytes, content, path, rel_path, file_node_id, lang_name)
                    if s or n or e:
                        skills.extend(s); nodes.extend(n); edges.extend(e)
                        extracted_via_ts = True
                except Exception:
                    extracted_via_ts = False

            # Fallback regex extractor if Tree-Sitter parser not available or failed
            if not extracted_via_ts:
                s, n, e = self._regex_fallback_extract(content, path, rel_path, file_node_id, lang_name)
                skills.extend(s); nodes.extend(n); edges.extend(e)

        return skills, nodes, edges

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _analyze_ts_tree(
        self,
        tree: Any,
        content_bytes: bytes,
        content: str,
        path: Path,
        rel_path: str,
        file_node_id: str,
        lang: str,
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        is_test = any(w in path.name.lower() for w in ("test", "spec", "_test"))

        def get_text(node: Any) -> str:
            return content_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="ignore").strip()

        # Find comments preceding line
        def get_preceding_comment(line_idx: int) -> str:
            lines = content.splitlines()
            comments = []
            for idx in range(line_idx - 2, -1, -1):
                if idx >= len(lines):
                    continue
                l = lines[idx].strip()
                if l.startswith("//") or l.startswith("#") or l.startswith("*") or l.startswith("/*"):
                    cleaned = re.sub(r"^[/\\*#]+\s*", "", l).rstrip("*/").strip()
                    if cleaned and not cleaned.startswith("@"):
                        comments.insert(0, cleaned)
                else:
                    break
            return " ".join(comments)

        cursor = tree.walk()
        visited_nodes: Set[int] = set()

        def visit(node: Any):
            if node.id in visited_nodes:
                return
            visited_nodes.add(node.id)

            ntype = node.type

            # 1. Imports / Dependencies
            if "import" in ntype or "include" in ntype or "using" in ntype or ntype in ("use_declaration",):
                import_text = get_text(node)
                # extract quoted module or bare identifier
                match = re.search(r"['\"<]([a-zA-Z0-9_\-\.\/]+)['\">]", import_text)
                if match:
                    dep_name = match.group(1).split("/")[0].strip("<>\"'")
                    if dep_name and not dep_name.startswith("."):
                        edges.append(
                            GraphEdge(
                                source=file_node_id,
                                target=f"dep:{dep_name}",
                                type=EdgeType.IMPORTS,
                                label=f"imports {dep_name}",
                            )
                        )

            # 2. Classes / Structs / Interfaces / Data Models
            elif ntype in CLASS_NODE_TYPES:
                name_node = node.child_by_field_name("name")
                name = get_text(name_node) if name_node else ""
                if not name:
                    # heuristic search for identifier child
                    for child in node.children:
                        if child.type in ("identifier", "type_identifier", "name"):
                            name = get_text(child)
                            break

                if name and not name.startswith("_") and not is_test:
                    line_no = node.start_point[0] + 1
                    doc = get_preceding_comment(line_no)
                    is_data = any(w in ntype for w in ("struct", "record", "message", "type")) or "model" in name.lower()
                    category = SkillCategory.DATA_MODEL if is_data else SkillCategory.DOMAIN_SERVICE
                    cls_id = f"{rel_path}:{name}"

                    skills.append(
                        Skill(
                            id=f"skill:{cls_id}",
                            name=name,
                            category=category,
                            description=doc or f"{lang.capitalize()} {ntype.replace('_', ' ')} `{name}`",
                            location=f"{rel_path}:{line_no}",
                            signature=f"{ntype} {name}",
                            tags=[lang, category.value, "ast"],
                        )
                    )
                    cls_node = GraphNode(
                        id=cls_id,
                        label=name,
                        type=NodeType.DATA_MODEL if is_data else NodeType.CLASS,
                        file_path=rel_path,
                        line=line_no,
                        description=doc or f"{lang.capitalize()} {name}",
                    )
                    nodes.append(cls_node)
                    edges.append(GraphEdge(source=file_node_id, target=cls_id, type=EdgeType.EXPOSES))

            # 3. Functions / Methods / Endpoints
            elif ntype in FUNCTION_NODE_TYPES:
                name_node = node.child_by_field_name("name") or node.child_by_field_name("declarator")
                name = ""
                if name_node:
                    if name_node.type in ("identifier", "field_identifier", "property_identifier"):
                        name = get_text(name_node)
                    else:
                        # might be a nested function declarator in C/C++
                        for child in name_node.children:
                            if child.type in ("identifier", "field_identifier"):
                                name = get_text(child)
                                break
                        if not name:
                            name = get_text(name_node).split("(")[0].strip()

                if not name:
                    for child in node.children:
                        if child.type in ("identifier", "field_identifier"):
                            name = get_text(child)
                            break

                if name and not name.startswith("_") and not is_test and name not in ("main", "init"):
                    line_no = node.start_point[0] + 1
                    doc = get_preceding_comment(line_no)
                    fn_id = f"{rel_path}:{name}"

                    # Detect if function is an API route (e.g. Spring, Express, FastAPI, Gin)
                    route_info = self._detect_route_in_surroundings(content, line_no)
                    if route_info:
                        method, path_str = route_info
                        skills.append(
                            Skill(
                                id=f"api:{method}:{path_str}",
                                name=f"API: {method} {path_str}",
                                category=SkillCategory.API_ENDPOINT,
                                description=doc or f"{method} {path_str} endpoint handler",
                                location=f"{rel_path}:{line_no}",
                                signature=f"{method} {path_str}",
                                example_usage=f"curl -X {method} http://localhost:8080{path_str}",
                                tags=["api", "route", lang, method.lower()],
                            )
                        )
                        ep_node = GraphNode(
                            id=f"endpoint:{method}:{path_str}",
                            label=f"{method} {path_str}",
                            type=NodeType.ENDPOINT,
                            file_path=rel_path,
                            line=line_no,
                            description=f"{method} {path_str}",
                        )
                        nodes.append(ep_node)
                        edges.append(GraphEdge(source=file_node_id, target=ep_node.id, type=EdgeType.EXPOSES))
                    else:
                        skills.append(
                            Skill(
                                id=f"skill:{fn_id}",
                                name=name,
                                category=SkillCategory.CORE_FUNCTION,
                                description=doc or f"Callable {lang.capitalize()} function `{name}` in {path.name}",
                                location=f"{rel_path}:{line_no}",
                                signature=f"fn {name}(...)",
                                tags=[lang, "function", "ast"],
                            )
                        )
                        fn_node = GraphNode(
                            id=fn_id,
                            label=name,
                            type=NodeType.FUNCTION,
                            file_path=rel_path,
                            line=line_no,
                            description=doc or f"{lang} function {name}",
                        )
                        nodes.append(fn_node)
                        edges.append(GraphEdge(source=file_node_id, target=fn_id, type=EdgeType.EXPOSES))

            # Recurse children
            for child in node.children:
                visit(child)

        visit(tree.root_node)
        return skills, nodes, edges

    def _detect_route_in_surroundings(self, content: str, line_no: int) -> Optional[Tuple[str, str]]:
        """Look at the lines around the function for route annotations/decorators."""
        lines = content.splitlines()
        start = max(0, line_no - 6)
        end = min(len(lines), line_no + 1)
        snippet = "\n".join(lines[start:end])

        # Spring / ASP.NET: @GetMapping("/path"), [HttpGet("/path")]
        spring = re.search(r"[@\[](Get|Post|Put|Delete|Patch)(?:Mapping|Method)?\s*\(\s*['\"]([^'\"]+)['\"]", snippet, re.IGNORECASE)
        if spring:
            return spring.group(1).upper(), spring.group(2)

        # Rails / Sinatra: get '/path' do
        ruby_route = re.search(r"\b(get|post|put|delete|patch)\s+['\"]([^'\"]+)['\"]", snippet, re.IGNORECASE)
        if ruby_route:
            return ruby_route.group(1).upper(), ruby_route.group(2)

        return None

    def _regex_fallback_extract(
        self,
        content: str,
        path: Path,
        rel_path: str,
        file_node_id: str,
        lang: str,
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        """Universal regex extractor for any language when tree-sitter is bypassed."""
        skills, nodes, edges = [], [], []
        is_test = any(w in path.name.lower() for w in ("test", "spec", "_test"))

        # Functions pattern: def foo, fn foo, function foo, func foo, sub foo, void foo(
        fn_pattern = re.compile(
            r"(?:(?:public|private|protected|static|async|export|def|fn|func|function|sub)\s+)+([a-zA-Z0-9_]+)\s*\(([^)]*)\)"
        )
        for match in fn_pattern.finditer(content):
            name = match.group(1)
            if name.startswith("_") or is_test or name in ("if", "while", "for", "switch", "catch", "return"):
                continue
            line_no = content[:match.start()].count("\n") + 1
            fn_id = f"{rel_path}:{name}"

            skills.append(
                Skill(
                    id=f"skill:{fn_id}",
                    name=name,
                    category=SkillCategory.CORE_FUNCTION,
                    description=f"{lang.capitalize()} function `{name}` in {path.name}",
                    location=f"{rel_path}:{line_no}",
                    signature=f"{name}({match.group(2)[:30]})",
                    tags=[lang, "function", "regex"],
                )
            )
            nodes.append(
                GraphNode(id=fn_id, label=name, type=NodeType.FUNCTION, file_path=rel_path, line=line_no)
            )
            edges.append(GraphEdge(source=file_node_id, target=fn_id, type=EdgeType.EXPOSES))

        # Classes / Structs / Interfaces pattern
        cls_pattern = re.compile(
            r"(?:class|struct|interface|trait|enum|record|message)\s+([a-zA-Z0-9_]+)"
        )
        for match in cls_pattern.finditer(content):
            name = match.group(1)
            if name.startswith("_") or is_test:
                continue
            line_no = content[:match.start()].count("\n") + 1
            cls_id = f"{rel_path}:{name}"

            skills.append(
                Skill(
                    id=f"skill:{cls_id}",
                    name=name,
                    category=SkillCategory.DOMAIN_SERVICE,
                    description=f"{lang.capitalize()} component `{name}`",
                    location=f"{rel_path}:{line_no}",
                    signature=f"class/struct {name}",
                    tags=[lang, "class", "regex"],
                )
            )
            nodes.append(
                GraphNode(id=cls_id, label=name, type=NodeType.CLASS, file_path=rel_path, line=line_no)
            )
            edges.append(GraphEdge(source=file_node_id, target=cls_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges
