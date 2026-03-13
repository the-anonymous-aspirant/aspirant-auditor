# aspirant-auditor

Automated convention checker for aspirant-* repositories. Statically analyzes repos against the standards defined in [aspirant-meta](https://github.com/the-anonymous-aspirant/aspirant-meta) and reports pass/fail/warn per convention.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Scan a single repo
python -m app.main scan ~/git/aspirant-transcriber

# Scan all aspirant-* repos
python -m app.main scan-all ~/git/

# Validate aspirant-deploy specifically
python -m app.main scan-deploy ~/git/aspirant-deploy
```

## Docker

```bash
docker build -t aspirant-auditor .
docker run --rm -v ~/git:/repos aspirant-auditor scan-all /repos/
```

## Options

```
--format [terminal|json]   Output format (default: terminal)
--category <name>          Run only one check category
--verbose                  Show PASS results too (default: only FAIL/WARN)
--rules <path>             Custom rules YAML (default: bundled)
--no-color                 Disable colored output
```

Exit code: 0 = all pass, 1 = any failures.

## Check Categories

1. **Required Files** — Expected files per service type
2. **Docker Compose** — Compose validation (deploy repos)
3. **Port Registry** — Port/volume conflict detection (deploy repos)
4. **API Contract** — Health endpoint static analysis
5. **Code Structure** — Logging, database, model conventions
6. **Git Hygiene** — .env safety, .gitignore completeness
7. **Documentation** — Doc files, sections, changelog format
8. **Testing** — Test standards (no SQLite, fixtures, health tests)

## Documentation

See `docs/` for full documentation:
- [SPEC.md](docs/SPEC.md) — What we're building and why
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — How it fits together
- [OPERATIONS.md](docs/OPERATIONS.md) — How to run, test, debug
- [DECISIONS.md](docs/DECISIONS.md) — Key design choices
- [CHANGELOG.md](docs/CHANGELOG.md) — What changed and when
