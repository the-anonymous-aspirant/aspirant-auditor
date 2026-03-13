"""Check: Docker Compose validation (deploy repos only)."""

import yaml

from app.checks.base import CheckResult, RepoContext, Status, check


def _load_compose(path) -> dict | None:
    """Load a docker-compose YAML file, return None on error."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_services(ctx: RepoContext) -> list[CheckResult]:
    """Check that expected services are defined in both compose files."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    dev_path = ctx.repo_path / "docker-compose.dev.yml"

    prod = _load_compose(prod_path)
    dev = _load_compose(dev_path)

    if prod is None:
        results.append(CheckResult(
            check_id="docker_compose.prod_parseable",
            category="Docker Compose",
            status=Status.FAIL,
            message="docker-compose.yml could not be parsed",
        ))
        return results

    if dev is None:
        results.append(CheckResult(
            check_id="docker_compose.dev_parseable",
            category="Docker Compose",
            status=Status.FAIL,
            message="docker-compose.dev.yml could not be parsed",
        ))
        return results

    prod_services = set(prod.get("services", {}).keys())
    dev_services = set(dev.get("services", {}).keys())

    # Check expected services from port registry exist in prod
    port_registry = ctx.rules.get("port_registry", {})
    for service_name in port_registry:
        check_id = f"docker_compose.service_defined.{service_name}"
        if service_name in prod_services:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.PASS,
                message=f"Service '{service_name}' defined in prod compose",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.WARN,
                message=f"Service '{service_name}' not found in prod compose",
            ))

    return results


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_health_checks(ctx: RepoContext) -> list[CheckResult]:
    """Check postgres has healthcheck defined."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})
    postgres = services.get("postgres", {})

    if "healthcheck" in postgres:
        results.append(CheckResult(
            check_id="docker_compose.postgres_healthcheck",
            category="Docker Compose",
            status=Status.PASS,
            message="PostgreSQL has healthcheck configured",
        ))
    else:
        results.append(CheckResult(
            check_id="docker_compose.postgres_healthcheck",
            category="Docker Compose",
            status=Status.FAIL,
            message="PostgreSQL missing healthcheck",
        ))

    return results


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_dev_postgres(ctx: RepoContext) -> list[CheckResult]:
    """Check dev compose: postgres port 5433, pgdata-dev volume, DB_HOST override."""
    results = []
    dev_path = ctx.repo_path / "docker-compose.dev.yml"
    dev = _load_compose(dev_path)
    if dev is None:
        return []

    services = dev.get("services", {})
    postgres = services.get("postgres", {})

    # Check port mapping
    ports = postgres.get("ports", [])
    port_str = str(ports)
    expected_port = ctx.rules.get("docker_compose", {}).get("dev", {}).get(
        "postgres_host_port", "5433"
    )
    if expected_port in port_str:
        results.append(CheckResult(
            check_id="docker_compose.dev_postgres_port",
            category="Docker Compose",
            status=Status.PASS,
            message=f"Dev postgres uses host port {expected_port}",
        ))
    else:
        results.append(CheckResult(
            check_id="docker_compose.dev_postgres_port",
            category="Docker Compose",
            status=Status.FAIL,
            message=f"Dev postgres should use host port {expected_port} to avoid conflicts",
        ))

    # Check volume name
    volumes = dev.get("volumes", {})
    expected_vol = ctx.rules.get("docker_compose", {}).get("dev", {}).get(
        "volume_name", "pgdata-dev"
    )
    if expected_vol in volumes:
        results.append(CheckResult(
            check_id="docker_compose.dev_volume_name",
            category="Docker Compose",
            status=Status.PASS,
            message=f"Dev compose uses '{expected_vol}' volume",
        ))
    else:
        results.append(CheckResult(
            check_id="docker_compose.dev_volume_name",
            category="Docker Compose",
            status=Status.WARN,
            message=f"Dev compose should use '{expected_vol}' volume to avoid conflicts",
        ))

    # Check DB_HOST override on services
    expected_host = ctx.rules.get("docker_compose", {}).get("dev", {}).get(
        "db_host_override", "postgres"
    )
    for svc_name, svc in services.items():
        if svc_name == "postgres":
            continue
        env = svc.get("environment", {})
        if isinstance(env, dict) and env.get("DB_HOST") == expected_host:
            results.append(CheckResult(
                check_id=f"docker_compose.dev_db_host.{svc_name}",
                category="Docker Compose",
                status=Status.PASS,
                message=f"Service '{svc_name}' overrides DB_HOST to '{expected_host}'",
            ))
        elif isinstance(env, list):
            if any(f"DB_HOST={expected_host}" in e for e in env):
                results.append(CheckResult(
                    check_id=f"docker_compose.dev_db_host.{svc_name}",
                    category="Docker Compose",
                    status=Status.PASS,
                    message=f"Service '{svc_name}' overrides DB_HOST to '{expected_host}'",
                ))

    return results


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_memory_limits(ctx: RepoContext) -> list[CheckResult]:
    """Check memory limits on heavy services."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})
    limited_services = ctx.rules.get("docker_compose", {}).get(
        "memory_limited_services", []
    )
    expected_limit = ctx.rules.get("docker_compose", {}).get("memory_limit", "2g")

    for svc_name in limited_services:
        check_id = f"docker_compose.memory_limit.{svc_name}"
        svc = services.get(svc_name, {})
        if not svc:
            continue

        mem_limit = svc.get("mem_limit") or svc.get("deploy", {}).get(
            "resources", {}
        ).get("limits", {}).get("memory")

        if mem_limit:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.PASS,
                message=f"Service '{svc_name}' has memory limit: {mem_limit}",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.WARN,
                message=f"Service '{svc_name}' should have mem_limit: {expected_limit}",
            ))

    return results


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_image_naming(ctx: RepoContext) -> list[CheckResult]:
    """Check prod image naming follows convention."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})
    prefix = ctx.rules.get("docker_compose", {}).get(
        "image_prefix", "ghcr.io/the-anonymous-aspirant/aspirant-"
    )

    for svc_name, svc in services.items():
        image = svc.get("image", "")
        if not image:
            continue  # Uses build context, not a pre-built image

        check_id = f"docker_compose.image_naming.{svc_name}"
        if image.startswith(prefix) or svc_name == "postgres" or svc_name == "kiwix":
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.PASS,
                message=f"Service '{svc_name}' image follows naming convention",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.WARN,
                message=f"Service '{svc_name}' image '{image}' doesn't match prefix '{prefix}'",
            ))

    return results


@check(category="Docker Compose", applies_to=["deploy"])
def check_compose_depends_on(ctx: RepoContext) -> list[CheckResult]:
    """Check depends_on with service_healthy for DB-dependent services."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})

    # Services known to depend on postgres
    db_dependent = ["server", "transcriber", "commander", "finance"]

    for svc_name in db_dependent:
        check_id = f"docker_compose.depends_on.{svc_name}"
        svc = services.get(svc_name, {})
        if not svc:
            continue

        depends = svc.get("depends_on", {})
        if isinstance(depends, dict) and "postgres" in depends:
            condition = depends["postgres"].get("condition", "")
            if condition == "service_healthy":
                results.append(CheckResult(
                    check_id=check_id,
                    category="Docker Compose",
                    status=Status.PASS,
                    message=f"Service '{svc_name}' depends on postgres with service_healthy",
                ))
            else:
                results.append(CheckResult(
                    check_id=check_id,
                    category="Docker Compose",
                    status=Status.WARN,
                    message=f"Service '{svc_name}' depends on postgres but without service_healthy condition",
                ))
        elif isinstance(depends, list) and "postgres" in depends:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.WARN,
                message=f"Service '{svc_name}' depends on postgres but should use service_healthy condition",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Docker Compose",
                status=Status.FAIL,
                message=f"Service '{svc_name}' should depend on postgres",
            ))

    return results
