"""Check: Git hygiene — .env safety, .gitignore completeness."""

from app.checks.base import CheckResult, RepoContext, Status, check


@check(category="Git Hygiene")
def check_gitignore(ctx: RepoContext) -> list[CheckResult]:
    results = []
    gitignore_path = ctx.repo_path / ".gitignore"

    if not gitignore_path.exists():
        results.append(CheckResult(
            check_id="git_hygiene.gitignore_exists",
            category="Git Hygiene",
            status=Status.FAIL,
            message=".gitignore file missing",
        ))
        return results

    content = gitignore_path.read_text()

    required_entries = ctx.rules.get("gitignore", {}).get("required_entries", [])
    for entry in required_entries:
        check_id = f"git_hygiene.gitignore.{entry.strip('/').replace('.', '_')}"
        if entry in content:
            results.append(CheckResult(
                check_id=check_id,
                category="Git Hygiene",
                status=Status.PASS,
                message=f".gitignore includes {entry}",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Git Hygiene",
                status=Status.WARN,
                message=f".gitignore missing entry: {entry}",
            ))

    return results


@check(category="Git Hygiene")
def check_env_not_committed(ctx: RepoContext) -> list[CheckResult]:
    """Check that .env files are not present (they should be gitignored)."""
    results = []
    env_file = ctx.repo_path / ".env"

    # We can't truly check if it's tracked without git, but we can check
    # if .gitignore has the entry
    gitignore_path = ctx.repo_path / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if ".env" in content:
            results.append(CheckResult(
                check_id="git_hygiene.env_ignored",
                category="Git Hygiene",
                status=Status.PASS,
                message=".env is listed in .gitignore",
            ))
        else:
            results.append(CheckResult(
                check_id="git_hygiene.env_ignored",
                category="Git Hygiene",
                status=Status.FAIL,
                message=".env is NOT listed in .gitignore — secrets may be committed",
            ))

    return results
