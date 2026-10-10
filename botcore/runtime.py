"""Routing, policy, delivery, events, jobs, and plugin-scoped state."""

import asyncio
import inspect
import json
import logging
import math
import sqlite3
from dataclasses import dataclass, field

from .api import Command, Context, Event, Message, Registration, Response

log = logging.getLogger(__name__)


def _payload_chunks(text: str, limit: int) -> list[str]:
    """Prefer word boundaries while preserving the original payload."""
    result, current, size = [], [], 0
    for char in text:
        width = len(char.encode("utf-8"))
        if width > limit:
            raise ValueError("message byte limit is too small for split tags and payload")
        while size + width > limit:
            boundary = next((i + 1 for i in range(len(current) - 1, -1, -1)
                             if current[i].isspace()), len(current))
            result.append("".join(current[:boundary]))
            current = current[boundary:]
            size = sum(len(item.encode("utf-8")) for item in current)
        current.append(char)
        size += width
    if current:
        result.append("".join(current))
    return result


def chunks(text: str, limit: int) -> list[str]:
    """Number multipart messages; include prefix bytes in every packet's budget."""
    if type(limit) is not int or limit < 4:
        raise ValueError("message byte limit must be at least 4")
    if not text:
        return []
    if len(text.encode("utf-8")) <= limit:
        return [text]
    total = 2
    while True:
        # Reserve the widest prefix, then recalculate if the count grows.
        budget = limit - len(f"[{total}/{total}] ")
        if budget < 1:
            raise ValueError("message byte limit is too small for split tags and payload")
        parts = _payload_chunks(text, budget)
        if len(parts) <= total:
            total = len(parts)
            return [f"[{index}/{total}] {part}" for index, part in enumerate(parts, 1)]
        total = len(parts)


@dataclass
class Policy:
    admins: frozenset[int] = frozenset()
    blocked: frozenset[int] = frozenset()
    broadcast_plugins: frozenset[str] = frozenset()

    def allows(self, message: Message, command: Command) -> bool:
        return (message.sender not in self.blocked
                and (not command.admin_only or message.sender in self.admins)
                and (not command.direct_only or message.direct))


@dataclass
class PluginState:
    registration: Registration
    status: str = "starting"
    errors: int = 0
    last_error: str | None = None
    tasks: list[asyncio.Task] = field(default_factory=list)


class PluginServices:
    def __init__(self, runtime, plugin):
        self._runtime, self._plugin = runtime, plugin

    @property
    def message_bytes(self):
        return self._runtime.byte_limit

    async def reply(self, response, message):
        """Delayed replies retain their original audience and delivery policy."""
        if self._runtime.plugins[self._plugin].status != "active":
            raise RuntimeError("plugin is not active")
        if message.sender in self._runtime.policy.blocked:
            raise PermissionError("sender is blocked")
        await self._runtime.deliver(self._plugin, response, message)

    def get(self, key, default=None):
        row = self._runtime.db.execute(
            "SELECT value FROM state WHERE plugin=? AND key=?",
            (self._plugin, key)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, key, value):
        with self._runtime.db:
            self._runtime.db.execute("INSERT OR REPLACE INTO state VALUES (?, ?, ?)",
                                     (self._plugin, key, json.dumps(value)))

    async def emit(self, event):
        if self._runtime.plugins[self._plugin].status != "active":
            raise RuntimeError("plugin is not active")
        if not isinstance(event, Event) or not event.name:
            raise ValueError("emit requires a named Event")
        await self._runtime.events.put(event)

    async def send(self, response):
        if self._runtime.plugins[self._plugin].status != "active":
            raise RuntimeError("plugin is not active")
        await self._runtime.deliver(self._plugin, response)


