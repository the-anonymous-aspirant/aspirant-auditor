"""Tests for documentation checks."""

from app.checks.base import RepoContext, Status
from app.checks.documentation import (
    check_changelog_format,
    check_spec_sections,
    check_architecture_diagrams,
    check_operations_sections,
)


def test_changelog_format(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_changelog_format(ctx)
    assert any(r.status == Status.PASS for r in results)


def test_changelog_no_docs(tmp_path, rules):
    repo = tmp_path / "aspirant-empty"
    repo.mkdir()

    ctx = RepoContext(
        repo_path=repo,
        repo_name="aspirant-empty",
        service_type="python",
        rules=rules,
    )
    results = check_changelog_format(ctx)
    assert any(r.status == Status.SKIP for r in results)


def test_spec_sections(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_spec_sections(ctx)
    passed = [r for r in results if r.status == Status.PASS]
    assert len(passed) == 4  # API Endpoints, Data Model, Constraints, Acceptance Criteria


def test_architecture_diagrams(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_architecture_diagrams(ctx)
    assert any(r.status == Status.PASS for r in results)


def test_operations_sections(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_operations_sections(ctx)
    passed = [r for r in results if r.status == Status.PASS]
    assert len(passed) == 6  # Setup, How to Run, How to Test, How to Validate, How to Debug, Gotchas
