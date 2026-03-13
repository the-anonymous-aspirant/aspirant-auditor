"""Check: CI workflow — GitHub Actions build and push pipeline."""

import yaml
from pathlib import Path

from app.checks.base import CheckResult, RepoContext, Status, check


def _load_yaml(path: Path) -> dict | None:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _workflow_dir(ctx: RepoContext) -> Path:
    """Resolve the workflow directory from rules (supports both workflow_file and workflow_directory)."""
    ci_rules = ctx.rules.get("ci_workflow", {})
    if "workflow_file" in ci_rules:
        return ctx.repo_path / Path(ci_rules["workflow_file"]).parent
    return ctx.repo_path / ci_rules.get("workflow_directory", ".github/workflows")


def _find_workflow_files(ctx: RepoContext) -> list[Path]:
    """Return all .yml/.yaml workflow files in .github/workflows/."""
    wf_dir = _workflow_dir(ctx)
    if not wf_dir.is_dir():
        return []
    return sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))


def _has_docker_image_in_deploy(ctx: RepoContext) -> bool:
    """Check if the deploy repo's docker-compose.yml references a ghcr.io image for this service."""
    if ctx.deploy_path is None:
        return False

    compose_path = ctx.deploy_path / "docker-compose.yml"
    compose = _load_yaml(compose_path)
    if compose is None:
        return False

    prefix = ctx.rules.get("ci_workflow", {}).get(
        "image_prefix", "ghcr.io/the-anonymous-aspirant/aspirant-"
    )
    services = compose.get("services", {})

    # Match service name from repo name (aspirant-finance -> finance)
    short_name = ctx.repo_name.removeprefix("aspirant-")
    svc = services.get(short_name, {})
    image = svc.get("image", "")
    return image.startswith(prefix)


@check(category="CI Workflow", applies_to=["python", "go", "vue"])
def check_workflow_exists(ctx: RepoContext) -> list[CheckResult]:
    """Check that a CI workflow directory and at least one workflow file exist."""
    results = []
    wf_dir = _workflow_dir(ctx)

    if not wf_dir.is_dir():
        results.append(CheckResult(
            check_id="ci_workflow.directory_exists",
            category="CI Workflow",
            status=Status.FAIL,
            message=f"{wf_dir.relative_to(ctx.repo_path)} directory missing",
        ))
        return results

    results.append(CheckResult(
        check_id="ci_workflow.directory_exists",
        category="CI Workflow",
        status=Status.PASS,
        message=f"{wf_dir.relative_to(ctx.repo_path)} directory exists",
    ))

    workflows = _find_workflow_files(ctx)
    if not workflows:
        results.append(CheckResult(
            check_id="ci_workflow.has_workflow_file",
            category="CI Workflow",
            status=Status.FAIL,
            message="No workflow files (.yml/.yaml) found",
        ))
    else:
        names = ", ".join(w.name for w in workflows)
        results.append(CheckResult(
            check_id="ci_workflow.has_workflow_file",
            category="CI Workflow",
            status=Status.PASS,
            message=f"Found workflow(s): {names}",
        ))

    return results


