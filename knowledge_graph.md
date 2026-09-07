# Knowledge Graph Architecture: Model

> Structural and semantic topology extracted deterministically via AST and import graphs.

## 📈 Graph Metrics
- **Total Entities (Nodes)**: `495`
- **Total Relationships (Edges)**: `1215`
- **Architectural Clusters**: `3`
- **Circular Dependency Cycles**: `1`

### ⚠️ Circular Dependencies Detected
The following circular reference cycles were identified in the codebase:

- `file:tests/fixtures/sample_circular_app/a.py` ➔ `file:tests/fixtures/sample_circular_app/b.py` ➔ `file:tests/fixtures/sample_circular_app/a.py`

## Architectural Clusters & Subdomains

### Skilly_core Domain (`351` components)
- **Key Components**: `compile`, `_detect_route_in_surroundings`, `range`, `test_graph_engine_metrics_and_clusters`, `ManifestExtractor._parse_cargo_toml`, `ManifestExtractor._parse_docker`, `ManifestExtractor._parse_build_gradle`, `ManifestExtractor._parse_package_swift`, `skilly_core/extractors/javascript_extractor.py`, `test_graph_engine_cycle_detection`
- _...and 341 more components_

### Tests Domain (`138` components)
- **Key Components**: `is_file`, `json`, `tests/test_universal_engine.py`, `tests/test_python_extractor.py`, `tests/test_production.py`, `analyze`, `skilly_core/cli.py`, `skilly_core/injectors/__init__.py`, `test_json_summary_flag`, `load`
- _...and 128 more components_

### Root Domain (`6` components)
- **Key Components**: `setuptools`, `setup.py`, `start`, `test`, `skilly`, `install.sh`

## High-Level Module Architecture Diagram

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
    str["str (module)"]
    len["len (module)"]
    lower["lower (module)"]
    replace["replace (module)"]
    Skill["Skill (module)"]
    GraphNode["GraphNode (module)"]
    isinstance["isinstance (module)"]
    _rel["_rel (module)"]
```

## Central Architectural Hubs (PageRank)

| Rank | Symbol / Module | Type | PageRank | In-Degree | Out-Degree | Impact / Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| #1 | `append` | `module` | `0.0099` | `42` | `0` | Critical Choke Point |
| #2 | `str` | `module` | `0.0080` | `18` | `0` | Critical Choke Point |
| #3 | `GraphNode` | `module` | `0.0077` | `34` | `0` | Critical Choke Point |
| #4 | `isinstance` | `module` | `0.0070` | `13` | `0` | Critical Choke Point |
| #5 | `Skill` | `module` | `0.0068` | `28` | `0` | Critical Choke Point |
| #6 | `Path` | `module` | `0.0066` | `19` | `0` | Critical Choke Point |
| #7 | `len` | `module` | `0.0064` | `22` | `0` | Critical Choke Point |
| #8 | `_rel` | `module` | `0.0061` | `22` | `0` | Critical Choke Point |
| #9 | `replace` | `module` | `0.0055` | `11` | `0` | Critical Choke Point |
| #10 | `lower` | `module` | `0.0054` | `22` | `0` | Critical Choke Point |
| #11 | `read_text` | `module` | `0.0050` | `20` | `0` | Critical Choke Point |
| #12 | `GraphEdge` | `module` | `0.0049` | `23` | `0` | Critical Choke Point |
| #13 | `round` | `module` | `0.0048` | `2` | `0` | High Importance |
| #14 | `BaseModel` | `module` | `0.0047` | `2` | `0` | High Importance |
| #15 | `resolve` | `module` | `0.0044` | `7` | `0` | Critical Choke Point |

## Relationship Types Distribution

| Relationship Type | Count | Description |
| :--- | :--- | :--- |
| `calls` | `805` | Inter-component connection |
| `exposes` | `276` | Inter-component connection |
| `imports` | `111` | Inter-component connection |
| `inherits` | `14` | Inter-component connection |
| `depends_on` | `9` | Inter-component connection |

---
*Interactive visual graph available in `knowledge_graph.html`*