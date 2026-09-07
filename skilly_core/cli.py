"""
Command-line interface for Skilly.
Usage:
    skilly [projectname_or_path] [options]
    skilly .
    skilly my-project --serve
"""

import argparse
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from skilly_core import __version__
from skilly_core.analyzer import ProjectAnalyzer

# Try importing rich for premium terminal styling
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    HAVE_RICH = True
    # If legacy windows console without utf-8, use safe console
    console = Console(highlight=False)
except ImportError:
    HAVE_RICH = False
    console = None


def print_banner():
    if HAVE_RICH:
        banner = (
            "[bold cyan]>> Skilly[/bold cyan] [dim]v" + __version__ + "[/dim] [dim]by [bold white]Arastu Thakur[/bold white] (https://arastuthakur.com.np/)[/dim]\n"
            "[italic white]Autonomous LLM-free Codebase to Skills.md & Knowledge Graph Synthesizer[/italic white]"
        )
        try:
            console.print(Panel(banner, border_style="cyan", padding=(0, 2)))
        except Exception:
            print(f">> Skilly v{__version__} by Arastu Thakur (https://arastuthakur.com.np/)")
    else:
        print(f"=== Skilly v{__version__} by Arastu Thakur (https://arastuthakur.com.np/) ===")
        print("Autonomous LLM-free Codebase to Skills.md & Knowledge Graph Synthesizer\n")


