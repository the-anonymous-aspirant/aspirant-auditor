# Import all check modules to trigger registration
from app.checks import (
    required_files,
    docker_compose,
    port_registry,
    api_contract,
    code_structure,
    git_hygiene,
    documentation,
    testing,
)
