---
project: "Model"
total_skills: 148
languages: ['PowerShell', 'Shell', 'HTML', 'Python', 'JavaScript', 'Ruby', 'Java', 'C', 'Solidity']
frameworks: ['Click CLI', 'Docker', 'Express.js', 'FastAPI', 'Jest', 'Make', 'Pydantic', 'Spring Boot']
generator: "skilly (deterministic LLM-free AST analyzer)"
---

# Project Skills & Capabilities: Model

> Auto-generated capability catalog extracted via static AST and manifest context.

## 📊 Repository Capabilities Overview

| Metric | Count / Detail |
| :--- | :--- |
| **Architecture Health Grade** | `B` (85/100 - Grade B (85/100): 1 circular dependency cycles detected.) |
| **Primary Languages** | PowerShell (1 files), Shell (1 files), HTML (3 files), Python (35 files), JavaScript (1 files), Ruby (1 files), Java (1 files), C (1 files), Solidity (1 files) |
| **Frameworks / Tooling** | Click CLI, Docker, Express.js, FastAPI, Jest, Make, Pydantic, Spring Boot |
| **Total Skills Cataloged** | `148` |
| **Knowledge Graph Entities** | `495 nodes, 1215 edges` |
| **Runnable Commands & Workflows** | `15` |
| **API Endpoints** | `6` |
| **Domain Services & Models** | `77` |

