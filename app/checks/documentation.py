"""Check: Documentation — doc files, sections, changelog format."""

import re

from app.checks.base import CheckResult, RepoContext, Status, check


@check(category="Documentation")
def check_changelog_format(ctx: RepoContext) -> list[CheckResult]:
    """Check changelog has date headers matching ### YYYY-MM-DD."""
    results = []
    docs_dir = ctx.repo_path / "docs"

    if not docs_dir.exists():
        results.append(CheckResult(
            check_id="documentation.changelog_format",
            category="Documentation",
            status=Status.SKIP,
            message="No docs/ directory found",
        ))
        return results

    changelog = docs_dir / "CHANGELOG.md"
    if not changelog.exists():
        return results  # Already caught by required_files

    content = changelog.read_text()
    pattern = ctx.rules.get("documentation", {}).get(
        "changelog_date_pattern", r"^### \d{4}-\d{2}-\d{2}"
    )

    if re.search(pattern, content, re.MULTILINE):
        results.append(CheckResult(
            check_id="documentation.changelog_format",
            category="Documentation",
            status=Status.PASS,
            message="Changelog has date headers (### YYYY-MM-DD)",
        ))
    else:
        results.append(CheckResult(
            check_id="documentation.changelog_format",
            category="Documentation",
            status=Status.WARN,
            message="Changelog missing date headers (expected ### YYYY-MM-DD)",
        ))

    return results


@check(category="Documentation")
def check_spec_sections(ctx: RepoContext) -> list[CheckResult]:
    """Check spec has required sections."""
    results = []
    docs_dir = ctx.repo_path / "docs"

    if not docs_dir.exists():
        return []

    # Find spec file (may be named {PROJECT}_SPEC.md or SPEC.md)
    spec_files = list(docs_dir.glob("*SPEC*"))
    if not spec_files:
        return []  # Already caught by required_files

    spec_content = spec_files[0].read_text()
    required_sections = ctx.rules.get("documentation", {}).get(
        "spec_required_sections", []
    )

    for section in required_sections:
        check_id = f"documentation.spec_section.{section.lower().replace(' ', '_')}"
        # Case-insensitive search for section heading
        if re.search(rf"^#+\s+.*{re.escape(section)}", spec_content, re.MULTILINE | re.IGNORECASE):
            results.append(CheckResult(
                check_id=check_id,
                category="Documentation",
                status=Status.PASS,
                message=f"Spec has section: {section}",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Documentation",
                status=Status.WARN,
                message=f"Spec missing section: {section}",
            ))

    return results


@check(category="Documentation")
def check_architecture_diagrams(ctx: RepoContext) -> list[CheckResult]:
    """Check architecture doc has diagrams (mermaid or ASCII)."""
    results = []
    docs_dir = ctx.repo_path / "docs"

    if not docs_dir.exists():
        return []

    arch_files = list(docs_dir.glob("*ARCHITECTURE*"))
    if not arch_files:
        return []

    content = arch_files[0].read_text()
    has_mermaid = "```mermaid" in content
    has_ascii = any(c in content for c in ["┌", "└", "│", "├", "─", "▶", "▼"])

    if has_mermaid or has_ascii:
        results.append(CheckResult(
            check_id="documentation.architecture_diagrams",
            category="Documentation",
            status=Status.PASS,
            message="Architecture doc contains diagrams",
        ))
    else:
        results.append(CheckResult(
            check_id="documentation.architecture_diagrams",
            category="Documentation",
            status=Status.WARN,
            message="Architecture doc has no diagrams (mermaid or ASCII)",
        ))

    return results


@check(category="Documentation")
def check_operations_sections(ctx: RepoContext) -> list[CheckResult]:
    """Check operations doc has required sections."""
    results = []
    docs_dir = ctx.repo_path / "docs"

    if not docs_dir.exists():
        return []

    ops_files = list(docs_dir.glob("*OPERATIONS*"))
    if not ops_files:
        return []

    content = ops_files[0].read_text()
    required_sections = ctx.rules.get("documentation", {}).get(
        "operations_required_sections", []
    )

    for section in required_sections:
        check_id = f"documentation.ops_section.{section.lower().replace(' ', '_')}"
        if re.search(rf"^#+\s+.*{re.escape(section)}", content, re.MULTILINE | re.IGNORECASE):
            results.append(CheckResult(
                check_id=check_id,
                category="Documentation",
                status=Status.PASS,
                message=f"Operations doc has section: {section}",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Documentation",
                status=Status.WARN,
                message=f"Operations doc missing section: {section}",
            ))

    return results