def main(args: Optional[list] = None):
    parser = argparse.ArgumentParser(
        prog="skilly",
        description="Convert any codebase into skills.md and an interactive knowledge graph without LLMs.",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target project directory or name (default: current directory '.')",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=None,
        help="Output directory for generated artifacts (default: target project directory)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start a local web server and open the interactive knowledge graph in browser",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for local server when using --serve (default: 8765)",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        default=None,
        help="Path to .skilly.json or .skilly.yaml configuration file",
    )
    parser.add_argument(
        "--fail-on-grade",
        dest="fail_on_grade",
        default=None,
        help="Fail (exit code 2) if Architecture Health Grade is below threshold (e.g. B, C)",
    )
    parser.add_argument(
        "--fail-on-cycles",
        action="store_true",
        help="Fail (exit code 2) if circular dependency cycles are detected",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass incremental cache and perform full fresh scan",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker threads for parallel extraction",
    )
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Output machine-readable JSON analysis summary to stdout",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="Generate only skills.md",
    )
    parser.add_argument(
        "--graph-only",
        action="store_true",
        help="Generate only knowledge graph artifacts",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run silently without progress banners",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"skilly {__version__}",
    )

    parsed_args = parser.parse_args(args)

    target_path = Path(parsed_args.target).resolve()
    if not target_path.exists():
        msg = f"Error: Target path does not exist: {target_path}"
        if HAVE_RICH:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    # Load enterprise config
    from skilly_core.config import SkillyConfig
    config = SkillyConfig.load(target_path, explicit_config_path=parsed_args.config_path)
    if parsed_args.no_cache:
        config.use_cache = False
    if parsed_args.workers:
        config.max_workers = parsed_args.workers
    if parsed_args.fail_on_grade:
        config.fail_on_grade = parsed_args.fail_on_grade
    if parsed_args.fail_on_cycles:
        config.fail_on_cycles = True

    if not parsed_args.quiet and not parsed_args.json_summary:
        print_banner()
        if HAVE_RICH:
            console.print(f"[bold green][*] Analyzing project:[/bold green] [yellow]{target_path}[/yellow]")
        else:
            print(f"[*] Analyzing project: {target_path}")

    # Run analysis with config
    analyzer = ProjectAnalyzer(target_path, config=config)

    if HAVE_RICH and not parsed_args.quiet:
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Parsing ASTs, manifests, routes, and call graphs...", total=None)
            result = analyzer.analyze()
            progress.update(task, description="Building knowledge graph & PageRank topology...")
    else:
        result = analyzer.analyze()

    # Determine what to write
    out_dir = Path(parsed_args.output_dir).resolve() if parsed_args.output_dir else target_path

    if parsed_args.skills_only:
        p = analyzer.write_artifacts(result, output_dir=out_dir)
        # remove graph artifacts if requested skills-only
        for k in ["graph_html", "graph_json", "graph_md"]:
            if k in p and p[k].exists():
                p[k].unlink()
        written = {"skills_md": p["skills_md"]}
    elif parsed_args.graph_only:
        p = analyzer.write_artifacts(result, output_dir=out_dir)
        if "skills_md" in p and p["skills_md"].exists():
            p["skills_md"].unlink()
        written = {k: v for k, v in p.items() if k != "skills_md"}
    else:
        written = analyzer.write_artifacts(result, output_dir=out_dir)

    # Output Summary Table
    if not parsed_args.quiet:
        summary = result.summary
        if HAVE_RICH:
            table = Table(title="[bold cyan]Analysis & Graph Summary[/bold cyan]", border_style="dim")
            table.add_column("Category", style="cyan")
            health = getattr(result, "health", None)
            if health:
                grade_color = "green" if "A" in health.grade else ("yellow" if "B" in health.grade else "red")
                table.add_row("Architecture Health", f"[{grade_color}]{health.grade} ({health.score}/100)[/{grade_color}] - {health.summary_text}")

            table.add_row("Files Scanned", f"{summary.total_files} files ({summary.total_lines:,} lines)")
            table.add_row("Languages", ", ".join(f"{k} ({v})" for k, v in summary.languages.items()) or "Generic")
            table.add_row("Frameworks", ", ".join(summary.frameworks) or "Standard Library")
            table.add_row("Skills Extracted", f"[bold green]{len(result.skills)}[/bold green]")
            table.add_row("Graph Nodes", f"{summary.total_nodes} nodes")
            table.add_row("Graph Edges", f"{summary.total_edges} relations")
            table.add_row("Architectural Clusters", f"{len(result.clusters)} clusters")
            if result.circular_dependencies:
                table.add_row("Circular References", f"[bold yellow]{len(result.circular_dependencies)} detected[/bold yellow]")
            else:
                table.add_row("Circular References", "[green]None (Acyclic)[/green]")

            console.print(table)
            console.print("\n[bold green][OK] Successfully Generated Artifacts:[/bold green]")
            for key, path in written.items():
                console.print(f"  * [bold cyan]{path.name}[/bold cyan] -> [dim]{path}[/dim]")
            console.print("\n[dim]Synthesized by Skilly • Architected by [bold white]Arastu Thakur[/bold white] (https://arastuthakur.com.np/)[/dim]")
        else:
            print("\nAnalysis Summary:")
            print(f"- Files Scanned: {summary.total_files}")
            print(f"- Skills Cataloged: {len(result.skills)}")
            print(f"- Knowledge Graph: {summary.total_nodes} nodes, {summary.total_edges} edges")
            print("\nGenerated Artifacts:")
            for key, path in written.items():
                print(f"  * {path.name} -> {path}")
            print("\nSynthesized by Skilly • Architected by Arastu Thakur (https://arastuthakur.com.np/)")

    # Output JSON summary if requested (e.g. for CI pipelines or scripts)
    if parsed_args.json_summary:
        payload = {
            "summary": result.summary.to_dict(),
            "health": result.health.to_dict(),
            "artifacts": {k: str(v) for k, v in written.items()},
        }
        print(json.dumps(payload, indent=2))

    # CI Quality Gate Check
    if config.fail_on_cycles and result.circular_dependencies:
        msg = f"CI Quality Gate Failed: {len(result.circular_dependencies)} circular dependency cycles detected."
        if HAVE_RICH:
            console.print(f"\n[bold red][FAIL][/bold red] {msg}")
        else:
            print(f"\n[FAIL] {msg}", file=sys.stderr)
        sys.exit(2)

    if config.fail_on_grade:
        threshold = config.fail_on_grade.upper()
        # Grade hierarchy: A+ > A > B > C > D
        grades = ["D", "C", "B", "A", "A+"]
        current_idx = grades.index(result.health.grade) if result.health.grade in grades else 0
        thresh_idx = grades.index(threshold) if threshold in grades else 2
        if current_idx < thresh_idx:
            msg = f"CI Quality Gate Failed: Architecture grade '{result.health.grade}' is below required '{threshold}'."
            if HAVE_RICH:
                console.print(f"\n[bold red][FAIL][/bold red] {msg}")
            else:
                print(f"\n[FAIL] {msg}", file=sys.stderr)
            sys.exit(2)

    # Handle --serve
    if parsed_args.serve and "graph_html" in written:
        html_file = written["graph_html"]
        serve_dir = html_file.parent
        port = parsed_args.port

        class QuietHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(serve_dir), **kwargs)
            def log_message(self, format, *args):
                pass  # suppress request logging

        url = f"http://localhost:{port}/{html_file.name}"
        if HAVE_RICH:
            console.print(f"\n[bold green]>> Serving interactive Knowledge Graph at:[/bold green] [underline cyan]{url}[/underline cyan]")
            console.print("[dim]Press Ctrl+C to stop the server.[/dim]")
        else:
            print(f"\nServing interactive Knowledge Graph at: {url}")
            print("Press Ctrl+C to stop.")

        webbrowser.open(url)
        try:
            httpd = HTTPServer(("localhost", port), QuietHandler)
            httpd.serve_forever()
        except KeyboardInterrupt:
            if HAVE_RICH:
                console.print("\n[yellow]Server stopped.[/yellow]")
            else:
                print("\nServer stopped.")


if __name__ == "__main__":
    main()
