# Decisions

## 2026-03-13

### Functions with decorator over class hierarchy
Check functions are stateless — they take a context and return results. No need for inheritance, lifecycle hooks, or shared state. A `@check` decorator + global registry is simpler than a base class with overrides.

### YAML rules over live reading from aspirant-meta
Rules are compiled into `rules/aspirant.yml` rather than reading from the sibling aspirant-meta repo at runtime. This removes a runtime dependency, works in Docker without mounting sibling repos, and makes the tool self-contained.

### Rich terminal + JSON output
Terminal output uses Rich for colored, human-friendly display. JSON output is available for CI integration. No HTML or other formats — these two cover all use cases.

### No FastAPI endpoint
The auditor is a CLI tool. Adding a web server would add complexity without value — the JSON output is sufficient for any integration needs.

### WARN not FAIL for Dockerfile naming
All current aspirant repos use `Dockerfile` instead of the convention `Dockerfile-{Name}`. Failing would produce noise without value until repos are updated. WARN flags the deviation without breaking CI.

### WARN not FAIL for database files in stateless services
Services like translator, monitor, and remarkable have no database. Requiring database.py/models.py would be incorrect. Detection is based on absence of `sqlalchemy` in requirements.txt.
