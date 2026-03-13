"""Tests for service type detection."""

from app.detector import detect_service_type


def test_detect_python(tmp_path):
    repo = tmp_path / "aspirant-test"
    repo.mkdir()
    (repo / "requirements.txt").write_text("fastapi\n")
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
