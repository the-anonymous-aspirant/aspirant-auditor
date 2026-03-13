"""Check: Port/volume registry — conflict detection (deploy repos only)."""

import yaml

from app.checks.base import CheckResult, RepoContext, Status, check


def _load_compose(path) -> dict | None:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _parse_port_mapping(port_str: str) -> tuple[str | None, str | None]:
    """Parse a port mapping like '8081:8080' into (host, container)."""
    port_str = str(port_str)
    if ":" in port_str:
        parts = port_str.split(":")
        return parts[0], parts[-1]
    return None, port_str


@check(category="Port Registry", applies_to=["deploy"])
def check_port_conflicts(ctx: RepoContext) -> list[CheckResult]:
    """Check for duplicate host ports across services."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})
    host_ports: dict[str, list[str]] = {}  # port -> list of service names

    for svc_name, svc in services.items():
        for port_mapping in svc.get("ports", []):
            host_port, _ = _parse_port_mapping(str(port_mapping))
            if host_port:
                host_ports.setdefault(host_port, []).append(svc_name)

    for port, svc_names in host_ports.items():
        if len(svc_names) > 1:
            results.append(CheckResult(
                check_id=f"port_registry.conflict.{port}",
                category="Port Registry",
                status=Status.FAIL,
                message=f"Host port {port} used by multiple services: {', '.join(svc_names)}",
            ))

    if not any(r.status == Status.FAIL for r in results):
        results.append(CheckResult(
            check_id="port_registry.no_conflicts",
            category="Port Registry",
            status=Status.PASS,
            message="No host port conflicts detected",
        ))

    return results


@check(category="Port Registry", applies_to=["deploy"])
def check_port_registry_match(ctx: RepoContext) -> list[CheckResult]:
    """Check that ports match the registry in rules YAML."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    services = prod.get("services", {})
    registry = ctx.rules.get("port_registry", {})

    for svc_name, expected in registry.items():
        check_id = f"port_registry.match.{svc_name}"
        svc = services.get(svc_name, {})
        if not svc:
            continue

        expected_host = str(expected["host"])
        expected_container = str(expected["container"])

        actual_ports = svc.get("ports", [])
        matched = False
        for pm in actual_ports:
            host_port, container_port = _parse_port_mapping(str(pm))
            if host_port == expected_host and container_port == expected_container:
                matched = True
                break

        if matched:
            results.append(CheckResult(
                check_id=check_id,
                category="Port Registry",
                status=Status.PASS,
                message=f"Service '{svc_name}' port mapping matches registry ({expected_host}:{expected_container})",
            ))
        elif actual_ports:
            results.append(CheckResult(
                check_id=check_id,
                category="Port Registry",
                status=Status.WARN,
                message=f"Service '{svc_name}' port mapping doesn't match registry (expected {expected_host}:{expected_container})",
            ))

    return results


@check(category="Port Registry", applies_to=["deploy"])
def check_volume_conflicts(ctx: RepoContext) -> list[CheckResult]:
    """Check for volume name conflicts and naming pattern."""
    results = []
    prod_path = ctx.repo_path / "docker-compose.yml"
    prod = _load_compose(prod_path)
    if prod is None:
        return []

    volumes = prod.get("volumes", {})
    if not volumes:
        return []

    # Check naming pattern: {contenttype}data
    for vol_name in volumes:
        check_id = f"port_registry.volume_name.{vol_name}"
        if vol_name.endswith("data"):
            results.append(CheckResult(
                check_id=check_id,
                category="Port Registry",
                status=Status.PASS,
                message=f"Volume '{vol_name}' follows naming convention",
            ))
        else:
            results.append(CheckResult(
                check_id=check_id,
                category="Port Registry",
                status=Status.WARN,
                message=f"Volume '{vol_name}' doesn't follow {{contenttype}}data pattern",
            ))

    return results
