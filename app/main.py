"""CLI entrypoint using Click."""

import sys
from pathlib import Path

import click

from app.config import DEFAULT_RULES_PATH, VERSION
from app.detector import detect_service_type
from app.loader import load_rules
from app.reporter import (
    print_header,
    report_json,
    report_terminal,
    report_terminal_summary,
)
from app.scanner import discover_repos, scan_all, scan_repo

# Import checks to trigger registration
import app.checks  # noqa: F401

from app.checks.base import Status


@click.group()
@click.version_option(version=VERSION)
def cli():
    """aspirant-auditor — Automated convention checker for aspirant-* repos."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option("--category", default=None, help="Run only one check category")
@click.option("--verbose", is_flag=True, help="Show PASS results too")
@click.option("--rules", "rules_path", type=click.Path(exists=True), default=None)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def scan(path, fmt, category, verbose, rules_path, no_color):
    """Scan a single aspirant-* repo."""
    repo_path = Path(path).resolve()
    rp = Path(rules_path) if rules_path else DEFAULT_RULES_PATH
    rules = load_rules(rp)
    service_type = detect_service_type(repo_path)

    results = scan_repo(repo_path, rules, category_filter=category)

    if fmt == "json":
        click.echo(report_json({repo_path.name: results}))
    else:
        print_header(no_color)
        report_terminal(repo_path.name, service_type, results, verbose, no_color)

    has_failures = any(r.status == Status.FAIL for r in results)
    sys.exit(1 if has_failures else 0)


@cli.command("scan-all")
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option("--category", default=None, help="Run only one check category")
@click.option("--verbose", is_flag=True, help="Show PASS results too")
@click.option("--rules", "rules_path", type=click.Path(exists=True), default=None)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def scan_all_cmd(path, fmt, category, verbose, rules_path, no_color):
    """Scan all aspirant-* repos under a directory."""
    base_path = Path(path).resolve()
    rp = Path(rules_path) if rules_path else DEFAULT_RULES_PATH

    all_results = scan_all(base_path, rp, category_filter=category)

    if fmt == "json":
        click.echo(report_json(all_results))
    else:
        print_header(no_color)
        rules = load_rules(rp)
        for repo_name, results in sorted(all_results.items()):
            repo_path = base_path / repo_name
            service_type = detect_service_type(repo_path)
            report_terminal(repo_name, service_type, results, verbose, no_color)

        report_terminal_summary(all_results, no_color)

    has_failures = any(
        r.status == Status.FAIL
        for results in all_results.values()
        for r in results
    )
    sys.exit(1 if has_failures else 0)


@cli.command("scan-deploy")
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json"]), default="terminal")
@click.option("--category", default=None, help="Run only one check category")
@click.option("--verbose", is_flag=True, help="Show PASS results too")
@click.option("--rules", "rules_path", type=click.Path(exists=True), default=None)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def scan_deploy(path, fmt, category, verbose, rules_path, no_color):
    """Validate aspirant-deploy specifically (compose checks)."""
    repo_path = Path(path).resolve()
    rp = Path(rules_path) if rules_path else DEFAULT_RULES_PATH
    rules = load_rules(rp)

    results = scan_repo(
        repo_path,
        rules,
        service_type="deploy",
        category_filter=category,
        deploy_path=repo_path,
    )

    if fmt == "json":
        click.echo(report_json({repo_path.name: results}))
    else:
        print_header(no_color)
        report_terminal(repo_path.name, "deploy", results, verbose, no_color)

    has_failures = any(r.status == Status.FAIL for r in results)
    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    cli()
