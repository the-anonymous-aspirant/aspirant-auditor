"""Default paths and constants."""

from pathlib import Path

VERSION = "1.0.0"

# Default rules file (bundled with the project)
DEFAULT_RULES_PATH = Path(__file__).parent.parent / "rules" / "aspirant.yml"
