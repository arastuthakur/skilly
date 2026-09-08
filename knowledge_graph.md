# Knowledge Graph Architecture: Model

> Structural and semantic topology extracted deterministically via AST and import graphs.

## 📈 Graph Metrics
- **Total Entities (Nodes)**: `490`
- **Total Relationships (Edges)**: `1321`
- **Architectural Clusters**: `5`
- **Circular Dependency Cycles**: `1`

### ⚠️ Circular Dependencies Detected
The following circular reference cycles were identified in the codebase:

- `file:tests/fixtures/sample_circular_app/a.py` ➔ `file:tests/fixtures/sample_circular_app/b.py` ➔ `file:tests/fixtures/sample_circular_app/a.py`

## Architectural Clusters & Subdomains

### Skilly_core Domain (`336` components)
- **Key Components**: `ManifestExtractor._parse_gemfile`, `ManifestExtractor._parse_github_workflows`, `PythonASTExtractor.extract`, `ManifestExtractor._parse_go_mod`, `ManifestExtractor._parse_package_json`, `removesuffix`, `JavaScriptExtractor`, `submit`, `setdefault`, `split`
- _...and 326 more components_

### Tests Domain (`138` components)
- **Key Components**: `dumps`, `test_pep561_py_typed_exists`, `loads`, `safe_load`, `readouterr`, `test_manifest_extractor_package_json`, `GraphMarkdownGenerator`, `to_dict`, `test_ci_fail_on_cycles_cli`, `from_dict`
- _...and 128 more components_

### Root Domain (`6` components)
- **Key Components**: `setup.py`, `setuptools`, `start`, `test`, `skilly`, `install.sh`

### .agents Domain (`9` components)
- **Key Components**: `api-security-testing`, `application-security-testing`, `ci-security-scanning-with-strix`, `find-security-vulnerabilities-in-code`, `fix-security-vulnerabilities-with-strix`, `managed-pentesting-with-strix`, `owasp-top-10-testing`, `penetration-testing-with-strix`, `web-app-penetration-testing`

### .github Domain (`1` components)
- **Key Components**: `generate_project_skills___knowledge_graph`

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
    replace["replace (module)"]
    GraphNode["GraphNode (module)"]
    Skill["Skill (module)"]
    isinstance["isinstance (module)"]
    _rel["_rel (module)"]
    file_skilly_py -->|imports| file_skilly_core_cli_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_extractors_manifest_extractor_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_extractors_python_extractor_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_extractors_javascript_extractor_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_extractors_polyglot_extractor_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_extractors_universal_engine_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_graph_engine_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_models_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_config_py
    file_skilly_core_analyzer_py -->|imports| file_skilly_core_cache_py
    file_skilly_core_cache_py -->|imports| file_skilly_core_models_py
    file_skilly_core_cli_py -->|imports| file_skilly_core___init___py
    file_skilly_core_cli_py -->|imports| file_skilly_core_analyzer_py
    file_skilly_core_graph_engine_py -->|imports| file_skilly_core_models_py
    file_skilly_core___init___py -->|imports| file_skilly_core_analyzer_py
    file_skilly_core___init___py -->|imports| file_skilly_core_models_py
    file_skilly_core_extractors_base_py -->|imports| file_skilly_core_models_py
    file_skilly_core_extractors_javascript_extractor_py -->|imports| file_skilly_core_extractors_base_py
    file_skilly_core_extractors_javascript_extractor_py -->|imports| file_skilly_core_models_py
    file_skilly_core_extractors_manifest_extractor_py -->|imports| file_skilly_core_extractors_base_py
    file_skilly_core_extractors_manifest_extractor_py -->|imports| file_skilly_core_models_py
    file_skilly_core_extractors_polyglot_extractor_py -->|imports| file_skilly_core_extractors_base_py
    file_skilly_core_extractors_polyglot_extractor_py -->|imports| file_skilly_core_models_py
    file_skilly_core_extractors_python_extractor_py -->|imports| file_skilly_core_extractors_base_py
    file_skilly_core_extractors_python_extractor_py -->|imports| file_skilly_core_models_py
```

## Central Architectural Hubs (PageRank)

| Rank | Symbol / Module | Type | PageRank | In-Degree | Out-Degree | Impact / Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| #1 | `append` | `module` | `0.0098` | `45` | `0` | Critical Choke Point |
| #2 | `str` | `module` | `0.0082` | `18` | `0` | Critical Choke Point |
| #3 | `GraphNode` | `module` | `0.0079` | `37` | `0` | Critical Choke Point |
| #4 | `Path` | `module` | `0.0073` | `23` | `0` | Critical Choke Point |
| #5 | `isinstance` | `module` | `0.0072` | `13` | `0` | Critical Choke Point |
| #6 | `Skill` | `module` | `0.0071` | `31` | `0` | Critical Choke Point |
| #7 | `_rel` | `module` | `0.0067` | `27` | `0` | Critical Choke Point |
| #8 | `len` | `module` | `0.0064` | `26` | `0` | Critical Choke Point |
| #9 | `replace` | `module` | `0.0062` | `12` | `0` | Critical Choke Point |
| #10 | `models.py` | `file` | `0.0059` | `19` | `18` | Critical Choke Point |
| #11 | `lower` | `module` | `0.0056` | `24` | `0` | Critical Choke Point |
| #12 | `read_text` | `module` | `0.0051` | `22` | `0` | Critical Choke Point |
| #13 | `round` | `module` | `0.0051` | `2` | `0` | High Importance |
| #14 | `write_text` | `module` | `0.0049` | `16` | `0` | Critical Choke Point |
| #15 | `ProjectAnalyzer` | `module` | `0.0049` | `14` | `0` | Critical Choke Point |

## Relationship Types Distribution

| Relationship Type | Count | Description |
| :--- | :--- | :--- |
| `calls` | `893` | Inter-component connection |
| `exposes` | `258` | Inter-component connection |
| `imports` | `147` | Inter-component connection |
| `inherits` | `14` | Inter-component connection |
| `depends_on` | `9` | Inter-component connection |

---
*Interactive visual graph available in `knowledge_graph.html`*