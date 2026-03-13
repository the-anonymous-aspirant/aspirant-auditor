"""Tests for Docker Compose checks."""

from app.checks.base import RepoContext, Status
from app.checks.docker_compose import (
    check_compose_services,
    check_compose_health_checks,
    check_compose_dev_postgres,
    check_compose_memory_limits,
    check_compose_depends_on,
    check_compose_image_naming,
)


def test_compose_services(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_services(ctx)
    # server, transcriber, client, postgres should pass
    passed = [r for r in results if r.status == Status.PASS]
    assert len(passed) >= 3


def test_postgres_healthcheck(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_health_checks(ctx)
    assert any(r.status == Status.PASS and "healthcheck" in r.message for r in results)


def test_dev_postgres_port(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_dev_postgres(ctx)
    port_results = [r for r in results if "port" in r.message.lower()]
    assert any(r.status == Status.PASS for r in port_results)


def test_memory_limits(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_memory_limits(ctx)
    # transcriber should have memory limit
    transcriber = [r for r in results if "transcriber" in r.message]
    assert any(r.status == Status.PASS for r in transcriber)


def test_depends_on(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_depends_on(ctx)
    server_results = [r for r in results if "server" in r.message]
    assert any(r.status == Status.PASS for r in server_results)


def test_image_naming(tmp_deploy_repo, rules):
    ctx = RepoContext(
        repo_path=tmp_deploy_repo,
        repo_name="aspirant-deploy",
        service_type="deploy",
        rules=rules,
    )
    results = check_compose_image_naming(ctx)
    passed = [r for r in results if r.status == Status.PASS]
    assert len(passed) >= 2
