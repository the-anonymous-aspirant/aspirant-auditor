"""Shared fixtures: temp dirs with mock repo structures."""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def rules():
    """Load the bundled rules."""
    rules_path = Path(__file__).parent.parent / "rules" / "aspirant.yml"
    with open(rules_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a minimal Python service repo structure."""
    repo = tmp_path / "aspirant-test"
    repo.mkdir()

    # Root files
    (repo / "README.md").write_text("# Test Service\n")
    (repo / ".gitignore").write_text(".env\n__pycache__/\nnode_modules/\n.DS_Store\n.vscode/\n.idea/\ndocker-compose.override.yml\n")
    (repo / "requirements.txt").write_text("fastapi==0.115.6\nuvicorn==0.34.0\nsqlalchemy==2.0.36\npydantic==2.10.0\npytest==8.3.4\nhttpx==0.28.1\n")
    (repo / "Dockerfile").write_text("FROM python:3.11-slim\n")

    # App directory
    app = repo / "app"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "main.py").write_text(
        'import logging\n'
        'logging.basicConfig(\n'
        '    level=logging.INFO,\n'
        '    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",\n'
        ')\n'
        'from fastapi import FastAPI\n'
        'app = FastAPI()\n'
    )
    (app / "config.py").write_text("import os\n")
    (app / "database.py").write_text(
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import sessionmaker, declarative_base\n"
        "engine = create_engine('postgresql://...')\n"
        "SessionLocal = sessionmaker(bind=engine)\n"
        "Base = declarative_base()\n"
        "def get_db(): pass\n"
    )
    (app / "models.py").write_text(
        "from sqlalchemy import Column\n"
        "from sqlalchemy.dialects.postgresql import UUID\n"
        "import uuid\n"
        "class Item:\n"
        "    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)\n"
        "    created_at = Column()\n"
        "    updated_at = Column()\n"
    )
    (app / "schemas.py").write_text("from pydantic import BaseModel\n")
    (app / "routes.py").write_text(
        '@app.get("/health")\n'
        'def health():\n'
        '    return {"status": "ok", "service": "test", "version": "1.0.0", "checks": {}}\n'
    )

    # Tests directory
    tests = repo / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "conftest.py").write_text(
        "import pytest\n"
        "def db(): pass\n"
        "def client(): pass\n"
    )
    (tests / "test_health.py").write_text(
        "def test_health(client):\n"
        '    assert "status" in data\n'
        '    assert "service" in data\n'
        '    assert "checks" in data\n'
    )

    # Docs directory
    docs = repo / "docs"
    docs.mkdir()
    (docs / "SPEC.md").write_text(
        "# Spec\n## API Endpoints\n## Data Model\n## Constraints\n## Acceptance Criteria\n"
    )
    (docs / "ARCHITECTURE.md").write_text(
        "# Architecture\n```\n┌──────┐\n│ Test │\n└──────┘\n```\n"
    )
    (docs / "CHANGELOG.md").write_text("## Changelog\n\n### 2026-03-13\n- Initial\n")
    (docs / "DECISIONS.md").write_text("# Decisions\n")
    (docs / "OPERATIONS.md").write_text(
        "# Operations\n## Setup\n## How to Run\n## How to Test\n## How to Validate\n## How to Debug\n## Gotchas\n"
    )

    return repo


@pytest.fixture
def tmp_deploy_repo(tmp_path):
    """Create a minimal deploy repo structure."""
    repo = tmp_path / "aspirant-deploy"
    repo.mkdir()

    (repo / "README.md").write_text("# Deploy\n")
    (repo / ".gitignore").write_text(".env\n__pycache__/\nnode_modules/\n.DS_Store\n.vscode/\n.idea/\ndocker-compose.override.yml\n")

    # Prod compose
    prod_compose = {
        "services": {
            "postgres": {
                "image": "postgres:16-alpine",
                "ports": ["5432:5432"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready"],
                    "interval": "5s",
                },
                "volumes": ["pgdata:/var/lib/postgresql/data"],
            },
            "server": {
                "image": "ghcr.io/the-anonymous-aspirant/aspirant-server:latest",
                "ports": ["8081:8080"],
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                },
            },
            "transcriber": {
                "image": "ghcr.io/the-anonymous-aspirant/aspirant-transcriber:latest",
                "ports": ["8082:8000"],
                "mem_limit": "2g",
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                },
            },
            "client": {
                "image": "ghcr.io/the-anonymous-aspirant/aspirant-client:latest",
                "ports": ["80:80"],
            },
        },
        "volumes": {
            "pgdata": None,
            "filedata": None,
            "audiodata": None,
        },
    }

    # Dev compose
    dev_compose = {
        "services": {
            "postgres": {
                "image": "postgres:16-alpine",
                "ports": ["5433:5432"],
                "healthcheck": {
                    "test": ["CMD-SHELL", "pg_isready"],
                },
                "volumes": ["pgdata-dev:/var/lib/postgresql/data"],
            },
            "server": {
                "environment": {"DB_HOST": "postgres"},
                "depends_on": {
                    "postgres": {"condition": "service_healthy"},
                },
            },
        },
        "volumes": {
            "pgdata-dev": None,
        },
    }

    with open(repo / "docker-compose.yml", "w") as f:
        yaml.dump(prod_compose, f)
    with open(repo / "docker-compose.dev.yml", "w") as f:
        yaml.dump(dev_compose, f)

    # Docs
    docs = repo / "docs"
    docs.mkdir()
    (docs / "SPEC.md").write_text("# Spec\n## API Endpoints\n## Data Model\n## Constraints\n## Acceptance Criteria\n")
    (docs / "ARCHITECTURE.md").write_text("# Architecture\n```\n┌──────┐\n│ Test │\n└──────┘\n```\n")
    (docs / "CHANGELOG.md").write_text("## Changelog\n\n### 2026-03-13\n- Initial\n")
    (docs / "DECISIONS.md").write_text("# Decisions\n")
    (docs / "OPERATIONS.md").write_text("# Operations\n## Setup\n## How to Run\n## How to Test\n## How to Validate\n## How to Debug\n## Gotchas\n")

    return repo
