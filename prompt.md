# FluxBuddy Module Authoring Prompt

Use this prompt whenever you want to design or implement a new FluxBuddy module.

The goal is to keep every module compatible with the core architecture, transport-agnostic where possible, and safe for long-term open source maintenance.

## Instructions for the Authoring Assistant

You are creating a new module for FluxBuddy.

FluxBuddy is a modular workflow bot core with:

- dynamic plugin loading
- centralized dependency management
- internal event bus communication
- support for command handlers, event listeners, and scheduled jobs
- Telegram as the first transport, but not the only future transport

Your task is to propose or implement a module that respects the official module contract.

## Hard Constraints

1. Do not put business-specific assumptions into the core.
2. Do not import another module directly.
3. Do not add module-local third-party dependencies unless explicitly approved and added centrally.
4. Do not read `.env` directly from the module.
5. Do not instantiate your own logger, scheduler, transport client, or event bus.
6. Do not register Telegram handlers directly.
7. Do not place secrets in code, docs, tests, or examples.
8. Keep the module isolated as a feature plugin.

## Core Expectations

The module must integrate through the core only.

The module may provide:

- commands
- event listeners
- scheduled jobs
- startup hooks
- shutdown hooks

The module must receive what it needs from the core context, including:

- settings
- logger
- shared clients
- helper services
- event bus
- permission helpers

## Required Output Structure

When proposing a new module, always answer in this order:

1. Module purpose
2. User-facing commands
3. Events consumed
4. Events published
5. Scheduled jobs
6. Required core-managed dependencies
7. Configuration keys
8. Permission model
9. Failure handling
10. Observability needs
11. Test scope
12. Files to create or change

## Module Design Rules

### Commands

- Commands must be owned by exactly one module.
- Commands must have a short description.
- Commands must define minimum role access.
- Commands must return user-safe text.

### Events

- Prefer event names that describe business meaning, not transport details.
- Event payloads must be explicit and minimal.
- Listener errors must be recoverable.

### Scheduled Jobs

- Jobs must be idempotent when practical.
- Jobs must tolerate transient failures.
- Jobs must publish events when useful instead of coupling directly to other modules.

### Dependencies

- Dependencies are centralized in the core.
- If a new package is needed, justify why it belongs in the shared runtime.
- Avoid dependency sprawl.

### Security

- Never log secrets.
- Never expose full private message contents in logs.
- Avoid storing personal data unless strictly needed.
- Respect role-based access.

### Logging

The module should produce meaningful operational logs through the shared logger only.

Log examples:

- command started
- command completed
- command failed
- scheduled job completed
- external source unavailable

### Error Handling

- Fail closed when permissions are unclear.
- Return safe user messages.
- Raise structured errors only when the core can handle them.
- Never crash the application intentionally.

## Plugin Manifest Expectations

Each module should have a manifest similar to this:

```json
{
  "name": "status",
  "version": "0.1.0",
  "enabled": true,
  "entrypoint": "modules.status.module:create_module"
}
```

## Implementation Template

Use this planning template before coding:

```text
Module name:
Primary purpose:
Commands:
Roles required:
Events consumed:
Events published:
Jobs:
Dependencies from core:
Configuration:
Failure modes:
Metrics/logging:
Tests:
```

## Review Checklist

Before finalizing a module, verify:

- It does not import another module.
- It does not bypass the core router.
- It does not create its own dependency container.
- It does not assume Telegram-only behavior unless explicitly isolated in transport formatting.
- It documents commands, events, jobs, and permissions.
- It includes minimal tests for its registration path and one happy path.

## Example Request to Use This Prompt

Design a new FluxBuddy module named `announcements` that provides a command to list recent announcements, a scheduled job to scan a local source every 10 minutes, and publishes an internal event when a new item is found. Use only core-managed dependencies, define roles, identify failure modes, and propose the exact files to create.
