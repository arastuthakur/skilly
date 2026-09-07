# Knowledge Graph Architecture: Model

> Structural and semantic topology extracted deterministically via AST and import graphs.

## 📈 Graph Metrics
- **Total Entities (Nodes)**: `475`
- **Total Relationships (Edges)**: `1129`
- **Architectural Clusters**: `3`
- **Circular Dependency Cycles**: `1`

### ⚠️ Circular Dependencies Detected
The following circular reference cycles were identified in the codebase:

- `file:tests/fixtures/sample_circular_app/a.py` ➔ `file:tests/fixtures/sample_circular_app/b.py` ➔ `file:tests/fixtures/sample_circular_app/a.py`

## 🏛️ Architectural Clusters & Subdomains

### Skilly_core Domain (`406` components)
- **Key Components**: `exit`, `analyze`, `update`, `JavaScriptExtractor`, `skilly_core`, `HTMLVisualizer.generate`, `parse_args`, `skilly_core/cache.py`, `ArgumentParser`, `load`
- _...and 396 more components_

### Tests Domain (`63` components)
- **Key Components**: `tests/fixtures/sample_python_app/requirements.txt`, `AuthService.authenticate_user`, `print_banner`, `AuthToken`, `click`, `BaseModel`, `AuthService`, `pydantic`, `tests/fixtures/sample_python_app/services.py`, `command`
- _...and 53 more components_

### Root Domain (`6` components)
- **Key Components**: `setup.py`, `setuptools`, `start`, `test`, `skilly`, `install.sh`

## 🗺️ High-Level Module Architecture Diagram

```mermaid
graph TD
    file_setup_py["setup.py (file)"]
    file_skilly_py["skilly.py (file)"]
    file_skilly_core_analyzer_py["analyzer.py (file)"]
    file_skilly_core_cache_py["cache.py (file)"]
    file_skilly_core_cli_py["cli.py (file)"]
    file_skilly_core_config_py["config.py (file)"]
    file_skilly_core_graph_engine_py["graph_engine.py (file)"]
    file_skilly_core_models_py["models.py (file)"]
    file_skilly_core___init___py["__init__.py (file)"]
    file_skilly_core_extractors_base_py["base.py (file)"]
    file_skilly_core_extractors_javascript_extractor_py["javascript_extractor.py (file)"]
    file_skilly_core_extractors_manifest_extractor_py["manifest_extractor.py (file)"]
    file_skilly_core_extractors_polyglot_extractor_py["polyglot_extractor.py (file)"]
    file_skilly_core_extractors_python_extractor_py["python_extractor.py (file)"]
    file_skilly_core_extractors_universal_engine_py["universal_engine.py (file)"]
    Path["Path (module)"]
    append["append (module)"]
    len["len (module)"]
    str["str (module)"]
    replace["replace (module)"]
    GraphEdge["GraphEdge (module)"]
    Skill["Skill (module)"]
    GraphNode["GraphNode (module)"]
    isinstance["isinstance (module)"]
    _rel["_rel (module)"]
```

## 🌟 Central Architectural Hubs (PageRank)

| Rank | Symbol / Module | Type | PageRank | In-Degree | Out-Degree | Impact / Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| #1 | `append` | `module` | `0.0104` | `42` | `0` | Critical Choke Point |
| #2 | `str` | `module` | `0.0084` | `18` | `0` | Critical Choke Point |
| #3 | `GraphNode` | `module` | `0.0081` | `34` | `0` | Critical Choke Point |
| #4 | `isinstance` | `module` | `0.0074` | `13` | `0` | Critical Choke Point |
| #5 | `Skill` | `module` | `0.0071` | `28` | `0` | Critical Choke Point |
| #6 | `Path` | `module` | `0.0070` | `19` | `0` | Critical Choke Point |
| #7 | `_rel` | `module` | `0.0064` | `22` | `0` | Critical Choke Point |
| #8 | `len` | `module` | `0.0063` | `21` | `0` | Critical Choke Point |
| #9 | `replace` | `module` | `0.0058` | `11` | `0` | Critical Choke Point |
| #10 | `GraphEdge` | `module` | `0.0052` | `23` | `0` | Critical Choke Point |
| #11 | `round` | `module` | `0.0050` | `2` | `0` | High Importance |
| #12 | `BaseModel` | `module` | `0.0049` | `2` | `0` | High Importance |
| #13 | `lower` | `module` | `0.0048` | `21` | `0` | Critical Choke Point |
| #14 | `resolve` | `module` | `0.0047` | `7` | `0` | Critical Choke Point |
| #15 | `get` | `module` | `0.0045` | `10` | `0` | Critical Choke Point |

## 🔗 Relationship Types Distribution

| Relationship Type | Count | Description |
| :--- | :--- | :--- |
| `calls` | `743` | Inter-component connection |
| `exposes` | `260` | Inter-component connection |
| `imports` | `103` | Inter-component connection |
| `inherits` | `14` | Inter-component connection |
| `depends_on` | `9` | Inter-component connection |

---
*Interactive visual graph available in `knowledge_graph.html`*