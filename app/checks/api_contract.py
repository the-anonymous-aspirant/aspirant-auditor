"""Check: API contract — health endpoint static analysis."""

from app.checks.base import CheckResult, RepoContext, Status, check


@check(category="API Contract", applies_to=["python", "go"])
def check_health_endpoint(ctx: RepoContext) -> list[CheckResult]:
    """Check for /health route definition."""
    results = []

    if ctx.service_type == "python":
        routes_file = ctx.repo_path / "app" / "routes.py"
    elif ctx.service_type == "go":
        routes_file = ctx.repo_path / "server" / "routes.go"
        if not routes_file.exists():
            routes_file = ctx.repo_path / "routes.go"
    else:
        return []

    if not routes_file.exists():
        results.append(CheckResult(
            check_id="api_contract.health_route",
            category="API Contract",
            status=Status.FAIL,
            message="Routes file not found",
            path=str(routes_file.relative_to(ctx.repo_path)),
        ))
        return results

    content = routes_file.read_text()

    # Check for /health route
    if "/health" in content:
        results.append(CheckResult(
            check_id="api_contract.health_route",
            category="API Contract",
            status=Status.PASS,
            message="/health endpoint defined",
        ))
    else:
        results.append(CheckResult(
            check_id="api_contract.health_route",
            category="API Contract",
            status=Status.FAIL,
            message="/health endpoint not found in routes",
        ))

    return results


@check(category="API Contract", applies_to=["python", "go"])
def check_health_response_fields(ctx: RepoContext) -> list[CheckResult]:
    """Check health response includes required fields (status, service, version, checks)."""
    results = []

    # Search routes and schemas files for the field names
    search_files = []
    if ctx.service_type == "python":
        for name in ["routes.py", "schemas.py"]:
            f = ctx.repo_path / "app" / name
            if f.exists():
                search_files.append(f)
    elif ctx.service_type == "go":
        for candidate in [
            ctx.repo_path / "server" / "routes.go",
            ctx.repo_path / "routes.go",
            ctx.repo_path / "server" / "handlers" / "health.go",
        ]:
            if candidate.exists():
                search_files.append(candidate)

    if not search_files:
        return []

    combined_content = "\n".join(f.read_text() for f in search_files)
    required_fields = ctx.rules.get("api_contract", {}).get(
        "health_response_fields", []
    )

    for field in required_fields:
        check_id = f"api_contract.health_field.{field}"
        # Check for field name in quotes or as key
        if f'"{field}"' in combined_content or f"'{field}'" in combined_content or f'`{field}`' in combined_content or f"{field}:" in combined_content:
            results.append(CheckResult(
                check_id=check_id,
                category="API Contract",
                status=Status.PASS,
                message=f"Health response includes '{field}' field",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="API Contract",
                status=Status.WARN,
                message=f"Health response may be missing '{field}' field",
            ))

    return results
