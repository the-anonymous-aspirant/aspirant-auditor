"""Check: Required files per service type."""

from app.checks.base import CheckResult, RepoContext, Status, check


def _is_stateless(ctx: RepoContext) -> bool:
    """Check if a Python service is stateless (no SQLAlchemy dependency)."""
    req_path = ctx.repo_path / "requirements.txt"
    if not req_path.exists():
        return True
    content = req_path.read_text().lower()
    return "sqlalchemy" not in content


@check(category="Required Files")
def check_required_files(ctx: RepoContext) -> list[CheckResult]:
    results = []
    required = ctx.rules.get("required_files", {}).get(ctx.service_type, {})

    db_files = {"database.py", "models.py"}
    stateless = ctx.service_type == "python" and _is_stateless(ctx)

    for directory, files in required.items():
        if directory == "root":
            base = ctx.repo_path
        elif directory == "app":
            base = ctx.repo_path / "app"
        elif directory == "tests":
            base = ctx.repo_path / "tests"
        elif directory == "docs":
            base = ctx.repo_path / "docs"
        else:
            base = ctx.repo_path / directory

        for filename in files:
            filepath = base / filename
            check_id = f"required_files.{directory}.{filename}"
            rel_path = str(filepath.relative_to(ctx.repo_path))

            if filepath.exists():
                results.append(CheckResult(
                    check_id=check_id,
                    category="Required Files",
                    status=Status.PASS,
                    message=f"{rel_path} exists",
                    path=rel_path,
                ))
            else:
                # WARN instead of FAIL for database files in stateless services
                if stateless and directory == "app" and filename in db_files:
                    results.append(CheckResult(
                        check_id=check_id,
                        category="Required Files",
                        status=Status.WARN,
                        message=f"{rel_path} missing (OK for stateless service)",
                        path=rel_path,
                    ))
                else:
                    results.append(CheckResult(
                        check_id=check_id,
                        category="Required Files",
                        status=Status.FAIL,
                        message=f"{rel_path} missing",
                        path=rel_path,
                    ))

    return results


@check(category="Required Files")
def check_dockerfile(ctx: RepoContext) -> list[CheckResult]:
    """Check Dockerfile exists. WARN if not named Dockerfile-{Name}."""
    if ctx.service_type == "deploy":
        return []

    results = []
    # Look for any Dockerfile
    dockerfiles = list(ctx.repo_path.glob("Dockerfile*"))
    # Also check inside app/ or service dirs
    dockerfiles.extend(ctx.repo_path.glob("*/Dockerfile*"))

    if not dockerfiles:
        results.append(CheckResult(
            check_id="required_files.dockerfile",
            category="Required Files",
            status=Status.FAIL,
            message="No Dockerfile found",
        ))
        return results

    # Check naming convention
    service_name = ctx.repo_name.replace("aspirant-", "").capitalize()
    expected_name = f"Dockerfile-{service_name}"
    has_correct_name = any(
        d.name == expected_name for d in dockerfiles
    )

    if has_correct_name:
        results.append(CheckResult(
            check_id="required_files.dockerfile_naming",
            category="Required Files",
            status=Status.PASS,
            message=f"Dockerfile follows naming convention ({expected_name})",
        ))
    else:
        actual_names = ", ".join(d.name for d in dockerfiles)
        results.append(CheckResult(
            check_id="required_files.dockerfile_naming",
            category="Required Files",
            status=Status.WARN,
            message=f"Dockerfile found ({actual_names}) but expected {expected_name}",
        ))

    return results
