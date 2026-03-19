# FluxBuddy

FluxBuddy is an open source modular workflow bot core.

It provides a clean routing layer, a lightweight internal event bus, dynamic plugin loading, centralized dependency management, and Telegram as the first transport.

The project is intentionally domain-neutral. The core does not contain assumptions about any specific business area.

## Key Features

- Clean command routing
- Internal event bus
- Dynamic module loading from plugins
- Centralized configuration and dependencies
- Role-based access control (`viewer`, `operator`, `admin`)
- Bounded plain-text logging with sensitive-data redaction
- Safe scheduled jobs
- Telegram transport with room for future channels

## Project Status

This repository contains the MVP scaffold focused on production-ready core infrastructure.

Included example modules:

- `/status` — system status and uptime
- `/healthcheck` — admin-only health summary
- `/occurrences` — example of file-based monitoring and alert publication
- `/deadlines` — example of date-based reminders and daily alert jobs

## Requirements

- Python 3.11+
- Telegram bot token from [@BotFather](https://t.me/BotFather)
- Windows, Linux, or macOS

Tested target:

- Python 3.13

## Quick Start

### Windows automatic setup

```bat
setup.bat
```

Then edit `.env` and run:

```bat
run.bat
```

### Manual setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python main.py
```

## Environment Configuration

Main settings are stored in `.env`.

Important keys:

- `TG_BOT_TOKEN`
- `GROUP_CHAT_ID`
- `ADMIN_USER_IDS`
- `OPERATOR_USER_IDS`
- `ALLOWED_USER_IDS`
- `DEFAULT_ROLE`
- `LOG_FILE`
- `LOG_MAX_BYTES`
- `APP_TIMEZONE`

Module-specific configuration is also read from `.env` using prefixes.

Examples:

- `OCCURRENCES_FILE_PATH`
- `DEADLINES_FILE_PATH`

## Architecture Summary

FluxBuddy is built around four core ideas:

1. Router
   Routes commands to the owning module.

2. Event bus
   Lets modules communicate without importing each other.

3. Plugin loader
   Discovers feature modules dynamically from `modules/*/plugin.json`.

4. Dependency registry
   Keeps dependencies centralized in the core.

See:

- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE.pt-BR.md`
- `prompt.md`

## Module Contract

Each module is isolated as a feature plugin.

A module may define:

- commands
- event listeners
- scheduled jobs
- startup and shutdown hooks

A module must not:

- import another module
- read `.env` directly
- configure its own logger
- create its own scheduler
- register Telegram handlers directly
- install independent runtime dependencies without central approval

## Project Structure

```text
FluxBuddy/
├── main.py
├── prompt.md
├── core/
├── transports/
├── modules/
├── shared/
├── docs/
├── data/
└── logs/
```

## Logging and Safety

FluxBuddy logs:

- startup and shutdown
- command received and completed/failed
- module ownership
- latency
- scheduled job success/failure
- administrative actions

FluxBuddy does not log:

- bot token values
- private message contents in full
- sensitive environment values

## Development

Install development tools:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Run lint:

```bash
ruff check .
```

Run type check:

```bash
pyright
```

## Continuous Local Execution

For unattended local use on Windows:

- `run_forever.bat` restarts the app if it stops
- `install_task.bat` creates a Windows Scheduled Task to start the app on login

## Open Source Policy

- Core stability has priority
- Modules must follow the published contract
- Dependencies remain centralized
- Tests and lint checks must pass

## Documentation

Primary documentation is in English.

A PT-BR architecture companion is available in `docs/ARCHITECTURE.pt-BR.md`.

## License

Apache 2.0. See `LICENSE`.
