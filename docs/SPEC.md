# aspirant-auditor Spec

## What

A Python CLI tool that statically analyzes aspirant-* repositories and reports compliance against the conventions defined in aspirant-meta (CONVENTIONS.md, DEVELOPMENT_PHILOSOPHY.md, INFRASTRUCTURE.md).

## Why

Checking convention compliance currently requires prompting an AI agent each time — expensive, inconsistent, and non-repeatable. An automated auditor gives consistent, repeatable results runnable locally or in CI.

## Scope

- Static file and directory analysis only (no running services)
- Scans individual repos or all aspirant-* repos under a directory
- Special handling for aspirant-deploy (docker-compose validation)
- 8 check categories covering files, code patterns, docs, docker, testing, git hygiene

## API Endpoints

N/A — this is a CLI tool, not a service.

## CLI Interface

```
aspirant-auditor scan <path>         Scan a single repo
aspirant-auditor scan-all <path>     Scan all aspirant-* repos under a directory
aspirant-auditor scan-deploy <path>  Validate aspirant-deploy specifically
```

Options: `--format`, `--category`, `--verbose`, `--rules`, `--no-color`

## Data Model

- `CheckResult` — Individual check outcome (check_id, category, status, message, path)
- `RepoContext` — Repo being scanned (path, name, service type, rules, all repos, deploy path)
- `Status` — PASS / FAIL / WARN / SKIP

## Constraints

- Python 3.11, Click, PyYAML, Rich
- No runtime dependencies on sibling repos (rules compiled into YAML)
- Exit code 0 = all pass, 1 = any failures

## Acceptance Criteria

- Scanning aspirant-transcriber produces accurate results matching known compliance
- Scanning aspirant-deploy validates compose files correctly
- `--format json` produces valid, parseable JSON
- Docker build and run work
- All tests pass