## 📑 Table of Contents
- [1. Runnable Commands & CLI Workflows](#1-runnable-commands--cli-workflows)
- [2. API Endpoints & Routes](#2-api-endpoints--routes)
- [3. Domain Services & Key Controllers](#3-domain-services--key-controllers)
- [4. Data Models & Schemas](#4-data-models--schemas)
- [5. Core Exported Functions & Utilities](#5-core-exported-functions--utilities)
- [6. Environment & Configuration](#6-environment--configuration)
- [7. Architectural Hubs & Central Components](#7-architectural-hubs--central-components)

## 1. Runnable Commands & CLI Workflows

| Command / Skill | Type | Description | Location | Usage Example |
| :--- | :--- | :--- | :--- | :--- |
| **npm run start** | `CLI Command` | Run npm script 'start': `node ./bin/skilly-node.js` | `package.json:scripts.start` | `npm start` |
| **cli: skilly** | `CLI Command` | Executable binary 'skilly' -> ./bin/skilly-node.js | `package.json:bin.skilly` | `npx skilly` |
| **CLI: skilly** | `CLI Command` | Console script entry point: skilly_core.cli:main | `pyproject.toml:scripts.skilly` | `skilly --help` |
| **CLI: skilly** | `CLI Command` | Console script entry point: skilly_core.cli:main | `setup.py` | `skilly --help` |
| **npm run start** | `CLI Command` | Run npm script 'start': `node server.js` | `tests/fixtures/sample_node_app/package.json:scripts.start` | `npm start` |
| **npm run dev** | `CLI Command` | Run npm script 'dev': `nodemon server.js` | `tests/fixtures/sample_node_app/package.json:scripts.dev` | `npm run dev` |
| **make run** | `CLI Command` | Run development server | `tests/fixtures/sample_python_app/Makefile:4` | `make run` |
| **CLI: run-server** | `CLI Command` | Launch production server instance. | `tests/fixtures/sample_python_app/main.py:25` | `run-server --help` |
| **docker compose up** | `Workflow` | Start containerized services defined in docker-compose | `docker-compose.yml` | `docker compose up -d` |
| **docker build** | `Workflow` | Build Docker container image from Dockerfile | `Dockerfile` | `docker build -t app .` |
| **npm run test** | `Workflow` | Run npm script 'test': `python -m pytest tests/ -v` | `package.json:scripts.test` | `npm test` |
| **npm run test** | `Workflow` | Run npm script 'test': `jest` | `tests/fixtures/sample_node_app/package.json:scripts.test` | `npm test` |
| **npm run build** | `Workflow` | Run npm script 'build': `tsc` | `tests/fixtures/sample_node_app/package.json:scripts.build` | `npm run build` |
| **make test** | `Workflow` | Execute test suite | `tests/fixtures/sample_python_app/Makefile:8` | `make test` |
| **make lint** | `Workflow` | Run linter | `tests/fixtures/sample_python_app/Makefile:12` | `make lint` |

### Command Execution Cheat-Sheet
```bash
# Run npm script 'start': `node ./bin/skilly-node.js`
npm start

# Executable binary 'skilly' -> ./bin/skilly-node.js
npx skilly

# Console script entry point: skilly_core.cli:main
skilly --help

# Console script entry point: skilly_core.cli:main
skilly --help

# Run npm script 'start': `node server.js`
npm start

# Run npm script 'dev': `nodemon server.js`
npm run dev

# Run development server
make run

# Launch production server instance.
run-server --help

# Start containerized services defined in docker-compose
docker compose up -d

# Build Docker container image from Dockerfile
docker build -t app .

# Run npm script 'test': `python -m pytest tests/ -v`
npm test

# Run npm script 'test': `jest`
npm test

# Run npm script 'build': `tsc`
npm run build

# Execute test suite
make test

# Run linter
make lint

```

## 2. API Endpoints & Routes

| HTTP Method & Route | Description | Handler / Location | Quick Curl Invocation |
| :--- | :--- | :--- | :--- |
| **API: POST /api/v1/auth/login** | Authenticate user and return JWT access token. | `tests/fixtures/sample_python_app/main.py:13` | `curl -X POST http://localhost:8000/api/v1/auth/login` |
| **API: GET /api/v1/health** | Service health inspection endpoint. | `tests/fixtures/sample_python_app/main.py:19` | `curl -X GET http://localhost:8000/api/v1/health` |
| **API: GET /api/users** | Express/Node route handler for GET /api/users | `tests/fixtures/sample_node_app/server.js:4` | `curl -X GET http://localhost:3000/api/users` |
| **API: POST /api/users** | Express/Node route handler for POST /api/users | `tests/fixtures/sample_node_app/server.js:8` | `curl -X POST http://localhost:3000/api/users` |
| **API: GET /api/v1/catalog/items** | Spring REST controller mapping GET /api/v1/catalog/items | `tests/fixtures/sample_polyglot_app/ItemController.java:9` | `curl -X GET http://localhost:8080/api/v1/catalog/items` |
| **API: GET /api/v1/catalog/items** | GET /api/v1/catalog/items endpoint handler | `tests/fixtures/sample_polyglot_app/ItemController.java:9` | `curl -X GET http://localhost:8080/api/v1/catalog/items` |

## 3. Domain Services & Key Controllers

### `ProjectAnalyzer`
- **Role**: Orchestrates whole-project capability extraction and knowledge graph synthesis.
- **Location**: [`skilly_core/analyzer.py:134`](skilly_core/analyzer.py:134)
- **Signature**: `class ProjectAnalyzer():`
```python
from skilly_core.analyzer import ProjectAnalyzer
instance = ProjectAnalyzer()
```

### `ProjectAnalyzer.scan_files`
- **Role**: Walks the directory and collects all relevant source and manifest files.
- **Location**: [`skilly_core/analyzer.py:144`](skilly_core/analyzer.py:144)
- **Signature**: `def scan_files() -> List[Path]`
```python
from skilly_core.analyzer import scan_files
result = scan_files(...)
```

### `ProjectAnalyzer.analyze`
- **Role**: Runs all extractors and graph algorithms to produce ProjectAnalysisResult.
- **Location**: [`skilly_core/analyzer.py:176`](skilly_core/analyzer.py:176)
- **Signature**: `def analyze() -> ProjectAnalysisResult`
```python
from skilly_core.analyzer import analyze
result = analyze(...)
```

### `ProjectAnalyzer.write_artifacts`
- **Role**: Generates and writes all artifacts to the output directory (defaults to project dir).
- **Location**: [`skilly_core/analyzer.py:260`](skilly_core/analyzer.py:260)
- **Signature**: `def write_artifacts(result: ProjectAnalysisResult, output_dir: Optional[Path | str], skills_file: str, graph_html_file: str, graph_json_file: str, graph_md_file: str, inject_ai: Optional[bool]) -> Dict[str, Path]`
```python
from skilly_core.analyzer import write_artifacts
result = write_artifacts(...)
```

### `AnalysisCache`
- **Role**: Manages file hashes and cached extraction results.
- **Location**: [`skilly_core/cache.py:22`](skilly_core/cache.py:22)
- **Signature**: `class AnalysisCache():`
```python
from skilly_core.cache import AnalysisCache
instance = AnalysisCache()
```

### `AnalysisCache.compute_file_hash`
- **Role**: Computes fast SHA256 of file contents.
- **Location**: [`skilly_core/cache.py:47`](skilly_core/cache.py:47)
- **Signature**: `def compute_file_hash(path: Path) -> str`
```python
from skilly_core.cache import compute_file_hash
result = compute_file_hash(...)
```

### `AnalysisCache.get_cached`
- **Role**: Returns cached extraction if file hash matches.
- **Location**: [`skilly_core/cache.py:58`](skilly_core/cache.py:58)
- **Signature**: `def get_cached(rel_path: str, current_hash: str) -> Optional[Tuple[List[Skill], List[GraphNode], List[GraphEdge]]]`
```python
from skilly_core.cache import get_cached
result = get_cached(...)
```

### `AnalysisCache.store`
- **Role**: Stores extracted results for file.
- **Location**: [`skilly_core/cache.py:116`](skilly_core/cache.py:116)
- **Signature**: `def store(rel_path: str, file_hash: str, skills: List[Skill], nodes: List[GraphNode], edges: List[GraphEdge])`
```python
from skilly_core.cache import store
result = store(...)
```

### `SkillyConfig.load`
- **Role**: Loads configuration from project root or explicit path with sensible defaults.
- **Location**: [`skilly_core/config.py:58`](skilly_core/config.py:58)
- **Signature**: `def load(project_root: Path | str, explicit_config_path: Optional[str]) -> SkillyConfig`
```python
from skilly_core.config import load
result = load(...)
```

### `KnowledgeGraphEngine`
- **Role**: Constructs and analyzes the project knowledge graph.
- **Location**: [`skilly_core/graph_engine.py:14`](skilly_core/graph_engine.py:14)
- **Signature**: `class KnowledgeGraphEngine():`
```python
from skilly_core.graph_engine import KnowledgeGraphEngine
instance = KnowledgeGraphEngine()
```

### `KnowledgeGraphEngine.build_graph`
- **Role**: Builds the graph, calculates PageRank and metrics, clusters nodes,
- **Location**: [`skilly_core/graph_engine.py:22`](skilly_core/graph_engine.py:22)
- **Signature**: `def build_graph(nodes: List[GraphNode], edges: List[GraphEdge]) -> Tuple[List[GraphNode], List[GraphEdge], Dict[str, List[str]], List[GraphNode], List[List[str]]]`
```python
from skilly_core.graph_engine import build_graph
result = build_graph(...)
```

### `KnowledgeGraphEngine.compute_health_report`
- **Role**: Computes architectural health, acyclic integrity, and documentation quality.
- **Location**: [`skilly_core/graph_engine.py:161`](skilly_core/graph_engine.py:161)
- **Signature**: `def compute_health_report(skills: list, clusters: dict, cycles: list)`
```python
from skilly_core.graph_engine import compute_health_report
result = compute_health_report(...)
```

### `SkillCategory`
- **Role**: Service / component 'SkillCategory'
- **Location**: [`skilly_core/models.py:12`](skilly_core/models.py:12)
- **Signature**: `class SkillCategory(str, Enum):`
```python
from skilly_core.models import SkillCategory
instance = SkillCategory()
```

### `NodeType`
- **Role**: Service / component 'NodeType'
- **Location**: [`skilly_core/models.py:22`](skilly_core/models.py:22)
- **Signature**: `class NodeType(str, Enum):`
```python
from skilly_core.models import NodeType
instance = NodeType()
```

### `EdgeType`
- **Role**: Service / component 'EdgeType'
- **Location**: [`skilly_core/models.py:34`](skilly_core/models.py:34)
- **Signature**: `class EdgeType(str, Enum):`
```python
from skilly_core.models import EdgeType
instance = EdgeType()
```

### `BaseExtractor`
- **Role**: Abstract base class for static context and AST extractors.
- **Location**: [`skilly_core/extractors/base.py:11`](skilly_core/extractors/base.py:11)
- **Signature**: `class BaseExtractor(ABC):`
```python
from skilly_core.extractors.base import BaseExtractor
instance = BaseExtractor()
```

### `BaseExtractor.extract`
- **Role**: Analyze files and return extracted skills, knowledge graph nodes, and edges.
- **Location**: [`skilly_core/extractors/base.py:18`](skilly_core/extractors/base.py:18)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.base import extract
result = extract(...)
```

### `JavaScriptExtractor`
- **Role**: Analyzes JS/TS files for skills, exports, API routes, and dependency graphs.
- **Location**: [`skilly_core/extractors/javascript_extractor.py:24`](skilly_core/extractors/javascript_extractor.py:24)
- **Signature**: `class JavaScriptExtractor(BaseExtractor):`
```python
from skilly_core.extractors.javascript_extractor import JavaScriptExtractor
instance = JavaScriptExtractor()
```

### `JavaScriptExtractor.extract`
- **Role**: Function `JavaScriptExtractor.extract` in skilly_core/extractors/javascript_extractor.py
- **Location**: [`skilly_core/extractors/javascript_extractor.py:27`](skilly_core/extractors/javascript_extractor.py:27)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.javascript_extractor import extract
result = extract(...)
```

### `ManifestExtractor`
- **Role**: Parses project manifests, scripts, build configs, and environment templates.
- **Location**: [`skilly_core/extractors/manifest_extractor.py:25`](skilly_core/extractors/manifest_extractor.py:25)
- **Signature**: `class ManifestExtractor(BaseExtractor):`
```python
from skilly_core.extractors.manifest_extractor import ManifestExtractor
instance = ManifestExtractor()
```

### `ManifestExtractor.extract`
- **Role**: Function `ManifestExtractor.extract` in skilly_core/extractors/manifest_extractor.py
- **Location**: [`skilly_core/extractors/manifest_extractor.py:28`](skilly_core/extractors/manifest_extractor.py:28)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.manifest_extractor import extract
result = extract(...)
```

### `PolyglotExtractor`
- **Role**: Analyzes Go, Rust, Java, and C# files for skills, exports, and relationships.
- **Location**: [`skilly_core/extractors/polyglot_extractor.py:14`](skilly_core/extractors/polyglot_extractor.py:14)
- **Signature**: `class PolyglotExtractor(BaseExtractor):`
```python
from skilly_core.extractors.polyglot_extractor import PolyglotExtractor
instance = PolyglotExtractor()
```

### `PolyglotExtractor.extract`
- **Role**: Function `PolyglotExtractor.extract` in skilly_core/extractors/polyglot_extractor.py
- **Location**: [`skilly_core/extractors/polyglot_extractor.py:17`](skilly_core/extractors/polyglot_extractor.py:17)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.polyglot_extractor import extract
result = extract(...)
```

### `PythonASTExtractor`
- **Role**: Analyzes Python files for skills, AST symbols, API routes, and relationships.
- **Location**: [`skilly_core/extractors/python_extractor.py:16`](skilly_core/extractors/python_extractor.py:16)
- **Signature**: `class PythonASTExtractor(BaseExtractor):`
```python
from skilly_core.extractors.python_extractor import PythonASTExtractor
instance = PythonASTExtractor()
```

### `PythonASTExtractor.extract`
- **Role**: Function `PythonASTExtractor.extract` in skilly_core/extractors/python_extractor.py
- **Location**: [`skilly_core/extractors/python_extractor.py:19`](skilly_core/extractors/python_extractor.py:19)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.python_extractor import extract
result = extract(...)
```

### `UniversalPolyglotExtractor`
- **Role**: Universal AST and semantic extractor supporting 50+ programming languages.
- **Location**: [`skilly_core/extractors/universal_engine.py:72`](skilly_core/extractors/universal_engine.py:72)
- **Signature**: `class UniversalPolyglotExtractor(BaseExtractor):`
```python
from skilly_core.extractors.universal_engine import UniversalPolyglotExtractor
instance = UniversalPolyglotExtractor()
```

### `UniversalPolyglotExtractor.extract`
- **Role**: Function `UniversalPolyglotExtractor.extract` in skilly_core/extractors/universal_engine.py
- **Location**: [`skilly_core/extractors/universal_engine.py:94`](skilly_core/extractors/universal_engine.py:94)
- **Signature**: `def extract(file_paths: List[Path]) -> Tuple[List[Skill], List[GraphNode], List[GraphEdge]]`
```python
from skilly_core.extractors.universal_engine import extract
result = extract(...)
```

### `GraphMarkdownGenerator`
- **Role**: Generates knowledge_graph.md from graph analysis results.
- **Location**: [`skilly_core/generators/graph_markdown_generator.py:11`](skilly_core/generators/graph_markdown_generator.py:11)
- **Signature**: `class GraphMarkdownGenerator():`
```python
from skilly_core.generators.graph_markdown_generator import GraphMarkdownGenerator
instance = GraphMarkdownGenerator()
```

### `GraphMarkdownGenerator.generate`
- **Role**: Function `GraphMarkdownGenerator.generate` in skilly_core/generators/graph_markdown_generator.py
- **Location**: [`skilly_core/generators/graph_markdown_generator.py:14`](skilly_core/generators/graph_markdown_generator.py:14)
- **Signature**: `def generate(result: ProjectAnalysisResult) -> str`
```python
from skilly_core.generators.graph_markdown_generator import generate
result = generate(...)
```

### `HTMLVisualizer`
- **Role**: Renders a visual knowledge graph visualization.
- **Location**: [`skilly_core/generators/html_visualizer.py:13`](skilly_core/generators/html_visualizer.py:13)
- **Signature**: `class HTMLVisualizer():`
```python
from skilly_core.generators.html_visualizer import HTMLVisualizer
instance = HTMLVisualizer()
```

### `HTMLVisualizer.generate`
- **Role**: Function `HTMLVisualizer.generate` in skilly_core/generators/html_visualizer.py
- **Location**: [`skilly_core/generators/html_visualizer.py:16`](skilly_core/generators/html_visualizer.py:16)
- **Signature**: `def generate(result: ProjectAnalysisResult) -> str`
```python
from skilly_core.generators.html_visualizer import generate
result = generate(...)
```

### `SkillsGenerator`
- **Role**: Generates the skills.md documentation from extracted project analysis.
- **Location**: [`skilly_core/generators/skills_generator.py:12`](skilly_core/generators/skills_generator.py:12)
- **Signature**: `class SkillsGenerator():`
```python
from skilly_core.generators.skills_generator import SkillsGenerator
instance = SkillsGenerator()
```

### `SkillsGenerator.generate`
- **Role**: Function `SkillsGenerator.generate` in skilly_core/generators/skills_generator.py
- **Location**: [`skilly_core/generators/skills_generator.py:15`](skilly_core/generators/skills_generator.py:15)
- **Signature**: `def generate(result: ProjectAnalysisResult) -> str`
```python
from skilly_core.generators.skills_generator import generate
result = generate(...)
```

### `AIInjector`
- **Role**: Manages injection of Skilly capabilities into AI assistant instruction files.
- **Location**: [`skilly_core/injectors/ai_injector.py:29`](skilly_core/injectors/ai_injector.py:29)
- **Signature**: `class AIInjector():`
```python
from skilly_core.injectors.ai_injector import AIInjector
instance = AIInjector()
```

### `AIInjector.build_directive`
- **Role**: Build the structured AI guidance block.
- **Location**: [`skilly_core/injectors/ai_injector.py:38`](skilly_core/injectors/ai_injector.py:38)
- **Signature**: `def build_directive(result: ProjectAnalysisResult) -> str`
```python
from skilly_core.injectors.ai_injector import build_directive
result = build_directive(...)
```

### `AIInjector.inject_all`
- **Role**: Inject Skilly context into all enabled AI coding assistants.
- **Location**: [`skilly_core/injectors/ai_injector.py:104`](skilly_core/injectors/ai_injector.py:104)
- **Signature**: `def inject_all(target_dir: Path, result: ProjectAnalysisResult) -> Dict[str, Path]`
```python
from skilly_core.injectors.ai_injector import inject_all
result = inject_all(...)
```

### `ItemController`
- **Role**: Java class `ItemController`
- **Location**: [`tests/fixtures/sample_polyglot_app/ItemController.java:7`](tests/fixtures/sample_polyglot_app/ItemController.java:7)
- **Signature**: `public class ItemController`

### `ProjectAnalyzer`
- **Role**: Python class definition `ProjectAnalyzer`
- **Location**: [`skilly_core/analyzer.py:134`](skilly_core/analyzer.py:134)
- **Signature**: `class_definition ProjectAnalyzer`

### `AnalysisCache`
- **Role**: Python class definition `AnalysisCache`
- **Location**: [`skilly_core/cache.py:22`](skilly_core/cache.py:22)
- **Signature**: `class_definition AnalysisCache`

### `QuietHandler`
- **Role**: Python class definition `QuietHandler`
- **Location**: [`skilly_core/cli.py:320`](skilly_core/cli.py:320)
- **Signature**: `class_definition QuietHandler`

### `SkillyConfig`
- **Role**: Python class definition `SkillyConfig`
- **Location**: [`skilly_core/config.py:21`](skilly_core/config.py:21)
- **Signature**: `class_definition SkillyConfig`

### `KnowledgeGraphEngine`
- **Role**: Python class definition `KnowledgeGraphEngine`
- **Location**: [`skilly_core/graph_engine.py:14`](skilly_core/graph_engine.py:14)
- **Signature**: `class_definition KnowledgeGraphEngine`

### `SkillCategory`
- **Role**: Python class definition `SkillCategory`
- **Location**: [`skilly_core/models.py:12`](skilly_core/models.py:12)
- **Signature**: `class_definition SkillCategory`

### `NodeType`
- **Role**: Python class definition `NodeType`
- **Location**: [`skilly_core/models.py:22`](skilly_core/models.py:22)
- **Signature**: `class_definition NodeType`

### `EdgeType`
- **Role**: Python class definition `EdgeType`
- **Location**: [`skilly_core/models.py:34`](skilly_core/models.py:34)
- **Signature**: `class_definition EdgeType`

### `Skill`
- **Role**: Python class definition `Skill`
- **Location**: [`skilly_core/models.py:45`](skilly_core/models.py:45)
- **Signature**: `class_definition Skill`

### `GraphNode`
- **Role**: Python class definition `GraphNode`
- **Location**: [`skilly_core/models.py:75`](skilly_core/models.py:75)
- **Signature**: `class_definition GraphNode`

### `GraphEdge`
- **Role**: Python class definition `GraphEdge`
- **Location**: [`skilly_core/models.py:105`](skilly_core/models.py:105)
- **Signature**: `class_definition GraphEdge`

### `ProjectSummary`
- **Role**: Python class definition `ProjectSummary`
- **Location**: [`skilly_core/models.py:123`](skilly_core/models.py:123)
- **Signature**: `class_definition ProjectSummary`

### `HealthReport`
- **Role**: Python class definition `HealthReport`
- **Location**: [`skilly_core/models.py:149`](skilly_core/models.py:149)
- **Signature**: `class_definition HealthReport`

### `ProjectAnalysisResult`
- **Role**: Python class definition `ProjectAnalysisResult`
- **Location**: [`skilly_core/models.py:169`](skilly_core/models.py:169)
- **Signature**: `class_definition ProjectAnalysisResult`

### `BaseExtractor`
- **Role**: Python class definition `BaseExtractor`
- **Location**: [`skilly_core/extractors/base.py:11`](skilly_core/extractors/base.py:11)
- **Signature**: `class_definition BaseExtractor`

### `JavaScriptExtractor`
- **Role**: Python class definition `JavaScriptExtractor`
- **Location**: [`skilly_core/extractors/javascript_extractor.py:24`](skilly_core/extractors/javascript_extractor.py:24)
- **Signature**: `class_definition JavaScriptExtractor`

### `ManifestExtractor`
- **Role**: Python class definition `ManifestExtractor`
- **Location**: [`skilly_core/extractors/manifest_extractor.py:25`](skilly_core/extractors/manifest_extractor.py:25)
- **Signature**: `class_definition ManifestExtractor`

### `PolyglotExtractor`
- **Role**: Python class definition `PolyglotExtractor`
- **Location**: [`skilly_core/extractors/polyglot_extractor.py:14`](skilly_core/extractors/polyglot_extractor.py:14)
- **Signature**: `class_definition PolyglotExtractor`

### `PythonASTExtractor`
- **Role**: Python class definition `PythonASTExtractor`
- **Location**: [`skilly_core/extractors/python_extractor.py:16`](skilly_core/extractors/python_extractor.py:16)
- **Signature**: `class_definition PythonASTExtractor`

### `UniversalPolyglotExtractor`
- **Role**: Python class definition `UniversalPolyglotExtractor`
- **Location**: [`skilly_core/extractors/universal_engine.py:72`](skilly_core/extractors/universal_engine.py:72)
- **Signature**: `class_definition UniversalPolyglotExtractor`

### `GraphMarkdownGenerator`
- **Role**: Python class definition `GraphMarkdownGenerator`
- **Location**: [`skilly_core/generators/graph_markdown_generator.py:11`](skilly_core/generators/graph_markdown_generator.py:11)
- **Signature**: `class_definition GraphMarkdownGenerator`

### `HTMLVisualizer`
- **Role**: Python class definition `HTMLVisualizer`
- **Location**: [`skilly_core/generators/html_visualizer.py:13`](skilly_core/generators/html_visualizer.py:13)
- **Signature**: `class_definition HTMLVisualizer`

### `SkillsGenerator`
- **Role**: Python class definition `SkillsGenerator`
- **Location**: [`skilly_core/generators/skills_generator.py:12`](skilly_core/generators/skills_generator.py:12)
- **Signature**: `class_definition SkillsGenerator`

### `AIInjector`
- **Role**: Python class definition `AIInjector`
- **Location**: [`skilly_core/injectors/ai_injector.py:29`](skilly_core/injectors/ai_injector.py:29)
- **Signature**: `class_definition AIInjector`

### `PriceCalculator`
- **Role**: Ruby component `PriceCalculator`
- **Location**: [`tests/fixtures/sample_polyglot_app/calc.rb:2`](tests/fixtures/sample_polyglot_app/calc.rb:2)
- **Signature**: `class/struct PriceCalculator`

### `ItemController`
- **Role**: Java class declaration `ItemController`
- **Location**: [`tests/fixtures/sample_polyglot_app/ItemController.java:6`](tests/fixtures/sample_polyglot_app/ItemController.java:6)
- **Signature**: `class_declaration ItemController`

### `TokenVault`
- **Role**: Decentralized treasury vault for liquidity tokens
- **Location**: [`tests/fixtures/sample_polyglot_app/Vault.sol:5`](tests/fixtures/sample_polyglot_app/Vault.sol:5)
- **Signature**: `contract_declaration TokenVault`

### `UserLoginRequest`
- **Role**: Python class definition `UserLoginRequest`
- **Location**: [`tests/fixtures/sample_python_app/models.py:4`](tests/fixtures/sample_python_app/models.py:4)
- **Signature**: `class_definition UserLoginRequest`

### `AuthToken`
- **Role**: Python class definition `AuthToken`
- **Location**: [`tests/fixtures/sample_python_app/models.py:10`](tests/fixtures/sample_python_app/models.py:10)
- **Signature**: `class_definition AuthToken`

### `AuthService`
- **Role**: Python class definition `AuthService`
- **Location**: [`tests/fixtures/sample_python_app/services.py:7`](tests/fixtures/sample_python_app/services.py:7)
- **Signature**: `class_definition AuthService`

## 4. Data Models & Schemas

| Model / Schema | Description | Location | Details |
| :--- | :--- | :--- | :--- |
| **`SkillyConfig`** | Production configuration options for Skilly. | `skilly_core/config.py:21` | `class SkillyConfig():` |
| **`Skill`** | Data model / schema 'Skill' | `skilly_core/models.py:45` | `class Skill():` |
| **`GraphNode`** | Data model / schema 'GraphNode' | `skilly_core/models.py:75` | `class GraphNode():` |
| **`GraphEdge`** | Data model / schema 'GraphEdge' | `skilly_core/models.py:105` | `class GraphEdge():` |
| **`ProjectSummary`** | Data model / schema 'ProjectSummary' | `skilly_core/models.py:123` | `class ProjectSummary():` |
| **`HealthReport`** | Data model / schema 'HealthReport' | `skilly_core/models.py:149` | `class HealthReport():` |
| **`ProjectAnalysisResult`** | Data model / schema 'ProjectAnalysisResult' | `skilly_core/models.py:169` | `class ProjectAnalysisResult():` |
| **`Point3D`** | Represents a 3D point in coordinate space. | `tests/fixtures/sample_polyglot_app/main.c:5` | `struct_specifier Point3D` |
| **`Point3D`** | Calculates Euclidean distance between two 3D points. | `tests/fixtures/sample_polyglot_app/main.c:12` | `struct_specifier Point3D` |
| **`Point3D`** | Calculates Euclidean distance between two 3D points. | `tests/fixtures/sample_polyglot_app/main.c:12` | `struct_specifier Point3D` |

## 5. Core Exported Functions & Utilities

Found **50** core callable functions:

#### `print_banner`
- **Description**: Function `print_banner` in skilly_core/cli.py
- **Location**: `skilly_core/cli.py:43`
- **Signature**: `def print_banner()`
```python
from skilly_core.cli import print_banner
result = print_banner(...)
```

#### `main`
- **Description**: Function `main` in skilly_core/cli.py
- **Location**: `skilly_core/cli.py:58`
- **Signature**: `def main(args: Optional[list])`
- **Parameters**: `args` (Optional[list])
```python
from skilly_core.cli import main
result = main(...)
```

#### `analyze_project`
- **Description**: Convenience function to analyze a project directory.
- **Location**: `skilly_core/__init__.py:11`
- **Signature**: `def analyze_project(target_dir: str) -> ProjectAnalysisResult`
- **Parameters**: `target_dir` (str)
- **Returns**: `ProjectAnalysisResult`
```python
from skilly_core.__init__ import analyze_project
result = analyze_project(...)
```

#### `calculateTax`
- **Description**: Calculates sum with tax applied. @param amount Base price @param rate Tax rate decimal
- **Location**: `tests/fixtures/sample_node_app/server.js:12`
- **Signature**: `export function calculateTax(amount, rate)`
- **Parameters**: `amount` (any), `rate` (any)
```python
import { calculateTax } from './server';
const result = calculateTax(...);
```

#### `scan_files`
- **Description**: Callable Python function `scan_files` in analyzer.py
- **Location**: `skilly_core/analyzer.py:144`
- **Signature**: `fn scan_files(...)`

#### `analyze`
- **Description**: Callable Python function `analyze` in analyzer.py
- **Location**: `skilly_core/analyzer.py:176`
- **Signature**: `fn analyze(...)`

#### `write_artifacts`
- **Description**: Callable Python function `write_artifacts` in analyzer.py
- **Location**: `skilly_core/analyzer.py:260`
- **Signature**: `fn write_artifacts(...)`

#### `save`
- **Description**: Callable Python function `save` in cache.py
- **Location**: `skilly_core/cache.py:39`
- **Signature**: `fn save(...)`

#### `compute_file_hash`
- **Description**: Callable Python function `compute_file_hash` in cache.py
- **Location**: `skilly_core/cache.py:47`
- **Signature**: `fn compute_file_hash(...)`

#### `get_cached`
- **Description**: Callable Python function `get_cached` in cache.py
- **Location**: `skilly_core/cache.py:58`
- **Signature**: `fn get_cached(...)`

#### `store`
- **Description**: Callable Python function `store` in cache.py
- **Location**: `skilly_core/cache.py:116`
- **Signature**: `fn store(...)`

#### `print_banner`
- **Description**: Callable Python function `print_banner` in cli.py
- **Location**: `skilly_core/cli.py:43`
- **Signature**: `fn print_banner(...)`

#### `log_message`
- **Description**: Callable Python function `log_message` in cli.py
- **Location**: `skilly_core/cli.py:323`
- **Signature**: `fn log_message(...)`

#### `load`
- **Description**: Callable Python function `load` in config.py
- **Location**: `skilly_core/config.py:58`
- **Signature**: `fn load(...)`

#### `from_dict`
- **Description**: Callable Python function `from_dict` in config.py
- **Location**: `skilly_core/config.py:87`
- **Signature**: `fn from_dict(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in config.py
- **Location**: `skilly_core/config.py:94`
- **Signature**: `fn to_dict(...)`

#### `build_graph`
- **Description**: Callable Python function `build_graph` in graph_engine.py
- **Location**: `skilly_core/graph_engine.py:22`
- **Signature**: `fn build_graph(...)`

#### `compute_health_report`
- **Description**: Callable Python function `compute_health_report` in graph_engine.py
- **Location**: `skilly_core/graph_engine.py:161`
- **Signature**: `fn compute_health_report(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in models.py
- **Location**: `skilly_core/models.py:58`
- **Signature**: `fn to_dict(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in models.py
- **Location**: `skilly_core/models.py:88`
- **Signature**: `fn to_dict(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in models.py
- **Location**: `skilly_core/models.py:112`
- **Signature**: `fn to_dict(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in models.py
- **Location**: `skilly_core/models.py:134`
- **Signature**: `fn to_dict(...)`

#### `to_dict`
- **Description**: Callable Python function `to_dict` in models.py
- **Location**: `skilly_core/models.py:157`
- **Signature**: `fn to_dict(...)`

#### `analyze_project`
- **Description**: Callable Python function `analyze_project` in __init__.py
- **Location**: `skilly_core/__init__.py:11`
- **Signature**: `fn analyze_project(...)`

#### `extract`
- **Description**: Callable Python function `extract` in base.py
- **Location**: `skilly_core/extractors/base.py:18`
- **Signature**: `fn extract(...)`

#### `extract`
- **Description**: Callable Python function `extract` in javascript_extractor.py
- **Location**: `skilly_core/extractors/javascript_extractor.py:27`
- **Signature**: `fn extract(...)`

#### `extract`
- **Description**: Callable Python function `extract` in manifest_extractor.py
- **Location**: `skilly_core/extractors/manifest_extractor.py:28`
- **Signature**: `fn extract(...)`

#### `extract`
- **Description**: Callable Python function `extract` in polyglot_extractor.py
- **Location**: `skilly_core/extractors/polyglot_extractor.py:17`
- **Signature**: `fn extract(...)`

#### `extract`
- **Description**: Callable Python function `extract` in python_extractor.py
- **Location**: `skilly_core/extractors/python_extractor.py:19`
- **Signature**: `fn extract(...)`

#### `extract`
- **Description**: Callable Python function `extract` in universal_engine.py
- **Location**: `skilly_core/extractors/universal_engine.py:94`
- **Signature**: `fn extract(...)`

_...and 20 more exported functions available in source code._

## 6. Environment & Configuration

_No environment templates (.env.example) found._

## 7. Architectural Hubs & Central Components

The following components exhibit the highest architectural centrality (PageRank & connectivity):

| Rank | Component / Symbol | Type | Centrality Score | Inbound Deps | Outbound Calls | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| #1 | **`append`** | `module` | `0.009902734742027939` | `42` | `0` | Core system component |
| #2 | **`str`** | `module` | `0.008000265047100977` | `18` | `0` | Core system component |
| #3 | **`GraphNode`** | `module` | `0.007696338621061196` | `34` | `0` | Core system component |
| #4 | **`isinstance`** | `module` | `0.007003489291072726` | `13` | `0` | Core system component |
| #5 | **`Skill`** | `module` | `0.006787725264070577` | `28` | `0` | Core system component |
| #6 | **`Path`** | `module` | `0.006622989711624956` | `19` | `0` | Core system component |
| #7 | **`len`** | `module` | `0.006379109693073134` | `22` | `0` | Core system component |
| #8 | **`_rel`** | `module` | `0.006115901075974002` | `22` | `0` | Core system component |
| #9 | **`replace`** | `module` | `0.0055442048362015885` | `11` | `0` | Core system component |
| #10 | **`lower`** | `module` | `0.0053942997527417335` | `22` | `0` | Core system component |
| #11 | **`read_text`** | `module` | `0.005012021126085019` | `20` | `0` | Core system component |
| #12 | **`GraphEdge`** | `module` | `0.004904483327230995` | `23` | `0` | Core system component |
| #13 | **`round`** | `module` | `0.0047508024362884595` | `2` | `0` | Core system component |
| #14 | **`BaseModel`** | `module` | `0.0046964233150014086` | `2` | `0` | Core system component |
| #15 | **`resolve`** | `module` | `0.004405785587040516` | `7` | `0` | Core system component |

---
*Generated autonomously by **Skilly** (Zero-LLM Architecture Synthesizer) • Created by [Arastu Thakur](https://arastuthakur.com.np/) • [GitHub](https://github.com/arastuthakur) • [LinkedIn](https://www.linkedin.com/in/arastuthakur/)*