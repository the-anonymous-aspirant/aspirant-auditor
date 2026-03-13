"""Load rules from YAML configuration."""

from pathlib import Path

import yaml


def load_rules(rules_path: Path) -> dict:
    """Load and return the rules dictionary from a YAML file."""
    with open(rules_path) as f:
        return yaml.safe_load(f)
