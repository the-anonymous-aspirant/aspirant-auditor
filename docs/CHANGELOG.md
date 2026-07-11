## Changelog

### 2026-07-11
- Detect `python-cli` service type (Python + click, no web framework) and audit against a CLI-appropriate required-files template (no routes.py / schemas.py / test_health.py). Fixes self-audit CI red since 2026-03-13.

### 2026-03-13
- Initial spec, architecture, decisions, and operations documents
- Implemented CLI with Click (scan, scan-all, scan-deploy commands)
- Implemented check framework with decorator-based registration
- Compiled aspirant-meta conventions into rules/aspirant.yml
- Implemented all 8 check categories: required files, docker compose, port registry, API contract, code structure, git hygiene, documentation, testing
- Added Rich terminal output and JSON output
- Added tests with temp directory fixtures