class Runtime:
    def __init__(self, transport, database, *, policy=None, byte_limit=160, send_delay=0.7):
        chunks("", byte_limit)
        if not math.isfinite(send_delay) or send_delay < 0:
            raise ValueError("send delay must be finite and nonnegative")
        self.transport, self.policy = transport, policy or Policy()
        self.byte_limit, self.send_delay = byte_limit, send_delay
        self.db = sqlite3.connect(database)
        self.db.execute("CREATE TABLE IF NOT EXISTS state "
                        "(plugin TEXT, key TEXT, value TEXT, PRIMARY KEY(plugin,key))")
        self.plugins, self.commands = {}, {}
        self.events = asyncio.Queue(maxsize=256)
        self.delivery_lock = asyncio.Lock()

    def health(self):
        return {name: {"status": state.status, "errors": state.errors,
                       "last_error": state.last_error}
                for name, state in self.plugins.items()}

    def validate(self, registration):
        if not isinstance(registration, Registration):
            raise TypeError("register must return Registration")
        names = set()
        for command in registration.commands:
            if not isinstance(command, Command) or not inspect.iscoroutinefunction(command.handler):
                raise ValueError("commands require async handlers")
            for name in (command.text, *command.aliases):
                if not isinstance(name, str) or not name.strip() or name != " ".join(name.lower().split()):
                    raise ValueError("command names must be normalized lowercase text")
                if name in self.commands or name in names:
                    raise ValueError(f"command conflict: {name}")
                names.add(name)
        job_names = set()
        for job in registration.jobs:
            if not job.name or job.name in job_names or not math.isfinite(job.interval) or job.interval <= 0:
                raise ValueError("jobs need unique names and positive finite intervals")
            job_names.add(job.name)
            if not inspect.iscoroutinefunction(job.handler):
                raise ValueError("jobs require async handlers")
        for subscription in registration.events:
            if not subscription.event or not inspect.iscoroutinefunction(subscription.handler):
                raise ValueError("subscriptions require named events and async handlers")
        for hook in (registration.start, registration.stop):
            if hook is not None and not inspect.iscoroutinefunction(hook):
                raise ValueError("lifecycle hooks must be async")

    async def activate(self, name, registration):
        if name in self.plugins:
            raise ValueError(f"duplicate plugin: {name}")
        self.validate(registration)
        state = self.plugins[name] = PluginState(registration)
        services = PluginServices(self, name)
        try:
            if registration.start:
                await asyncio.wait_for(registration.start(services), 10)
            state.status = "active"
            for command in registration.commands:
                for alias in (command.text, *command.aliases):
                    self.commands[alias] = (name, command)
            for job in registration.jobs:
                state.tasks.append(asyncio.create_task(self._job(name, job, services)))
        except BaseException:
            state.status = "failed"
            if registration.stop:
                try:
                    await asyncio.wait_for(registration.stop(services), 10)
                except Exception:
                    log.exception("Cleanup failed for %s", name)
            raise

    def failed(self, name, error):
        state = self.plugins[name]
        state.errors += 1
        state.last_error = str(error)
        log.exception("Plugin %s handler failed", name)

    async def dispatch(self, message):
        text = message.text.strip()
        # Longest command wins; matching is case insensitive and boundary aware.
        for alias in sorted(self.commands, key=len, reverse=True):
            if text.lower() != alias and not text.lower().startswith(alias + " "):
                continue
            name, command = self.commands[alias]
            if not self.policy.allows(message, command):
                return False
            try:
                reply = await asyncio.wait_for(command.handler(Context(
                    message, command.text, text[len(alias):].strip(),
                    PluginServices(self, name))), 30)
                for response in reply if isinstance(reply, list) else ([] if reply is None else [reply]):
                    await self.deliver(name, response, message)
            except Exception as error:
                self.failed(name, error)
            return True
        return False

    async def deliver(self, plugin, response, message=None):
        if not isinstance(response, Response) or not isinstance(response.text, str):
            raise TypeError("handlers must return Response objects")
        if response.destination not in ("reply", "private", "channel"):
            raise ValueError("invalid response destination")
        if message is None and response.destination != "channel":
            raise ValueError("unsolicited messages require an explicit channel")
        channel = response.channel if response.channel is not None else (message.channel if message else None)
        interface = response.interface or (message.interface if message else "primary")
        destination = message.sender if message and (response.destination == "private" or
                       (response.destination == "reply" and message.direct)) else None
        # Scheduled broadcasts and any change of audience require explicit permission.
        broadcast = destination is None and (message is None or message.direct or channel != message.channel)
        if (broadcast or (message and interface != message.interface)) and plugin not in self.policy.broadcast_plugins:
            raise PermissionError("plugin is not permitted to broadcast or change interface")
        if not isinstance(channel, int) or isinstance(channel, bool) or not 0 <= channel <= 7:
            raise ValueError("channel must be between 0 and 7")
        async with self.delivery_lock:
            for part in chunks(response.text, self.byte_limit):
                await self.transport.send(part, destination, channel, interface)
                await asyncio.sleep(self.send_delay)

    async def event_loop(self):
        while True:
            event = await self.events.get()
            for name, state in self.plugins.items():
                if state.status != "active":
                    continue
                for subscription in state.registration.events:
                    if subscription.event == event.name:
                        try:
                            await asyncio.wait_for(subscription.handler(event, PluginServices(self, name)), 30)
                        except Exception as error:
                            self.failed(name, error)

    async def _job(self, name, job, services):
        while True:
            await asyncio.sleep(job.interval)
            try:
                await asyncio.wait_for(job.handler(services), 30)
            except Exception as error:
                self.failed(name, error)

    async def close(self):
        for name, state in reversed(list(self.plugins.items())):
            was_active = state.status == "active"
            if was_active:
                state.status = "stopping"
            for task in state.tasks:
                task.cancel()
            await asyncio.gather(*state.tasks, return_exceptions=True)
            if was_active and state.registration.stop:
                try:
                    await asyncio.wait_for(state.registration.stop(PluginServices(self, name)), 10)
                except Exception as error:
                    self.failed(name, error)
            state.status = "stopped" if was_active else state.status
        self.commands.clear()
        self.db.close()
