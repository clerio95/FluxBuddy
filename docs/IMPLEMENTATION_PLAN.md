# FluxBuddy Implementation Plan

## Goal

Translate the approved architecture into a minimal but production-usable MVP.

## Phase 1: Core Skeleton

Deliverables:

- `main.py`
- `core/bootstrap.py`
- `core/env.py`
- `core/logging.py`
- `core/contracts.py`
- `core/types.py`

Acceptance criteria:

- App starts with `.env`
- Startup and shutdown are logged
- Logger uses bounded file size
- Environment is validated centrally

## Phase 2: Routing and Permissions

Deliverables:

- `core/router.py`
- `core/permissions.py`
- `core/telemetry.py`

Acceptance criteria:

- Commands can be registered dynamically
- Duplicate commands are rejected cleanly
- Roles `viewer`, `operator`, `admin` are enforced
- Command latency and outcomes are logged

## Phase 3: Event Bus and Scheduler

Deliverables:

- `core/event_bus.py`
- `core/scheduler.py`

Acceptance criteria:

- Modules can publish and subscribe to internal events
- Listener failure is isolated
- Jobs can be declared by modules and executed safely

## Phase 4: Plugin System

Deliverables:

- `core/plugin_loader.py`
- `modules/status/plugin.json`
- `modules/status/module.py`

Acceptance criteria:

- Modules are discovered from the filesystem
- Invalid module manifests do not stop the app
- Status module is loaded dynamically

## Phase 5: Telegram Transport

Deliverables:

- `transports/base.py`
- `transports/telegram/adapter.py`
- `transports/telegram/formatter.py`

Acceptance criteria:

- Telegram updates reach the internal router
- Transport-specific details stay outside modules
- Command menu can be derived from module metadata

## Phase 6: Example Modules

Deliverables:

- `modules/occurrences`
- `modules/deadlines`

Acceptance criteria:

- Both modules use only core-managed dependencies
- Both modules demonstrate commands plus one additional integration style
- Neither module introduces business-specific names into the core

## Phase 7: Quality and OSS Readiness

Deliverables:

- `README.md`
- `CONTRIBUTING.md`
- `.env.example`
- CI workflow
- tests for core and plugin contract

Acceptance criteria:

- Lint passes
- Type checker passes
- Core tests pass
- Module contract is documented clearly for contributors

## Test Plan

Keep tests small.

Required first:

- plugin manifest validation
- duplicate command detection
- role authorization checks
- event listener isolation
- one integration smoke test for a module

## Open Implementation Decisions to Confirm Before Coding

1. Module manifest format: JSON is the default unless you want TOML.
2. Healthcheck command name: `/healthcheck` is the default unless you want `/health`.
3. Example module naming: `occurrences` and `deadlines` can stay as neutral examples, or be renamed to more generic labels.
