# FluxBuddy Architecture

## Purpose

FluxBuddy is an open source workflow bot core focused on clean routing, modular integrations, and safe growth over time.

The MVP must provide:

- Telegram as the first transport
- A transport-agnostic internal router
- A lightweight internal event bus
- Dynamic module loading through plugins and config
- Safe scheduled jobs
- Centralized authorization, logging, configuration, and dependency wiring
- Neutral domain language with no fuel station assumptions in the core

This document is the validation baseline before implementation.

## Product Boundaries

FluxBuddy is not a business solution by itself.

FluxBuddy is:

- A bot runtime
- A routing core
- A module host
- An event-driven workflow shell

FluxBuddy is not:

- A fuel station bot
- A Telnet integration project
- A hardcoded command collection
- A place for module-specific dependencies to leak into the core

## Design Goals

1. Keep the core stable and small.
2. Make feature modules isolated and replaceable.
3. Allow synchronous commands, scheduled jobs, and internal events.
4. Prevent a module failure from crashing the bot.
5. Keep configuration portable, local-first, and predictable.
6. Make future transports possible without rewriting business modules.

## Non-Goals for MVP

- No external database requirement
- No Docker requirement
- No Slack runtime in v1, only channel-ready abstractions
- No strict type system bureaucracy beyond practical checks
- No business-specific integrations in the core

## Runtime Model

The runtime is organized in six layers.

1. Transport layer
   Telegram adapter receives updates and converts them into internal requests/events.

2. Routing layer
   The router resolves commands and dispatches them to the owning module.

3. Event bus layer
   Modules publish and subscribe to internal events without importing each other.

4. Scheduling layer
   Jobs are registered by modules but executed by the core with error isolation.

5. Security and policy layer
   Authorization, role checks, healthcheck access, and audit logging are enforced centrally.

6. Module layer
   Modules expose manifest metadata, command handlers, event listeners, and optional scheduled jobs.

## Proposed Project Structure

```text
FluxBuddy/
├── main.py
├── prompt.md
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .env.example
├── requirements.txt
├── setup.bat
├── run.bat
├── run_forever.bat
├── docs/
│   ├── ARCHITECTURE.md
│   └── ARCHITECTURE.pt-BR.md
├── core/
│   ├── app.py
│   ├── bootstrap.py
│   ├── contracts.py
│   ├── dependency_registry.py
│   ├── env.py
│   ├── event_bus.py
│   ├── exceptions.py
│   ├── logging.py
│   ├── permissions.py
│   ├── plugin_loader.py
│   ├── router.py
│   ├── scheduler.py
│   ├── telemetry.py
│   └── types.py
├── transports/
│   ├── base.py
│   └── telegram/
│       ├── adapter.py
│       ├── handlers.py
│       └── formatter.py
├── modules/
│   ├── status/
│   │   ├── module.py
│   │   └── plugin.json
│   ├── occurrences/
│   │   ├── module.py
│   │   └── plugin.json
│   └── deadlines/
│       ├── module.py
│       └── plugin.json
├── shared/
│   ├── models.py
│   └── text.py
├── data/
└── logs/
```

## Core Responsibilities

### main.py

- Entry point only
- Applies Windows asyncio policy if needed
- Starts app bootstrap

### core/bootstrap.py

- Loads environment
- Configures logger
- Builds dependency registry
- Loads modules dynamically
- Builds router, event bus, scheduler, and transports

### core/router.py

- Registers commands from module manifests
- Prevents duplicate command ownership
- Dispatches commands to the correct module handler
- Measures latency and logs the result

### core/event_bus.py

- Supports `publish` and `subscribe`
- Delivers internal events to listeners asynchronously
- Contains exception boundaries per listener
- Logs listener success and failure without breaking the core

### core/scheduler.py

- Accepts job registrations from modules
- Runs recurring jobs through the chosen transport scheduler backend
- Wraps every job in safe logging and exception handling

### core/permissions.py

- Supports three levels: `viewer`, `operator`, `admin`
- Reads user-role mapping from `.env`
- Exposes authorization helpers to the router and handlers

### core/logging.py

- Centralized plain text logging
- Bounded file size using truncation or single-file rollover policy
- Redacts sensitive values

### core/dependency_registry.py

- Central place for shared clients, helpers, settings, and services
- Modules receive dependencies from the core context
- Modules must not install or wire dependencies themselves

