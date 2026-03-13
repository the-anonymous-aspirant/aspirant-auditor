"""Tests for required files checks."""

from app.checks.base import RepoContext, Status
from app.checks.required_files import check_required_files, check_dockerfile


def test_all_files_present(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_required_files(ctx)
    failed = [r for r in results if r.status == Status.FAIL]
    assert len(failed) == 0, f"Unexpected failures: {[r.message for r in failed]}"


def test_missing_docs(tmp_repo, rules):
    import shutil
    shutil.rmtree(tmp_repo / "docs")

    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_required_files(ctx)
    failed = [r for r in results if r.status == Status.FAIL]
    # Should fail for all docs files
    doc_failures = [r for r in failed if "docs/" in r.message]
    assert len(doc_failures) >= 5


def test_stateless_service_warns_for_db(tmp_path, rules):
    """Stateless services (no sqlalchemy) get WARN not FAIL for database files."""
    repo = tmp_path / "aspirant-translator"
    repo.mkdir()
    (repo / "README.md").write_text("# Translator\n")
    (repo / ".gitignore").write_text(".env\n")
    (repo / "requirements.txt").write_text("fastapi\nargostranslate\n")

    app = repo / "app"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "main.py").write_text("")
    (app / "config.py").write_text("")
    (app / "schemas.py").write_text("")
    (app / "routes.py").write_text("")

    tests = repo / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "conftest.py").write_text("")
    (tests / "test_health.py").write_text("")

    docs = repo / "docs"
    docs.mkdir()
    for f in ["SPEC.md", "ARCHITECTURE.md", "CHANGELOG.md", "DECISIONS.md", "OPERATIONS.md"]:
        (docs / f).write_text("")

    ctx = RepoContext(
        repo_path=repo,
        repo_name="aspirant-translator",
        service_type="python",
        rules=rules,
    )
    results = check_required_files(ctx)

    # database.py and models.py should be WARN not FAIL
    db_results = [r for r in results if "database.py" in r.message or "models.py" in r.message]
    for r in db_results:
        assert r.status == Status.WARN, f"Expected WARN for {r.message}, got {r.status}"


def test_dockerfile_check(tmp_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_repo,
        repo_name="aspirant-test",
        service_type="python",
        rules=rules,
    )
    results = check_dockerfile(ctx)
    # Has Dockerfile but not Dockerfile-Test
    warn_results = [r for r in results if r.status == Status.WARN]
    assert len(warn_results) >= 1
