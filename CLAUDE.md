# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Faster APP** is a FastAPI framework with Django-style conventions. Core philosophy: **Convention over Configuration** (约定优于配置).

- Python 3.12+, FastAPI 0.116+, Tortoise ORM, Pydantic v2
- CLI via Google Fire, migrations via Aerich
- Primary language: Chinese (bilingual codebase)

## Development Commands

```bash
# Install dev environment
uv sync --all-extras --dev
uv run pre-commit install

# Linting & formatting
uv run ruff check faster_app/          # Check
uv run ruff check --fix faster_app/    # Auto-fix
uv run ruff format faster_app/

# Type checking
uv run mypy faster_app/

# Testing
uv run pytest                              # All tests
uv run pytest tests/test_models.py -v      # Single file
uv run pytest --cov=faster_app --cov-report=html

# Documentation
make docs-serve                            # Local preview
make docs-deploy                           # Deploy to GitHub Pages

# Build & release
make build && make upload
```

## Architecture

### Auto-Discovery System (Core Pattern)

The framework eliminates boilerplate through automatic discovery. All discoverers extend `BaseDiscover` (`utils/discover.py`):

| Discoverer | Location | Discovers | From |
|------------|----------|-----------|------|
| `RoutesDiscover` | `routes/discover.py` | `APIRouter` instances | `apps/*/` |
| `ModelDiscover` | `models/discover.py` | `tortoise.Model` subclasses | `apps/*/models.py` |
| `CommandDiscover` | `commands/discover.py` | `BaseCommand` subclasses | `apps/*/` |
| `MiddlewareDiscover` | `middleware/discover.py` | `BaseMiddleware` subclasses | `middleware/` |
| `SettingsDiscover` | `settings/discover.py` | `BaseSettings` subclasses | `config/` |

**How it works**: `BaseDiscover.discover()` walks directories, imports Python modules dynamically, and extracts instances/subclasses of specified types.

### Application Lifecycle

`app.py`:
1. `create_app()` - Factory that initializes FastAPI with lifespan
2. Discovers and registers middleware via `MiddlewareDiscover`
3. Discovers and includes routes via `RoutesDiscover` (with conflict validation if `VALIDATE_ROUTES=true`)
4. Registers exception handlers via `ExceptionManager`
5. `get_app()` - Singleton wrapper

### Key Modules

```
faster_app/
├── app.py              # FastAPI factory (create_app, get_app)
├── main.py             # Uvicorn entry point
├── cli.py              # Fire CLI entry point
├── models/base.py      # Base models: UUIDModel, DateTimeModel, EnumModel, ScopeModel
├── viewsets/           # DRF-like ViewSet system with mixins, permissions, filters
├── exceptions/         # FasterAppError base, built-in types, ExceptionManager
├── lifespan/           # Async context managers for app lifecycle
└── settings/builtins/settings.py  # DefaultSettings with nested configs
```

### ViewSet System (DRF-like)

Located in `viewsets/`:
- **Mixins**: `ListModelMixin`, `CreateModelMixin`, `RetrieveModelMixin`, `UpdateModelMixin`, `DestroyModelMixin`
- **ViewSets**: `ModelViewSet` (all CRUD), `ReadOnlyModelViewSet` (list/retrieve)
- **Support classes**: Permissions, Authentication, Filters, Throttling
- Convert to router: `router = as_router(MyViewSet, prefix="/items")`

## User Project Convention

```
my-project/
├── apps/                    # Feature modules (auto-discovered)
│   └── users/
│       ├── models.py        # Tortoise models
│       ├── routes.py        # APIRouter instances
│       ├── schemas.py       # Pydantic schemas
│       └── commands.py      # BaseCommand subclasses
├── config/settings.py       # Custom BaseSettings
├── middleware/              # Custom BaseMiddleware
└── .env                     # Environment variables
```

## CLI Commands

```bash
faster app demo              # Create example app structure
faster app config            # Create config directory
faster app env               # Create .env file
faster server start          # Start dev server (auto-reload)
faster db init               # Initialize Aerich migrations
faster db migrate --name=... # Generate migration
faster db upgrade            # Apply migrations
```

## Commit Convention

```
type(scope): subject

Types: feat, fix, docs, style, refactor, test, chore
Example: feat(models): add SoftDeleteModel base class
```
