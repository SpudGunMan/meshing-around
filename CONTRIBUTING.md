# Contributing

Develop against the plugin runtime documented in [docs/plugins.md](docs/plugins.md).
Feature plugins live in `plugins.d/` and use `botcore.api`; they must not import
the original code under `integration/`. That directory is migration reference.

Run `venv/bin/python -m unittest discover -s tests -v` before proposing changes.
Include useful tests for new behavior and document plugin configuration.
