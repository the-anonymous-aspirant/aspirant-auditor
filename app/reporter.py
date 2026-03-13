"""Terminal (Rich) and JSON output."""

import json

from rich.console import Console
from rich.table import Table

from app.checks.base import CheckResult, Status
from app.config import VERSION


def _status_style(status: Status) -> str:
    return {
        Status.PASS: "green",
        Status.FAIL: "bold red",
        Status.WARN: "yellow",
        Status.SKIP: "dim",
    }[status]


def _status_icon(status: Status) -> str:
    return {
        Status.PASS: "PASS",
        Status.FAIL: "FAIL",
        Status.WARN: "WARN",
        Status.SKIP: "SKIP",
    }[status]


def report_terminal(
    repo_name: str,
    service_type: str,
    results: list[CheckResult],
    verbose: bool = False,
    no_color: bool = False,
) -> None:
    """Print results for a single repo to terminal."""
    console = Console(no_color=no_color)

    console.print(f"\nScanning [bold]{repo_name}[/bold] ({service_type})")
    console.print("━" * 40)

    # Group by category
    categories: dict[str, list[CheckResult]] = {}
    for r in results:
        categories.setdefault(r.category, []).append(r)

    for category, checks in categories.items():
        # Filter: only show category if it has non-PASS results (unless verbose)
        visible = [c for c in checks if verbose or c.status != Status.PASS]
        if not visible:
            continue

        console.print(f"\n[bold]{category}[/bold]")
        for c in visible:
            style = _status_style(c.status)
            icon = _status_icon(c.status)
            path_suffix = f" ({c.path})" if c.path else ""
            console.print(f"  [{style}]{icon}[/{style}]  {c.message}{path_suffix}")

    # Summary
    counts = {s: 0 for s in Status}
    for r in results:
        counts[r.status] += 1

    console.print("\n" + "━" * 40)
    parts = []
    if counts[Status.PASS]:
        parts.append(f"[green]{counts[Status.PASS]} passed[/green]")
    if counts[Status.FAIL]:
        parts.append(f"[bold red]{counts[Status.FAIL]} failed[/bold red]")
    if counts[Status.WARN]:
        parts.append(f"[yellow]{counts[Status.WARN]} warnings[/yellow]")
    if counts[Status.SKIP]:
        parts.append(f"[dim]{counts[Status.SKIP]} skipped[/dim]")
    console.print(f"Summary: {', '.join(parts)}")


def report_terminal_summary(
    all_results: dict[str, list[CheckResult]],
    no_color: bool = False,
) -> None:
    """Print a summary table across all repos."""
    console = Console(no_color=no_color)

    table = Table(title="\nAll Repos Summary")
    table.add_column("Repository", style="bold")
    table.add_column("Pass", style="green", justify="right")
    table.add_column("Fail", style="red", justify="right")
    table.add_column("Warn", style="yellow", justify="right")
    table.add_column("Skip", style="dim", justify="right")

    for repo_name, results in sorted(all_results.items()):
        counts = {s: 0 for s in Status}
        for r in results:
            counts[r.status] += 1
        table.add_row(
            repo_name,
            str(counts[Status.PASS]),
            str(counts[Status.FAIL]),
            str(counts[Status.WARN]),
            str(counts[Status.SKIP]),
        )

    console.print(table)


def report_json(all_results: dict[str, list[CheckResult]]) -> str:
    """Return JSON string of all results."""
    output = {}
    for repo_name, results in all_results.items():
        output[repo_name] = [
            {
                "check_id": r.check_id,
                "category": r.category,
                "status": r.status.value,
                "message": r.message,
                "path": r.path,
            }
            for r in results
        ]
    return json.dumps(output, indent=2)


def print_header(no_color: bool = False) -> None:
    """Print the tool header."""
    console = Console(no_color=no_color)
    console.print(f"[bold]aspirant-auditor[/bold] v{VERSION}")
