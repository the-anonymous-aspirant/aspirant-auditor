"""Check: Code structure — logging, database, model conventions (Python)."""

import re

from app.checks.base import CheckResult, RepoContext, Status, check


@check(category="Code Structure", applies_to=["python"])
def check_logging_format(ctx: RepoContext) -> list[CheckResult]:
    """Check that main.py uses the standard logging format."""
    results = []
    main_py = ctx.repo_path / "app" / "main.py"

    if not main_py.exists():
        return []

    content = main_py.read_text()
    expected = ctx.rules.get("code_patterns", {}).get("python", {}).get(
        "logging_format", ""
    )

    if expected and expected in content:
        results.append(CheckResult(
            check_id="code_structure.logging_format",
            category="Code Structure",
            status=Status.PASS,
            message="Logging format matches convention",
        ))
    elif "logging.basicConfig" in content:
        results.append(CheckResult(
            check_id="code_structure.logging_format",
            category="Code Structure",
            status=Status.WARN,
            message="Logging configured but format doesn't match convention",
        ))
    else:
        results.append(CheckResult(
            check_id="code_structure.logging_format",
            category="Code Structure",
            status=Status.WARN,
            message="No logging.basicConfig found in main.py",
        ))

    return results


@check(category="Code Structure", applies_to=["python"])
def check_database_exports(ctx: RepoContext) -> list[CheckResult]:
    """Check that database.py exports expected symbols."""
    results = []
    db_py = ctx.repo_path / "app" / "database.py"

    if not db_py.exists():
        # Skip for stateless services
        req_path = ctx.repo_path / "requirements.txt"
        if req_path.exists() and "sqlalchemy" in req_path.read_text().lower():
            results.append(CheckResult(
                check_id="code_structure.database_exports",
                category="Code Structure",
                status=Status.FAIL,
                message="database.py missing but SQLAlchemy is a dependency",
            ))
        return results

    content = db_py.read_text()
    expected_exports = ctx.rules.get("code_patterns", {}).get("python", {}).get(
        "database_exports", []
    )

    for export in expected_exports:
        check_id = f"code_structure.db_export.{export}"
        if re.search(rf"\b{export}\b", content):
            results.append(CheckResult(
                check_id=check_id,
                category="Code Structure",
                status=Status.PASS,
                message=f"database.py defines {export}",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Code Structure",
                status=Status.FAIL,
                message=f"database.py missing expected export: {export}",
            ))

    return results


@check(category="Code Structure", applies_to=["python"])
def check_model_conventions(ctx: RepoContext) -> list[CheckResult]:
    """Check models have timestamps and UUID PKs."""
    results = []
    models_py = ctx.repo_path / "app" / "models.py"

    if not models_py.exists():
        return []

    content = models_py.read_text()

    # Check for timestamp columns
    timestamps = ctx.rules.get("code_patterns", {}).get("python", {}).get(
        "model_timestamps", []
    )
    for ts in timestamps:
        check_id = f"code_structure.model_timestamp.{ts}"
        if ts in content:
            results.append(CheckResult(
                check_id=check_id,
                category="Code Structure",
                status=Status.PASS,
                message=f"Models define {ts} column",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Code Structure",
                status=Status.WARN,
                message=f"Models missing {ts} column",
            ))

    # Check for UUID primary keys
    if "UUID" in content or "uuid" in content:
        results.append(CheckResult(
            check_id="code_structure.model_uuid_pk",
            category="Code Structure",
            status=Status.PASS,
            message="Models use UUID primary keys",
        ))
    else:
        results.append(CheckResult(
            check_id="code_structure.model_uuid_pk",
            category="Code Structure",
            status=Status.WARN,
            message="Models may not use UUID primary keys",
        ))

    return results
