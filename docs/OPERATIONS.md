# Operations

## Setup

Prerequisites: Python 3.11+, pip

```bash
cd ~/git/aspirant-auditor
pip install -r requirements.txt
```

## How to Run

```bash
# Scan a single repo
python -m app.main scan ~/git/aspirant-transcriber

# Scan all aspirant-* repos
python -m app.main scan-all ~/git/

# Scan deploy repo specifically
python -m app.main scan-deploy ~/git/aspirant-deploy

# JSON output for CI
python -m app.main scan-all ~/git/ --format json

# Verbose (show PASS results)
python -m app.main scan ~/git/aspirant-transcriber --verbose
```

### Docker

```bash
docker build -t aspirant-auditor .
docker run --rm -v ~/git:/repos aspirant-auditor scan-all /repos/
```

## How to Test

```bash
pytest tests/ -v
```

## How to Validate

- Run against aspirant-transcriber — should produce accurate pass/fail results
- Run against aspirant-deploy — compose checks should catch real issues
- Run `--format json` and pipe through `python -m json.tool` to verify valid JSON
- Compare results against manual inspection of a known repo

## How to Debug

- Use `--verbose` to see all results including PASS
- Use `--category <name>` to isolate a single check category
- Check `rules/aspirant.yml` if a rule seems wrong — the YAML is the source of truth for checks
- Add `--no-color` if terminal output is garbled

## Gotchas

- The tool does static analysis only — it reads files, not running services
- Rules are compiled from aspirant-meta CONVENTIONS.md — if conventions change, update `rules/aspirant.yml`
- Service type detection relies on marker files (go.mod, package.json, etc.) — a repo without these markers won't match any type
- Docker compose checks only run against repos detected as type `deploy`
