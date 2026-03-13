"""Check: Testing standards — no SQLite, fixtures, health tests."""

import re

from app.checks.base import CheckResult, RepoContext, Status, check


@check(category="Testing", applies_to=["python"])
def check_no_sqlite(ctx: RepoContext) -> list[CheckResult]:
    """Check that no test file references SQLite."""
    results = []
    tests_dir = ctx.repo_path / "tests"

    if not tests_dir.exists():
        return []

    forbidden = ctx.rules.get("testing", {}).get("forbidden_patterns", [])

    for test_file in tests_dir.glob("*.py"):
        content = test_file.read_text()
        for fp in forbidden:
            pattern = fp["pattern"]
            message = fp["message"]
            if re.search(pattern, content, re.IGNORECASE):
                results.append(CheckResult(
                    check_id=f"testing.forbidden.{pattern}",
                    category="Testing",
                    status=Status.FAIL,
                    message=f"{test_file.name}: {message}",
                    path=str(test_file.relative_to(ctx.repo_path)),
                ))

    if not any(r.status == Status.FAIL for r in results):
        results.append(CheckResult(
            check_id="testing.no_sqlite",
            category="Testing",
            status=Status.PASS,
            message="No forbidden test patterns found",
        ))

    return results


def _is_stateless(ctx: RepoContext) -> bool:
    """Check if a Python service is stateless (no SQLAlchemy dependency)."""
    req_path = ctx.repo_path / "requirements.txt"
    if not req_path.exists():
        return True
    content = req_path.read_text().lower()
    return "sqlalchemy" not in content


@check(category="Testing", applies_to=["python"])
def check_conftest_fixtures(ctx: RepoContext) -> list[CheckResult]:
    """Check conftest.py has required fixture definitions."""
    results = []
    conftest = ctx.repo_path / "tests" / "conftest.py"

    if not conftest.exists():
        return []  # Already caught by required_files

    content = conftest.read_text()
    required_fixtures = ctx.rules.get("testing", {}).get(
        "conftest_required_fixtures", []
    )
    stateless = _is_stateless(ctx)

    for fixture in required_fixtures:
        check_id = f"testing.conftest_fixture.{fixture}"
        # Look for def fixture_name or @pytest.fixture ... def fixture_name
        if re.search(rf"def\s+{fixture}\s*\(", content):
            results.append(CheckResult(
                check_id=check_id,
                category="Testing",
                status=Status.PASS,
                message=f"conftest.py defines '{fixture}' fixture",
            ))
        elif stateless and fixture == "db":
            results.append(CheckResult(
                check_id=check_id,
                category="Testing",
                status=Status.SKIP,
                message=f"conftest.py missing '{fixture}' fixture (OK for stateless service)",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Testing",
                status=Status.FAIL,
                message=f"conftest.py missing '{fixture}' fixture",
            ))

    return results


@check(category="Testing", applies_to=["python"])
def check_health_tests(ctx: RepoContext) -> list[CheckResult]:
    """Check test_health.py asserts on required fields."""
    results = []
    test_health = ctx.repo_path / "tests" / "test_health.py"

    if not test_health.exists():
        return []  # Already caught by required_files

    content = test_health.read_text()
    expected_fields = ["status", "service", "checks"]

    for field in expected_fields:
        check_id = f"testing.health_test.{field}"
        if f'"{field}"' in content or f"'{field}'" in content:
            results.append(CheckResult(
                check_id=check_id,
                category="Testing",
                status=Status.PASS,
                message=f"test_health.py checks '{field}' field",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Testing",
                status=Status.WARN,
                message=f"test_health.py may not check '{field}' field",
            ))

    return results
