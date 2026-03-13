## Changelog

### 2026-03-13
- Initial spec, architecture, decisions, and operations documents
- Implemented CLI with Click (scan, scan-all, scan-deploy commands)
- Implemented check framework with decorator-based registration
- Compiled aspirant-meta conventions into rules/aspirant.yml
- Implemented all 8 check categories: required files, docker compose, port registry, API contract, code structure, git hygiene, documentation, testing
- Added Rich terminal output and JSON output
- Added tests with temp directory fixtures
