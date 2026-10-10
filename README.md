# Mesh Bot

A plugin-driven Meshtastic bot, rebuilding the architecture of meshing-around.
One controller starts the core services and adopts enabled plugins from
`plugins.d/`. A ping-only bot enables only the ping plugin.

## Quick start

Requires Python 3.11 or newer.

```sh
bash bootstrap.sh
venv/bin/python mesh_bot.py --check
printf 'ping\n' | venv/bin/python mesh_bot.py
```

The default transport is a local console: type `ping` to receive `🏓 Pong.`.
Run `bash launch.sh` for an interactive session. EOF, Ctrl+C, or SIGTERM shuts
down the controller. Edit `bot.toml` to use a Meshtastic TCP or serial node.
Use `--config /path/to/local.toml` for a separate configuration file.

## Architecture

```text
mesh_bot.py       Primary entry point
botcore/          Controller, plugin API, and core services
plugins.d/        Paired feature logic (.py) and configuration (.toml)
bot.toml          Core, transport, and policy configuration
tests/            Tests of the new runtime
docs/             Plugin development documentation
integration/      Original implementation awaiting integration
data/             New runtime state (generated locally)
```

Core services handle command routing, policy, events, interval scheduling,
message formatting and delivery, and plugin-scoped storage. Plugins register
their own commands, event subscriptions, jobs, and lifecycle hooks without
changes to core code. See the [plugin development guide](docs/plugins.md).

## Validation

```sh
venv/bin/python -m unittest discover -s tests -v
```

Only ping has been ported. Physical radio operation has not yet been validated.
The original modules, assets, documentation, and deployment scripts are preserved
in [integration/](integration/README.md) as migration reference; they are not part
of the supported runtime. Use the original meshing-around project if you need
the original bot's feature set today.

## Containers

```sh
docker compose build
docker compose run --rm mesh-bot
```

The container uses the same `mesh_bot.py` entry point and console default.
Configuration and plugin files are built into the image; rebuild after editing
them. Compose persists only the new runtime's `data/` directory.

This project retains the original GPL license and acknowledges meshing-around's
authors and contributors. The `mesh_bot.py` name pays tribute to those roots.
