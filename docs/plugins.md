# Plugin runtime

The new runtime has one entry point, `mesh_bot.py`. Its features come entirely from
paired files in `plugins.d`; a ping-only installation enables only `ping.toml`.
The original implementation is preserved under `integration/` for future plugin
ports. It is not a supported runnable bot or a dependency of the new runtime.

Requires Python 3.11+ (`tomllib`). From the repository root:

```sh
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python mesh_bot.py --check
printf 'ping\n' | venv/bin/python mesh_bot.py
venv/bin/python -m unittest discover -s tests -v
```

`bot.toml` defaults to console transport: each input line is treated as a DM
from node 1, and responses print to stdout. EOF shuts down the controller.
`bash launch.sh` also starts the new runtime. Use `--config /path/to/bot.toml`
for local settings; relative plugin and database paths resolve against that
configuration file, not the shell working directory.

For live operation, configure `[radio]` with `type = "tcp"`, `hostname`, and
optional `port` (4403 by default), or `type = "serial"` and `device`. Only one
radio named `primary` is currently supported. Live radio operation requires a
reachable node and has not been validated with physical hardware.

## Layers

- Controller: configuration, plugin adoption, startup report, signals, shutdown.
- Core: transport adapters, command dispatcher, policy, event queue, interval
  scheduler, UTF-8 byte chunking, serialized delivery, namespaced SQLite state.
- Plugins: feature logic, command registrations, event subscriptions, jobs,
  configuration validation, and lifecycle hooks.

The core has no feature command list. Routing is case insensitive and matches
whole command text followed by a space or end of message. Longer commands win:
`bbs read` takes priority over `bbs`. Duplicate commands or aliases reject the
later plugin; loading order is alphabetical. Unknown commands receive no reply.

## Add a plugin

Create `plugins.d/example.toml`:

```toml
[plugin]
id = "example"
version = "1.0.0"
api_version = 1
enabled = true

[settings]
greeting = "Hello"
```

Create `plugins.d/example.py`:

```python
from botcore.api import Command, Registration, Response

def register(settings):
    greeting = settings.get("greeting", "Hello")
    if not isinstance(greeting, str):
        raise ValueError("greeting must be text")

    async def hello(context):
        return Response(f"{greeting} {context.arguments}".rstrip())

    return Registration(commands=(
        Command("hello", hello, aliases=("hi",), help="Say hello"),
    ))
```

No core edits are required. Plugin filenames use lowercase letters, digits,
and underscores, beginning with a letter. Identity must match the filename.
Missing pairs, malformed TOML, incompatible API versions, import errors,
registration conflicts, and failed initialization appear as rejected plugins in
the startup report. Disabled plugins are not imported. Both files must exist.
Plugins implement and validate their own `[settings]`; the core validates the
manifest and registration contract. `--check` runs initialization and shutdown
hooks, so those hooks should avoid irreversible actions.

## Contract

Import public types from `botcore.api`. `register(settings)` is synchronous and
returns a `Registration`. It should only validate settings and construct handlers.
Handlers and lifecycle hooks are asynchronous; blocking I/O belongs in
`asyncio.to_thread`, or an asynchronous client.

- Commands receive `Context`: normalized command name, arguments, original
  `Message` (sender, channel, interface, DM status), and plugin services.
  Return a `Response`, a list of responses, or `None`.
- `Response(text)` replies to the incoming audience. `destination="private"`
  replies to the sender. `destination="channel"` targets a channel.
- `Subscription("event.name", handler)` receives `(Event, services)`.
  Services can emit custom events. Non-text radio packets currently emit
  `radio.packet` with the decoded packet dictionary; additional normalized
  radio events can be added in the transport adapter.
- `Job("name", interval_seconds, handler)` receives services. It first runs
  after the interval, then waits another interval after each execution.
  This first version supports intervals, not calendar/cron schedules.
- `start(services)` and `stop(services)` own resource setup and cleanup. Startup
  has a 10-second timeout and cleanup runs even when startup fails. Commands
  and jobs are activated only after successful startup. Job tasks are cancelled
  before shutdown hooks. Hooks must make cleanup safe after partial startup.

Services provide `get(key, default)` and `set(key, JSON_serializable_value)` in
plugin-scoped persistent SQLite state, `emit(Event(...))`, and `send(Response(...))`.
Emission and sending require an active plugin, so startup/shutdown hooks should
focus on resource management. Jobs and event handlers have no implicit reply
recipient: sending requires `destination="channel"` and an explicit channel.

Core policy applies blocked node IDs and command `admin_only`/`direct_only`
flags. Unsolicited broadcasts, DM-to-channel responses, channel changes on
public replies, and interface changes require the plugin ID in
`policy.broadcast_plugins`. Direct replies to received public channel commands
are allowed. Channel indices must be 0–7.

Delivery splits text without dropping or reordering characters, respecting
`core.message_bytes` as a UTF-8 byte limit. A delivery lock prevents chunks
from different responses interleaving; `core.send_delay` paces transmissions.
Transport failures are reported, without automatic retries or durable outbox
semantics in this version.

Exceptions in command, event, or job handlers are logged and counted in
`Runtime.health()` with the last error. They do not stop other plugins. Command,
event, and job handlers have a 30-second timeout. Plugins run as trusted Python
code inside one process: this API is a software boundary, not a security sandbox.
Infinite synchronous code, process termination, or malicious code cannot be
contained by these exception handlers. Plugin-owned tasks must be cancelled in
their shutdown hook; prefer registered jobs for core-managed background work.

Configuration is read at startup; restart to adopt changes. Original feature
code is migration reference under `integration/`; plugins must not import it.
