"""Orchestration: discover repos, run checks, collect results."""

from pathlib import Path

from app.checks.base import CheckResult, RepoContext, Status, get_checks
from app.detector import detect_service_type
from app.loader import load_rules


def discover_repos(base_path: Path) -> list[Path]:
    """Find all aspirant-* directories under base_path."""
    repos = sorted(
        p for p in base_path.iterdir()
        if p.is_dir() and p.name.startswith("aspirant-")
    )
    return repos


def scan_repo(
    repo_path: Path,
    rules: dict,
    service_type: str | None = None,
    category_filter: str | None = None,
    all_repos: list[Path] | None = None,
    deploy_path: Path | None = None,
) -> list[CheckResult]:
    """Run all applicable checks against a single repo."""
    if service_type is None:
        service_type = detect_service_type(repo_path)

    ctx = RepoContext(
        repo_path=repo_path,
        repo_name=repo_path.name,
        service_type=service_type,
        rules=rules,
        all_repos=all_repos or [],
        deploy_path=deploy_path,
    )

    results = []
    for fn, category, applies_to in get_checks():
        # Filter by category if specified
        if category_filter and category.lower() != category_filter.lower():
            continue

        # Skip checks that don't apply to this service type
        if applies_to and service_type not in applies_to:
            continue

        results.extend(fn(ctx))

    return results


def scan_all(
    base_path: Path,
    rules_path: Path,
    category_filter: str | None = None,
) -> dict[str, list[CheckResult]]:
    """Scan all aspirant-* repos under base_path. Returns {repo_name: results}."""
    rules = load_rules(rules_path)
    repos = discover_repos(base_path)

    # Find deploy repo if present
    deploy_path = None
    for r in repos:
        if r.name == "aspirant-deploy":
            deploy_path = r
            break

    all_results = {}
    for repo in repos:
        results = scan_repo(
            repo,
            rules,
            category_filter=category_filter,
            all_repos=repos,
            deploy_path=deploy_path,
        )
        all_results[repo.name] = results

    return all_results
