"""Tests for service type detection."""

from app.detector import detect_service_type


def test_detect_python(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "requirements.txt").write_text("fastapi\n")
    assert detect_service_type(repo) == "python"


def test_detect_python_cli(tmp_path):
    """A Python repo with click and no web framework is a CLI, not a service."""
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "requirements.txt").write_text("click==8.1.7\npyyaml==6.0.2\n")
    assert detect_service_type(repo) == "python-cli"


def test_detect_python_web_with_click(tmp_path):
    """Click alongside a web framework still classifies as web python service."""
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "requirements.txt").write_text("fastapi\nclick\n")
    assert detect_service_type(repo) == "python"


def test_detect_go(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "go.mod").write_text("module aspirant-server\n")
    assert detect_service_type(repo) == "go"


def test_detect_vue(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "package.json").write_text('{"name": "client"}\n')
    assert detect_service_type(repo) == "vue"


def test_detect_deploy(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "docker-compose.yml").write_text("services:\n")
    assert detect_service_type(repo) == "deploy"


def test_detect_unknown(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    assert detect_service_type(repo) == "unknown"


def test_deploy_takes_priority(tmp_path):
    """Deploy detection takes priority over Python."""
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "docker-compose.yml").write_text("services:\n")
    (repo / "requirements.txt").write_text("fastapi\n")
    assert detect_service_type(repo) == "deploy"
