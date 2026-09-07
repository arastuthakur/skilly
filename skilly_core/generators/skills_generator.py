"""
Skills.md generator for Skilly.
Produces a rich, standardized, human and agent-readable capability catalog
documenting all runnable commands, API endpoints, domain services, data models,
and utility skills.
"""

from typing import Dict, List
from skilly_core.models import ProjectAnalysisResult, Skill, SkillCategory


class SkillsGenerator:
    """Generates the skills.md documentation from extracted project analysis."""

    def generate(self, result: ProjectAnalysisResult) -> str:
        summary = result.summary
        skills_by_cat: Dict[SkillCategory, List[Skill]] = {cat: [] for cat in SkillCategory}
        for s in result.skills:
            skills_by_cat[s.category].append(s)

        lines: List[str] = []

        # YAML Frontmatter
        lines.append("---")
        lines.append(f"project: \"{summary.name}\"")
        lines.append(f"total_skills: {len(result.skills)}")
        lines.append(f"languages: {list(summary.languages.keys())}")
        lines.append(f"frameworks: {summary.frameworks}")
        lines.append("generator: \"skilly (deterministic LLM-free AST analyzer)\"")
        lines.append("---\n")

        # Title
        lines.append(f"# Project Skills & Capabilities: {summary.name}\n")
        lines.append("> Auto-generated capability catalog extracted via static AST and manifest context.\n")

        # Summary Table
        health = getattr(result, "health", None)
        grade_badge = f"`{health.grade}` ({health.score}/100 - {health.summary_text})" if health else "`A`"

        lines.append("## Repository Capabilities Overview\n")
        lines.append("| Metric | Count / Detail |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **Architecture Health Grade** | {grade_badge} |")
        lines.append(f"| **Primary Languages** | {', '.join(f'{k} ({v} files)' for k, v in summary.languages.items()) or 'Generic'} |")
        lines.append(f"| **Frameworks / Tooling** | {', '.join(summary.frameworks) or 'Standard Library'} |")
        lines.append(f"| **Total Skills Cataloged** | `{len(result.skills)}` |")
        lines.append(f"| **Knowledge Graph Entities** | `{summary.total_nodes} nodes, {summary.total_edges} edges` |")
        lines.append(f"| **Runnable Commands & Workflows** | `{len(skills_by_cat[SkillCategory.COMMAND]) + len(skills_by_cat[SkillCategory.WORKFLOW])}` |")
        lines.append(f"| **API Endpoints** | `{len(skills_by_cat[SkillCategory.API_ENDPOINT])}` |")
        lines.append(f"| **Domain Services & Models** | `{len(skills_by_cat[SkillCategory.DOMAIN_SERVICE]) + len(skills_by_cat[SkillCategory.DATA_MODEL])}` |")
        lines.append("")

        # Table of Contents
        lines.append("## Table of Contents")
        lines.append("- [1. Runnable Commands & CLI Workflows](#1-runnable-commands--cli-workflows)")
        lines.append("- [2. API Endpoints & Routes](#2-api-endpoints--routes)")
        lines.append("- [3. Domain Services & Key Controllers](#3-domain-services--key-controllers)")
        lines.append("- [4. Data Models & Schemas](#4-data-models--schemas)")
        lines.append("- [5. Core Exported Functions & Utilities](#5-core-exported-functions--utilities)")
        lines.append("- [6. Environment & Configuration](#6-environment--configuration)")
        lines.append("- [7. Architectural Hubs & Central Components](#7-architectural-hubs--central-components)\n")

        # Section 1: Runnable Commands & CLI Workflows
        commands = skills_by_cat[SkillCategory.COMMAND] + skills_by_cat[SkillCategory.WORKFLOW]
        lines.append("## 1. Runnable Commands & CLI Workflows\n")
        if commands:
            lines.append("| Command / Skill | Type | Description | Location | Usage Example |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for cmd in commands:
                cat_label = "Workflow" if cmd.category == SkillCategory.WORKFLOW else "CLI Command"
                ex = f"`{cmd.example_usage}`" if cmd.example_usage else "`N/A`"
                lines.append(f"| **{cmd.name}** | `{cat_label}` | {cmd.description} | `{cmd.location}` | {ex} |")
            lines.append("")

            # Code block reference
            lines.append("### Command Execution Cheat-Sheet")
            lines.append("```bash")
            for cmd in commands:
                if cmd.example_usage:
                    lines.append(f"# {cmd.description}")
                    lines.append(f"{cmd.example_usage}\n")
            lines.append("```\n")
        else:
            lines.append("_No CLI commands or script workflows detected in project manifests._\n")

        # Section 2: API Endpoints & Routes
        api_skills = skills_by_cat[SkillCategory.API_ENDPOINT]
        lines.append("## 2. API Endpoints & Routes\n")
        if api_skills:
            lines.append("| HTTP Method & Route | Description | Handler / Location | Quick Curl Invocation |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for ep in api_skills:
                loc = f"`{ep.location}`"
                ex = f"`{ep.example_usage}`" if ep.example_usage else "N/A"
                lines.append(f"| **{ep.name}** | {ep.description} | {loc} | {ex} |")
            lines.append("")
        else:
            lines.append("_No REST, GraphQL, or HTTP endpoint handlers detected._\n")

        # Section 3: Domain Services & Key Controllers
        services = skills_by_cat[SkillCategory.DOMAIN_SERVICE]
        lines.append("## 3. Domain Services & Key Controllers\n")
        if services:
            for s in services:
                lines.append(f"### `{s.name}`")
                lines.append(f"- **Role**: {s.description}")
                lines.append(f"- **Location**: [`{s.location}`]({s.location})")
                if s.signature:
                    lines.append(f"- **Signature**: `{s.signature}`")
                if s.example_usage:
                    lines.append(f"```python\n{s.example_usage}\n```")
                lines.append("")
        else:
            lines.append("_No domain services or primary controller classes detected._\n")

        # Section 4: Data Models & Schemas
        models = skills_by_cat[SkillCategory.DATA_MODEL]
        lines.append("## 4. Data Models & Schemas\n")
        if models:
            lines.append("| Model / Schema | Description | Location | Details |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for m in models:
                details = m.signature or ", ".join(m.tags)
                lines.append(f"| **`{m.name}`** | {m.description} | `{m.location}` | `{details}` |")
            lines.append("")
        else:
            lines.append("_No explicit data models, Pydantic schemas, or structs detected._\n")

        # Section 5: Core Exported Functions & Utilities
        functions = skills_by_cat[SkillCategory.CORE_FUNCTION]
        lines.append("## 5. Core Exported Functions & Utilities\n")
        if functions:
            lines.append(f"Found **{len(functions)}** core callable functions:\n")
            for fn in functions[:30]:  # Cap at top 30 to avoid overwhelming file size
                lines.append(f"#### `{fn.name}`")
                lines.append(f"- **Description**: {fn.description}")
                lines.append(f"- **Location**: `{fn.location}`")
                if fn.signature:
                    lines.append(f"- **Signature**: `{fn.signature}`")
                if fn.parameters:
                    param_str = ", ".join(f"`{p['name']}` ({p.get('type') or 'any'})" for p in fn.parameters)
                    lines.append(f"- **Parameters**: {param_str}")
                if fn.return_type:
                    lines.append(f"- **Returns**: `{fn.return_type}`")
                if fn.example_usage:
                    lines.append(f"```python\n{fn.example_usage}\n```")
                lines.append("")
            if len(functions) > 30:
                lines.append(f"_...and {len(functions) - 30} more exported functions available in source code._\n")
        else:
            lines.append("_No standalone exported helper functions detected._\n")

        # Section 6: Environment & Configuration
        configs = skills_by_cat[SkillCategory.CONFIG]
        lines.append("## 6. Environment & Configuration\n")
        if configs:
            for cfg in configs:
                lines.append(f"### {cfg.name}")
                lines.append(f"Defined in: `{cfg.location}`\n")
                if cfg.parameters:
                    lines.append("| Variable Name | Default Value | Defined Line |")
                    lines.append("| :--- | :--- | :--- |")
                    for p in cfg.parameters:
                        lines.append(f"| `{p.get('name')}` | `{p.get('default') or ''}` | line {p.get('line')} |")
                    lines.append("")
        else:
            lines.append("_No environment templates (.env.example) found._\n")

        # Section 7: Architectural Hubs & Central Components
        lines.append("## 7. Architectural Hubs & Central Components\n")
        lines.append("The following components exhibit the highest architectural centrality (PageRank & connectivity):\n")
        if result.hubs:
            lines.append("| Rank | Component / Symbol | Type | Centrality Score | Inbound Deps | Outbound Calls | Description |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for idx, hub in enumerate(result.hubs, 1):
                t_label = hub.type.value if hasattr(hub.type, "value") else str(hub.type)
                desc = hub.description or "Core system component"
                lines.append(f"| #{idx} | **`{hub.label}`** | `{t_label}` | `{hub.importance_score}` | `{hub.in_degree}` | `{hub.out_degree}` | {desc} |")
            lines.append("")
        else:
            lines.append("_Graph has no distinct central hubs._\n")

        lines.append("---\n*Generated autonomously by **Skilly** (Zero-LLM Architecture Synthesizer) • Created by [Arastu Thakur](https://arastuthakur.com.np/) • [PyPI](https://pypi.org/project/skilly-ai/) • [GitHub](https://github.com/arastuthakur/skilly) • [LinkedIn](https://www.linkedin.com/in/arastuthakur/)*")
        return "\n".join(lines)
