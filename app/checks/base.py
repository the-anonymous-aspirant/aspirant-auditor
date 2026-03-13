"""Check framework: data types, decorator, and global registry."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, NamedTuple


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    SKIP = "SKIP"


class CheckResult(NamedTuple):
    check_id: str
    category: str
    status: Status
    message: str
    path: str | None = None


@dataclass
class RepoContext:
    repo_path: Path
    repo_name: str
    service_type: str  # "python", "go", "vue", "deploy"
    rules: dict
    all_repos: list[Path] = field(default_factory=list)
    deploy_path: Path | None = None


# Global check registry: list of (function, category, applies_to)
_registry: list[tuple[Callable, str, list[str]]] = []


def check(category: str, applies_to: list[str] | None = None):
    """Decorator to register a check function.

    Args:
        category: Display category name (e.g., "Required Files")
        applies_to: List of service types this check applies to.
                    None means all types.
    """
    def decorator(fn: Callable):
        _registry.append((fn, category, applies_to or []))
        return fn
    return decorator


def get_checks() -> list[tuple[Callable, str, list[str]]]:
    """Return all registered checks."""
    return list(_registry)
