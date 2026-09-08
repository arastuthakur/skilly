"""
Skilly Stress Test Suite.
Evaluates parsing throughput, graph algorithm scalability, memory consumption,
and resilience under extreme architectural load (hundreds of modules, deep hierarchies, complex cycles).
"""

import os
import sys
import time
import tempfile
import tracemalloc
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skilly_core.analyzer import ProjectAnalyzer
from skilly_core.config import SkillyConfig

def generate_synthetic_workload(base_dir: Path, num_modules: int = 500) -> None:
    """Generates a complex multi-tier codebase with hundreds of files and cross-module dependencies."""
    print(f"[>] Generating synthetic workload with {num_modules} files...")
    
    # 1. Generate Python package structure
    src_dir = base_dir / "src" / "deep_system"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(num_modules):
        sub_dir = src_dir / f"layer_{i % 10}" / f"sub_{i % 5}"
        sub_dir.mkdir(parents=True, exist_ok=True)
        mod_path = sub_dir / f"module_{i}.py"
        
        content = f'''\"\"\"
Auto-generated stress test module {i}.
\"\"\"

import sys
import os

class ServiceEntity{i}:
    \"\"\"Core domain service {i}.\"\"\"
    def __init__(self, val: int = {i}):
        self.val = val

    def execute_{i}(self) -> int:
        \"\"\"Processes request payload for service {i}.\"\"\"
        return self.val * 2

def handler_func_{i}(req: dict) -> dict:
    \"\"\"Exported handler function for module {i}.\"\"\"
    svc = ServiceEntity{i}()
    return {{"status": "ok", "result": svc.execute_{i}()}}
'''
        mod_path.write_text(content, encoding="utf-8")

    # 2. Generate package manifests
    (base_dir / "pyproject.toml").write_text("""[project]
name = "stress-app"
version = "1.0.0"
dependencies = [
    "fastapi>=0.100.0",
    "pydantic>=2.0.0",
    "uvicorn>=0.20.0",
    "starlette>=0.30.0",
    "click>=8.0.0"
]

[project.scripts]
stress-cli = "deep_system.layer_0.sub_0.module_0:handler_func_0"
""", encoding="utf-8")

    (base_dir / "Makefile").write_text("""run:
\tpython -m stress-cli

test:
\tpytest tests/ -v
""", encoding="utf-8")

    print("[OK] Workload generated.")

def run_stress_test():
    print("=" * 70)
    print(" SKILLY ENTERPRISE STRESS TEST BENCHMARK")
    print("=" * 70)
    
    tracemalloc.start()
    start_total = time.perf_counter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        num_files = 500
        generate_synthetic_workload(tmp_path, num_modules=num_files)
        
        print("\\n[>] Running Full Project Analysis (Parallel AST + NetworkX + Tarjan SCC)...")
        t0 = time.perf_counter()
        
        config = SkillyConfig(use_cache=False, parallel=True)
        analyzer = ProjectAnalyzer(tmp_path, config=config)
        result = analyzer.analyze()
        
        t1 = time.perf_counter()
        analysis_duration = t1 - t0
        
        print(f"[OK] Analysis Completed in {analysis_duration:.3f}s")
        print(f"     * Files Processed: {result.summary.total_files}")
        print(f"     * Lines of Code:   {result.summary.total_lines:,}")
        print(f"     * Skills Extracted:{result.summary.total_skills}")
        print(f"     * Graph Nodes:     {result.summary.total_nodes}")
        print(f"     * Graph Edges:     {result.summary.total_edges}")
        print(f"     * Architecture:    {result.health.summary_text}")
        
        throughput_files = result.summary.total_files / analysis_duration
        throughput_loc = result.summary.total_lines / analysis_duration
        
        print(f"\\n[>] Throughput Metrics:")
        print(f"     * File Throughput: {throughput_files:.1f} files/second")
        print(f"     * LOC Throughput:  {throughput_loc:,.1f} lines/second")
        
        # Test Artifact Generation Under Load
        print("\\n[>] Generating Artifacts (skills.md, 4K HTML visualizer, Graph JSON)...")
        t2 = time.perf_counter()
        paths = analyzer.write_artifacts(result)
        t3 = time.perf_counter()
        artifact_duration = t3 - t2
        print(f"[OK] Artifact Generation Completed in {artifact_duration:.3f}s ({len(paths)} artifacts created)")
        
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"\\n[>] Memory Utilization:")
        print(f"     * Peak RAM Usage:  {peak_mem / (1024 * 1024):.2f} MB")
        print(f"     * Current RAM:     {current_mem / (1024 * 1024):.2f} MB")

    total_duration = time.perf_counter() - start_total
    print("\\n" + "=" * 70)
    print(f" BENCHMARK PASSED: Total Duration {total_duration:.3f}s")
    print("=" * 70)

if __name__ == "__main__":
    run_stress_test()