## Module Contract

Each module is a feature plugin with isolated ownership.

Each module may declare:

- Metadata
- Zero or more commands
- Zero or more event listeners
- Zero or more scheduled jobs
- Optional startup and shutdown hooks

Each module must not:

- Import another module directly
- Read `.env` directly
- Configure logging directly
- Create independent schedulers
- Register Telegram handlers directly
- Install dependencies independently

## Dynamic Loading Strategy

The MVP should use folder-based dynamic discovery.

Each module folder contains:

- `plugin.json` for static metadata
- `module.py` for implementation

The loader should:

1. Scan `modules/*/plugin.json`
2. Validate manifest shape
3. Import the declared Python entrypoint
4. Build the module object
5. Register commands, listeners, and jobs
6. Skip invalid modules safely and report the reason

## Internal Event Bus

Suggested event categories for the MVP:

- `system.started`
- `system.stopped`
- `command.received`
- `command.completed`
- `command.failed`
- `job.started`
- `job.completed`
- `job.failed`
- `healthcheck.requested`

Suggested event payload rule:

- Event name is stable and string-based
- Payload is a typed dictionary or dataclass
- Payload contains no transport-specific raw objects unless explicitly wrapped

## Transport Strategy

Telegram is the only implemented transport in v1.

However, the core should avoid Telegram-specific concepts in module contracts.

Modules should receive an abstract interaction context that exposes operations such as:

- reply text
- send message
- publish event
- read caller identity and role
- access module config
- access shared dependencies

That keeps Slack or other channels viable later.

## Authorization Model

Authorization is centrally enforced.

Rules for MVP:

- User allowlist is configurable through `.env`
- Empty allowlist behavior must be configurable by installer
- Roles are `viewer`, `operator`, `admin`
- `/healthcheck` is admin-only
- Unauthorized access attempts must be logged without leaking private message content

Suggested environment model:

- `TG_BOT_TOKEN`
- `ALLOWED_USER_IDS`
- `ADMIN_USER_IDS`
- `OPERATOR_USER_IDS`
- `DEFAULT_ROLE`
- `GROUP_CHAT_ID`
- `LOG_MAX_BYTES`
- `APP_TIMEZONE`

## Logging and Audit Rules

The bot must log:

- startup
- shutdown
- command received
- command owner module
- latency
- job execution start and end
- success or failure
- admin actions

The bot must not log:

- tokens
- full private messages
- personal data beyond what is required for operational audit
- raw secrets from `.env`

Suggested audit format:

```text
timestamp | level | component | action=command.completed | command=status | module=status | user_id=123456 | role=admin | latency_ms=42
```

## Reliability Rules

1. A failing command handler must not bring down the core.
2. A failing event listener must not block the event bus.
3. A failing scheduled job must be isolated and logged.
4. An invalid plugin must not prevent valid plugins from loading.
5. The core must keep running even when one module is unhealthy.

## Example MVP Modules

### status

- Command: `/status`
- Purpose: expose uptime, Python version, active modules, health summary

### occurrences

- Neutral example of event or file-based alerts
- Can demonstrate scheduled scanning and event publication
- Must avoid business-specific wording in the core and module contract

### deadlines

- Neutral example of date-based reminders
- Can demonstrate recurring scheduled jobs and command rendering

## Testing Scope for MVP

Keep tests short and targeted.

Required:

- router registration and duplicate detection
- module loader contract validation
- event bus isolation on listener errors
- permission checks for roles
- a smoke test for one module integration path

Also required:

- lint
- basic type checker in CI

Not required:

- heavy end-to-end test matrix
- strict typing mode

## Documentation Policy

- Primary docs in English
- PT-BR companion docs allowed where useful
- Module authoring guidance must be explicit and easy to follow

## Delivery Order

1. Architecture and contract validation
2. Core scaffold implementation
3. Telegram transport implementation
4. Dynamic module loading
5. Status module
6. Neutral example modules
7. README, contributing, CI, and release polish

## Validation Checklist

Approve this document if the following statements are true:

- The core is domain-neutral.
- The module contract is strict enough to prevent architectural drift.
- Dynamic plugin loading is the correct default.
- Centralized dependencies are mandatory.
- Event bus plus router is the desired MVP foundation.
- Telegram is only a transport, not the architecture center.
- Example modules should remain generic and replaceable.
