"""
Deep Python AST extractor.
Parses Python source code using the standard library ast module.
Extracts classes, data models, functions, REST API endpoints (FastAPI, Flask, Django),
CLI commands (Click, Typer, Argparse), call graphs, imports, and docstrings.
Purely deterministic, zero LLM.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from skilly_core.extractors.base import BaseExtractor
from skilly_core.models import EdgeType, GraphEdge, GraphNode, NodeType, Skill, SkillCategory


class PythonASTExtractor(BaseExtractor):
    """Analyzes Python files for skills, AST symbols, API routes, and relationships."""

    def extract(self, file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        py_files = [p for p in file_paths if p.suffix.lower() == ".py"]

        for path in py_files:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=str(path))
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
                    description=f"Python source file {path.name}",
                    metadata={"lines": len(content.splitlines())},
                )
            )

            file_skills, file_nodes, file_edges = self._analyze_file_ast(tree, path, rel_path, file_node_id)
            skills.extend(file_skills)
            nodes.extend(file_nodes)
            edges.extend(file_edges)

        return skills, nodes, edges

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root_dir)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    def _resolve_python_import(self, current_file: Path, module_name: Optional[str], level: int = 0) -> Optional[str]:
        """Resolves a Python module import (absolute or relative) to an internal file path."""
        # 1. Relative import (level > 0)
        if level > 0:
            base_dir = current_file.parent
            for _ in range(level - 1):
                base_dir = base_dir.parent
            if not module_name:
                init_cand = base_dir / "__init__.py"
                if init_cand.is_file():
                    return self._rel(init_cand)
                return None
            rel_parts = module_name.split(".")
            cand_py = base_dir.joinpath(*rel_parts).with_suffix(".py")
            if cand_py.is_file():
                return self._rel(cand_py)
            cand_init = base_dir.joinpath(*rel_parts) / "__init__.py"
            if cand_init.is_file():
                return self._rel(cand_init)
            return None

        # 2. Absolute import (level == 0)
        if not module_name:
            return None

        parts = module_name.split(".")
        for search_root in (current_file.parent, self.root_dir, self.root_dir / "src"):
            cand_py = search_root.joinpath(*parts).with_suffix(".py")
            if cand_py.is_file():
                return self._rel(cand_py)
            cand_init = search_root.joinpath(*parts) / "__init__.py"
            if cand_init.is_file():
                return self._rel(cand_init)

            for i in range(len(parts) - 1, 0, -1):
                sub_parts = parts[:i]
                cand_sub = search_root.joinpath(*sub_parts).with_suffix(".py")
                if cand_sub.is_file():
                    return self._rel(cand_sub)
                cand_sub_init = search_root.joinpath(*sub_parts) / "__init__.py"
                if cand_sub_init.is_file():
                    return self._rel(cand_sub_init)

        return None

    def _analyze_file_ast(
        self, tree: ast.AST, path: Path, rel_path: str, file_node_id: str
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        is_test_file = "test" in path.name.lower() or "tests" in rel_path.lower().split("/")

        # Track imports
        imported_symbols: Dict[str, str] = {}  # alias/symbol -> module

        for node in ast.iter_child_nodes(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dep_name = alias.name.split(".")[0]
                    imported_symbols[alias.asname or alias.name] = alias.name
                    internal_path = self._resolve_python_import(path, alias.name, level=0)
                    target_id = f"file:{internal_path}" if internal_path else f"dep:{dep_name}"

                    edges.append(
                        GraphEdge(
                            source=file_node_id,
                            target=target_id,
                            type=EdgeType.IMPORTS,
                            label=f"imports {alias.name}",
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                mod_name = node.module or ""
                level = getattr(node, "level", 0)
                dep_name = mod_name.split(".")[0] if mod_name else ""
                for alias in node.names:
                    imported_symbols[alias.asname or alias.name] = f"{mod_name}.{alias.name}" if mod_name else alias.name

                internal_path = self._resolve_python_import(path, mod_name, level=level)
                if internal_path:
                    target_id = f"file:{internal_path}"
                elif dep_name:
                    target_id = f"dep:{dep_name}"
                else:
                    target_id = None

                if target_id:
                    prefix = "." * level
                    edges.append(
                        GraphEdge(
                            source=file_node_id,
                            target=target_id,
                            type=EdgeType.IMPORTS,
                            label=f"from {prefix}{mod_name} import ...",
                        )
                    )

            # Classes
            elif isinstance(node, ast.ClassDef):
                cls_skills, cls_nodes, cls_edges = self._analyze_class(node, rel_path, file_node_id, is_test_file)
                skills.extend(cls_skills)
                nodes.extend(cls_nodes)
                edges.extend(cls_edges)

            # Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_skills, fn_nodes, fn_edges = self._analyze_function(
                    node, rel_path, file_node_id, parent_class=None, is_test_file=is_test_file
                )
                skills.extend(fn_skills)
                nodes.extend(fn_nodes)
                edges.extend(fn_edges)

        return skills, nodes, edges

    def _analyze_class(
        self, node: ast.ClassDef, rel_path: str, file_node_id: str, is_test_file: bool
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        cls_name = node.name
        docstring = ast.get_docstring(node) or ""
        first_doc_line = docstring.strip().split("\n")[0] if docstring else ""

        # Extract base classes
        bases: List[str] = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)

        is_data_model = any(
            b in ("BaseModel", "Base", "Model", "Schema", "NamedTuple", "TypedDict") for b in bases
        ) or any(self._is_dataclass_decorator(d) for d in node.decorator_list)

        node_type = NodeType.DATA_MODEL if is_data_model else NodeType.CLASS
        class_node_id = f"{rel_path}:{cls_name}"

        # Class node
        class_node = GraphNode(
            id=class_node_id,
            label=cls_name,
            type=node_type,
            file_path=rel_path,
            line=node.lineno,
            description=first_doc_line or f"Class {cls_name} ({', '.join(bases) if bases else 'base'})",
            metadata={"bases": bases, "is_data_model": is_data_model},
        )
        nodes.append(class_node)
        edges.append(GraphEdge(source=file_node_id, target=class_node_id, type=EdgeType.EXPOSES))

        for b in bases:
            edges.append(GraphEdge(source=class_node_id, target=f"class:{b}", type=EdgeType.INHERITS, label=f"extends {b}"))

        # If not private or test, register as a skill
        if not cls_name.startswith("_") and not is_test_file:
            category = SkillCategory.DATA_MODEL if is_data_model else SkillCategory.DOMAIN_SERVICE
            desc = first_doc_line or f"{'Data model / schema' if is_data_model else 'Service / component'} '{cls_name}'"
            skills.append(
                Skill(
                    id=f"skill:{class_node_id}",
                    name=cls_name,
                    category=category,
                    description=desc,
                    location=f"{rel_path}:{node.lineno}",
                    signature=f"class {cls_name}({', '.join(bases)}):",
                    example_usage=f"from {rel_path.replace('/', '.').removesuffix('.py')} import {cls_name}\ninstance = {cls_name}()",
                    tags=["python", "class", "model" if is_data_model else "service"],
                    metadata={"bases": bases, "docstring": docstring},
                )
            )

        # Analyze methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_skills, fn_nodes, fn_edges = self._analyze_function(
                    item, rel_path, file_node_id, parent_class=cls_name, is_test_file=is_test_file
                )
                skills.extend(fn_skills)
                nodes.extend(fn_nodes)
                edges.extend(fn_edges)
                # Link method to class
                method_id = f"{rel_path}:{cls_name}.{item.name}"
                edges.append(GraphEdge(source=class_node_id, target=method_id, type=EdgeType.EXPOSES))

        return skills, nodes, edges

    def _analyze_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        rel_path: str,
        file_node_id: str,
        parent_class: Optional[str] = None,
        is_test_file: bool = False,
    ) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]:
        skills: List[Skill] = []
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        fn_name = node.name
        full_name = f"{parent_class}.{fn_name}" if parent_class else fn_name
        docstring = ast.get_docstring(node) or ""
        first_doc_line = docstring.strip().split("\n")[0] if docstring else ""

        # Signature & arguments
        params = self._extract_parameters(node.args)
        ret_type = self._extract_return_annotation(node.returns)
        is_async = isinstance(node, ast.AsyncFunctionDef)
        prefix = "async def" if is_async else "def"
        sig = f"{prefix} {fn_name}({', '.join(p['name'] + (': ' + p['type'] if p.get('type') else '') for p in params)})"
        if ret_type:
            sig += f" -> {ret_type}"

        # Decorator analysis: API route detection (FastAPI, Flask, etc.)
        route_info = self._detect_api_route(node.decorator_list)
        cli_info = self._detect_cli_command(node.decorator_list, fn_name)

        fn_node_id = f"{rel_path}:{full_name}"
        node_type = NodeType.ENDPOINT if route_info else (NodeType.CLI if cli_info else NodeType.FUNCTION)

        # Graph node
        desc = route_info["summary"] if route_info else (first_doc_line or f"Function {full_name}")
        fn_node = GraphNode(
            id=fn_node_id,
            label=full_name,
            type=node_type,
            file_path=rel_path,
            line=node.lineno,
            description=desc,
            metadata={"is_async": is_async, "signature": sig, "params": params, "returns": ret_type},
        )
        nodes.append(fn_node)
        edges.append(GraphEdge(source=file_node_id, target=fn_node_id, type=EdgeType.EXPOSES))

        # Skill generation
        if route_info:
            # REST API Route Skill
            method = route_info["method"]
            path_str = route_info["path"]
            skills.append(
                Skill(
                    id=f"api:{method}:{path_str}",
                    name=f"API: {method} {path_str}",
                    category=SkillCategory.API_ENDPOINT,
                    description=first_doc_line or f"API endpoint handler for {method} {path_str}",
                    location=f"{rel_path}:{node.lineno}",
                    signature=sig,
                    parameters=params,
                    return_type=ret_type,
                    example_usage=f"curl -X {method} http://localhost:8000{path_str}",
                    tags=["api", "route", method.lower(), "fastapi/flask"],
                    metadata={"http_method": method, "path": path_str, "handler": full_name},
                )
            )
        elif cli_info:
            # CLI Command Skill
            cmd_name = cli_info.get("name", fn_name)
            skills.append(
                Skill(
                    id=f"cli:{cmd_name}",
                    name=f"CLI: {cmd_name}",
                    category=SkillCategory.COMMAND,
                    description=first_doc_line or f"Command-line tool command '{cmd_name}'",
                    location=f"{rel_path}:{node.lineno}",
                    signature=sig,
                    parameters=params,
                    example_usage=f"{cmd_name} --help",
                    tags=["cli", "command", cmd_name],
                    metadata={"cli_framework": cli_info.get("framework")},
                )
            )
        elif not fn_name.startswith("_") and not is_test_file and fn_name not in ("setUp", "tearDown"):
            # Public Core Function Skill (prioritize functions with docstrings or meaningful names)
            if docstring or len(node.body) > 3 or parent_class is None:
                category = SkillCategory.DOMAIN_SERVICE if parent_class else SkillCategory.CORE_FUNCTION
                module_import = rel_path.replace("/", ".").removesuffix(".py")
                skills.append(
                    Skill(
                        id=f"skill:{fn_node_id}",
                        name=full_name,
                        category=category,
                        description=first_doc_line or f"Function `{full_name}` in {rel_path}",
                        location=f"{rel_path}:{node.lineno}",
                        signature=sig,
                        parameters=params,
                        return_type=ret_type,
                        example_usage=f"from {module_import} import {fn_name}\nresult = {fn_name}(...)",
                        tags=["python", "function", "async" if is_async else "sync"],
                        metadata={"docstring": docstring},
                    )
                )

        # Call graph extraction: find calls inside function body
        calls = self._extract_calls(node)
        for called in calls:
            edges.append(
                GraphEdge(
                    source=fn_node_id,
                    target=called,
                    type=EdgeType.CALLS,
                    label="calls",
                )
            )

        return skills, nodes, edges

    def _extract_parameters(self, args: ast.arguments) -> List[Dict[str, Any]]:
        params: List[Dict[str, Any]] = []
        for arg in args.args:
            if arg.arg in ("self", "cls"):
                continue
            type_str = ast.unparse(arg.annotation) if arg.annotation else None
            params.append({"name": arg.arg, "type": type_str})
        return params

    def _extract_return_annotation(self, ret: Optional[ast.expr]) -> Optional[str]:
        if ret is None:
            return None
        try:
            return ast.unparse(ret)
        except Exception:
            return None

    def _detect_api_route(self, decorators: List[ast.expr]) -> Optional[Dict[str, str]]:
        """Detects FastAPI / Flask / Starlette / Bottle route decorators."""
        http_methods = {"get", "post", "put", "delete", "patch", "options", "head"}
        for dec in decorators:
            # e.g., @app.get("/users") or @router.post("/items")
            if isinstance(dec, ast.Call):
                func = dec.func
                method = ""
                if isinstance(func, ast.Attribute) and func.attr.lower() in http_methods:
                    method = func.attr.upper()
                elif isinstance(func, ast.Attribute) and func.attr.lower() == "route":
                    method = "GET"  # default Flask
                    for kw in dec.keywords:
                        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                            methods_list = [ast.literal_eval(elt) for elt in kw.value.elts if isinstance(elt, ast.Constant)]
                            if methods_list:
                                method = "/".join(methods_list)

                if method:
                    route_path = "/"
                    if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                        route_path = dec.args[0].value
                    return {"method": method, "path": route_path, "summary": f"{method} {route_path}"}
        return None

    def _detect_cli_command(self, decorators: List[ast.expr], fn_name: str) -> Optional[Dict[str, str]]:
        """Detects Click / Typer CLI command decorators."""
        for dec in decorators:
            # @click.command(), @app.command()
            target_attr = ""
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                target_attr = dec.func.attr
            elif isinstance(dec, ast.Attribute):
                target_attr = dec.attr

            if target_attr in ("command", "group"):
                return {"name": fn_name.replace("_", "-"), "framework": "click/typer"}
        return None

    def _is_dataclass_decorator(self, dec: ast.expr) -> bool:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            return True
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == "dataclass":
            return True
        return False

    def _extract_calls(self, func_node: ast.AST) -> Set[str]:
        calls = set()
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        return calls
