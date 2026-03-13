# aspirant-auditor Architecture

## System Overview

```
┌──────────────────────────────────────────────────────┐
│                   CLI (Click)                         │
│                   app/main.py                         │
│                                                      │
│  scan <path>  │  scan-all <path>  │  scan-deploy     │
└───────┬───────┴────────┬──────────┴────────┬─────────┘
        │                │                   │
        ▼                ▼                   ▼
┌──────────────────────────────────────────────────────┐
│                   Scanner                             │
│                   app/scanner.py                      │
│                                                      │
│  1. Discover repos (glob aspirant-*)                 │
│  2. Detect service type (detector.py)                │
│  3. Load rules (loader.py → rules/aspirant.yml)      │
│  4. Build RepoContext                                 │
│  5. Run matching checks from registry                │
│  6. Collect CheckResults                              │
└───────────────────────┬──────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Check Module │ │ Check Module │ │ Check Module │
│ @check(...)  │ │ @check(...)  │ │ @check(...)  │
│              │ │              │ │              │
│ Returns      │ │ Returns      │ │ Returns      │
│ [CheckResult]│ │ [CheckResult]│ │ [CheckResult]│
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
┌──────────────────────────────────────────────────────┐
│                   Reporter                            │
│                   app/reporter.py                     │
│                                                      │
│  Terminal (Rich)  │  JSON                             │
└──────────────────────────────────────────────────────┘
```

## Components

| Component | File | Purpose |
|-----------|------|---------|
| CLI | `app/main.py` | Click commands, option parsing |
| Scanner | `app/scanner.py` | Orchestration: discover, detect, run checks |
| Detector | `app/detector.py` | Service type detection (python/go/vue/deploy) |
| Loader | `app/loader.py` | Load and parse rules YAML |
| Config | `app/config.py` | Default paths, constants |
| Reporter | `app/reporter.py` | Terminal (Rich) and JSON output |
| Base | `app/checks/base.py` | Data types, @check decorator, registry |
| Check modules | `app/checks/*.py` | Individual check implementations |
| Rules | `rules/aspirant.yml` | Compiled convention ruleset |

## Check Registration

Functions decorated with `@check(category, applies_to)` are auto-registered in a global registry. The scanner filters by service type at runtime.

## Data Flow

1. CLI parses args → Scanner receives repo path(s)
2. Scanner detects service type per repo
3. Scanner loads rules YAML once
4. Scanner builds RepoContext per repo
5. Scanner iterates registered checks, skipping non-applicable ones
6. Each check returns `list[CheckResult]`
7. Reporter formats results for terminal or JSON
