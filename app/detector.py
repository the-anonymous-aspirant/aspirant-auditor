"""Service type detection based on marker files."""

from pathlib import Path


_PYTHON_WEB_FRAMEWORKS = (
    "fastapi",
    "flask",
    "django",
    "starlette",
    "sanic",
    "bottle",
    "tornado",
)


def detect_service_type(repo_path: Path) -> str:
    """Detect the service type of a repository.

    Returns one of: "deploy", "go", "vue", "python", "python-cli", "unknown"
    """
    # Deploy repo: has docker-compose.yml at root
    if (repo_path / "docker-compose.yml").exists():
        return "deploy"

    # Go service: has go.mod
    if (repo_path / "go.mod").exists():
        return "go"

    # Vue/Node frontend: has package.json
    if (repo_path / "package.json").exists():
        return "vue"

    # Python: has requirements.txt. Split into web-service ("python") and
    # CLI-only ("python-cli") — CLI tools should not be held to the
    # routes.py/schemas.py/test_health.py contract.
    req_path = repo_path / "requirements.txt"
    if req_path.exists():
        req = req_path.read_text().lower()
        if "click" in req and not any(fw in req for fw in _PYTHON_WEB_FRAMEWORKS):
            return "python-cli"
        return "python"

    return "unknown"
