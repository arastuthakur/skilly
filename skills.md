---
project: "skilly-ai"
total_skills: 55
languages: ['PowerShell', 'Shell', 'HTML', 'Python']
frameworks: ['Docker']
generator: "skilly (deterministic LLM-free AST analyzer)"
---

# Project Skills & Capabilities: skilly-ai

> Auto-generated capability catalog extracted via static AST and manifest context.

## Repository Capabilities Overview

| Metric | Count / Detail |
| :--- | :--- |
| **Architecture Health Grade** | `A+` (100/100 - Grade A+ (100/100): Acyclic architecture with high integrity.) |
| **Primary Languages** | PowerShell (1 files), Shell (1 files), HTML (1 files), Python (31 files) |
| **Frameworks / Tooling** | Docker |
| **Total Skills Cataloged** | `55` |
| **Knowledge Graph Entities** | `432 nodes, 1293 edges` |
| **Runnable Commands & Workflows** | `9` |
| **API Endpoints** | `0` |
| **Domain Services & Models** | `43` |

## Table of Contents
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
| **cli: skilly-ai** | `CLI Command` | Executable binary 'skilly-ai' -> ./bin/skilly-node.js | `package.json:bin.skilly-ai` | `npx skilly-ai` |
| **CLI: skilly** | `CLI Command` | Console script entry point: skilly_core.cli:main | `pyproject.toml:scripts.skilly` | `skilly --help` |
| **Script: stress_test.py** | `CLI Command` | Executable project script at scripts/stress_test.py | `scripts/stress_test.py` | `python scripts/stress_test.py` |
| **docker compose up** | `Workflow` | Start containerized services defined in docker-compose | `docker-compose.yml` | `docker compose up -d` |
| **docker build** | `Workflow` | Build Docker container image from Dockerfile | `Dockerfile` | `docker build -t app .` |
| **npm run test** | `Workflow` | Run npm script 'test': `python -m pytest tests/ -v` | `package.json:scripts.test` | `npm test` |
| **CI Workflow: Generate Project Skills & Knowledge Graph** | `Workflow` | GitHub Actions CI workflow defined in .github/workflows/skilly.yml | `.github/workflows/skilly.yml` | `gh workflow run skilly.yml` |

### Command Execution Cheat-Sheet
```bash
# Run npm script 'start': `node ./bin/skilly-node.js`
npm start

# Executable binary 'skilly' -> ./bin/skilly-node.js
npx skilly

# Executable binary 'skilly-ai' -> ./bin/skilly-node.js
npx skilly-ai

# Console script entry point: skilly_core.cli:main
skilly --help

# Executable project script at scripts/stress_test.py
python scripts/stress_test.py

# Start containerized services defined in docker-compose
docker compose up -d

# Build Docker container image from Dockerfile
docker build -t app .

# Run npm script 'test': `python -m pytest tests/ -v`
npm test

# GitHub Actions CI workflow defined in .github/workflows/skilly.yml
gh workflow run skilly.yml

```

## 2. API Endpoints & Routes

_No REST, GraphQL, or HTTP endpoint handlers detected._

## 3. Domain Services & Key Controllers

### `ProjectAnalyzer`
- **Role**: Orchestrates whole-project capability extraction and knowledge graph synthesis.
- **Location**: [`skilly_core/analyzer.py:119`](skilly_core/analyzer.py:119)
- **Signature**: `class ProjectAnalyzer():`
```python
from skilly_core.analyzer import ProjectAnalyzer
instance = ProjectAnalyzer()
```

### `ProjectAnalyzer.scan_files`
- **Role**: Walks the directory and collects all relevant source and manifest files.
- **Location**: [`skilly_core/analyzer.py:129`](skilly_core/analyzer.py:129)
- **Signature**: `def scan_files() -> List[Path]`
```python
from skilly_core.analyzer import scan_files
result = scan_files(...)
```

### `ProjectAnalyzer.analyze`
- **Role**: Runs all extractors and graph algorithms to produce ProjectAnalysisResult.
- **Location**: [`skilly_core/analyzer.py:163`](skilly_core/analyzer.py:163)
- **Signature**: `def analyze() -> ProjectAnalysisResult`
```python
from skilly_core.analyzer import analyze
result = analyze(...)
```

### `ProjectAnalyzer.write_artifacts`
- **Role**: Generates and writes artifacts selectively to the output directory.
- **Location**: [`skilly_core/analyzer.py:280`](skilly_core/analyzer.py:280)
- **Signature**: `def write_artifacts(result: ProjectAnalysisResult, output_dir: Optional[Path | str], skills_file: str, graph_html_file: str, graph_json_file: str, graph_md_file: str, include_skills: bool, include_graph: bool, inject_ai: Optional[bool]) -> Dict[str, Path]`
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
- **Location**: [`skilly_core/graph_engine.py:173`](skilly_core/graph_engine.py:173)
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

## 5. Core Exported Functions & Utilities

Found **3** core callable functions:

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

## 6. Environment & Configuration

_No environment templates (.env.example) found._

## 7. Architectural Hubs & Central Components

The following components exhibit the highest architectural centrality (PageRank & connectivity):

| Rank | Component / Symbol | Type | Centrality Score | Inbound Deps | Outbound Calls | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| #1 | **`append`** | `module` | `0.011058450682381288` | `45` | `0` | Core system component |
| #2 | **`str`** | `module` | `0.009165362040271543` | `17` | `0` | Core system component |
| #3 | **`GraphNode`** | `module` | `0.008932726557061836` | `37` | `0` | Core system component |
| #4 | **`Path`** | `module` | `0.008293873756697162` | `24` | `0` | Core system component |
| #5 | **`isinstance`** | `module` | `0.008073833828348585` | `13` | `0` | Core system component |
| #6 | **`Skill`** | `module` | `0.007959506441723269` | `31` | `0` | Core system component |
| #7 | **`_rel`** | `module` | `0.007504067881836769` | `27` | `0` | Core system component |
| #8 | **`len`** | `module` | `0.0073725324611232474` | `27` | `0` | Core system component |
| #9 | **`replace`** | `module` | `0.007029417877267969` | `12` | `0` | Core system component |
| #10 | **`models.py`** | `file` | `0.006654514801840083` | `19` | `18` | Python source file models.py |
| #11 | **`lower`** | `module` | `0.006273492941243077` | `24` | `0` | Core system component |
| #12 | **`write_text`** | `module` | `0.005902366657838352` | `17` | `0` | Core system component |
| #13 | **`read_text`** | `module` | `0.0058302846869310344` | `23` | `0` | Core system component |
| #14 | **`round`** | `module` | `0.005739694329807803` | `2` | `0` | Core system component |
| #15 | **`ProjectAnalyzer`** | `module` | `0.005617045881117735` | `15` | `0` | Core system component |

---
*Generated autonomously by **Skilly** (Zero-LLM Architecture Synthesizer) • Created by [Arastu Thakur](https://arastuthakur.com.np/) • [PyPI](https://pypi.org/project/skilly-ai/) • [GitHub](https://github.com/arastuthakur/skilly) • [LinkedIn](https://www.linkedin.com/in/arastuthakur/)*