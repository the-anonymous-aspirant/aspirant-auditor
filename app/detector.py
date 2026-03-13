"""Service type detection based on marker files."""

from pathlib import Path


def detect_service_type(repo_path: Path) -> str:
    """Detect the service type of a repository.

    Returns one of: "deploy", "go", "vue", "python", "unknown"
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

    # Python service: has requirements.txt
    if (repo_path / "requirements.txt").exists():
        return "python"

    return "unknown"