@check(category="CI Workflow", applies_to=["python", "go", "vue"])
def check_docker_build_push(ctx: RepoContext) -> list[CheckResult]:
    """Check that a workflow builds and pushes a Docker image if deploy references one."""
    results = []

    if not _has_docker_image_in_deploy(ctx):
        results.append(CheckResult(
            check_id="ci_workflow.docker_build_push",
            category="CI Workflow",
            status=Status.SKIP,
            message="No ghcr.io image referenced in deploy compose — docker push not required",
        ))
        return results

    workflows = _find_workflow_files(ctx)
    if not workflows:
        results.append(CheckResult(
            check_id="ci_workflow.docker_build_push",
            category="CI Workflow",
            status=Status.FAIL,
            message="Deploy compose references a ghcr.io image but no CI workflow exists to build it",
        ))
        return results

    required_steps = ctx.rules.get("ci_workflow", {}).get("required_steps", [])
    found_steps = set()

    for wf_path in workflows:
        wf = _load_yaml(wf_path)
        if wf is None:
            continue

        # Walk all jobs and steps looking for the required actions
        for job_name, job in (wf.get("jobs") or {}).items():
            for step in (job.get("steps") or []):
                uses = step.get("uses", "")
                for required in required_steps:
                    if required in uses:
                        found_steps.add(required)

    missing = [s for s in required_steps if s not in found_steps]
    if missing:
        results.append(CheckResult(
            check_id="ci_workflow.docker_build_push",
            category="CI Workflow",
            status=Status.FAIL,
            message=f"Docker build/push workflow missing steps: {', '.join(missing)}",
        ))
    else:
        results.append(CheckResult(
            check_id="ci_workflow.docker_build_push",
            category="CI Workflow",
            status=Status.PASS,
            message="CI workflow builds and pushes Docker image to ghcr.io",
        ))

    return results


@check(category="CI Workflow", applies_to=["python", "go", "vue"])
def check_recommended_steps(ctx: RepoContext) -> list[CheckResult]:
    """Check for recommended CI steps: metadata-action (proper tagging) and buildx (caching)."""
    results = []
    workflows = _find_workflow_files(ctx)
    if not workflows:
        return []  # Already caught by check_workflow_exists

    recommended = ctx.rules.get("ci_workflow", {}).get("recommended_steps", [])
    if not recommended:
        return []

    found_steps = set()
    for wf_path in workflows:
        wf = _load_yaml(wf_path)
        if wf is None:
            continue
        for job_name, job in (wf.get("jobs") or {}).items():
            for step in (job.get("steps") or []):
                uses = step.get("uses", "")
                for rec in recommended:
                    if rec in uses:
                        found_steps.add(rec)

    missing = [s for s in recommended if s not in found_steps]
    if missing:
        results.append(CheckResult(
            check_id="ci_workflow.recommended_steps",
            category="CI Workflow",
            status=Status.WARN,
            message=f"Missing recommended CI steps: {', '.join(missing)} (see CONVENTIONS.md CI/CD)",
        ))
    else:
        results.append(CheckResult(
            check_id="ci_workflow.recommended_steps",
            category="CI Workflow",
            status=Status.PASS,
            message="All recommended CI steps present (buildx, metadata-action)",
        ))

    return results


@check(category="CI Workflow", applies_to=["python", "go", "vue"])
def check_main_push_trigger(ctx: RepoContext) -> list[CheckResult]:
    """Check that at least one workflow triggers on push to main."""
    results = []
    workflows = _find_workflow_files(ctx)
    if not workflows:
        return []  # Already caught by check_workflow_exists

    trigger_branch = ctx.rules.get("ci_workflow", {}).get(
        "push_trigger_branch", "main"
    )
    has_push_trigger = False

    for wf_path in workflows:
        wf = _load_yaml(wf_path)
        if wf is None:
            continue

        on_block = wf.get("on") or wf.get(True) or {}
        if isinstance(on_block, str):
            if on_block == "push":
                has_push_trigger = True
            continue

        push_config = on_block.get("push", {})
        if push_config is None:
            # on: push: (no filters) triggers on all branches
            has_push_trigger = True
            continue

        branches = push_config.get("branches", [])
        if trigger_branch in branches:
            has_push_trigger = True

    if has_push_trigger:
        results.append(CheckResult(
            check_id="ci_workflow.main_push_trigger",
            category="CI Workflow",
            status=Status.PASS,
            message=f"Workflow triggers on push to {trigger_branch}",
        ))
    else:
        results.append(CheckResult(
            check_id="ci_workflow.main_push_trigger",
            category="CI Workflow",
            status=Status.WARN,
            message=f"No workflow triggers on push to {trigger_branch} — images may not auto-deploy",
        ))

    return results
