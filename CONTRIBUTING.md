# Contributing to FluxBuddy

Thanks for contributing to FluxBuddy.

## Core Principles

- The core must remain stable and domain-neutral.
- Feature modules must follow the official module contract.
- Modules must not import each other.
- Runtime dependencies must remain centralized in the core.
- Tests, lint, and type checks must pass before merge.

## What to Contribute

Good contributions include:

- core reliability improvements
- transport abstractions
- module contract improvements
- example modules that stay domain-neutral
- tests and CI improvements
- documentation improvements

## Before Opening a Pull Request

Make sure that:

1. The change fits the architecture in `docs/ARCHITECTURE.md`.
2. The change does not introduce business-specific assumptions into the core.
3. The change does not add hidden coupling between modules.
4. The change keeps dependencies centralized.
5. Tests and checks pass locally.

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
```

## Quality Checks

Run before submitting:

```bash
pytest
ruff check .
pyright
```

## Module Rules

If you are adding or editing a module:

- use the contract in `prompt.md`
- do not read `.env` directly from the module
- do not register Telegram handlers directly
- do not create your own scheduler, logger, or transport client
- do not import another module
- keep behavior isolated and testable

## Pull Request Expectations

A good pull request should include:

- a clear problem statement
- a focused change set
- tests for new core behavior when relevant
- updated docs if the public contract changes

## Reporting Issues

When opening an issue, include:

- expected behavior
- actual behavior
- reproduction steps
- Python version
- OS
- relevant logs with sensitive values removed

## Architecture Changes

If you propose changes to the module contract, plugin format, or routing model, document the reasoning clearly and explain migration impact.
