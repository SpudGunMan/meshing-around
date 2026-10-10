"""Mesh diagnostics migrated from the original mesh and pong bots.

All delivery, scheduling, and storage use the public plugin API.
"""

import math
from time import monotonic
from dataclasses import dataclass

from botcore.api import Command, Event, Job, Message, Registration, Response


HELP = (
    "Ping commands: ping, pong, ack, test, and cq. "
    "Use 'ping N' for N replies or 'test N' for N growing buffer-test messages. "
    "Use 'ping stop' to cancel your sequence. Add #tag or @node to label a request. "
    "Use 'ping?' for help."
)


def clipped(text, limit=80):
    """Shorten labels at word boundaries; mark omission with an ellipsis."""
    text = " ".join(text.split())
    if len(text.encode("utf-8")) <= limit:
        return text
    words, used = [], 0
    for word in text.split():
        size = len(word.encode("utf-8")) + (1 if words else 0)
        if used + size > limit - 3:
            break
        words.append(word)
        used += size
    return " ".join(words) + "…"


def diagnostics(message):
    details = []
    if message.via_mqtt:
        details.append("Route: MQTT.")
    elif message.transport == "gateway":
        details.append("Route: gateway.")
    elif message.hops is not None:
        details.append("Route: direct RF." if message.hops == 0 else
                       f"Route: {message.hops} {'hop' if message.hops == 1 else 'hops'}.")
    elif message.transport == "rf":
        details.append("Route: RF.")
    for value, label, units in ((message.snr, "SNR", "dB"), (message.rssi, "RSSI", "dBm"),
                                (message.noise_floor, "Noise floor", "dBm")):
        if type(value) in (int, float) and math.isfinite(value):
            details.append(f"{label}: {value:g} {units}.")
    return " ".join(details)


@dataclass
class Sequence:
    message: Message
    kind: str
    total: int
    label: str
    next_due: float
    index: int = 0
    ready: bool = False


def register(settings):
    reply = settings.get("reply", "🏓 Pong.")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("ping settings.reply must be nonempty text")
    limits = {"max_count": (50, 2, 50), "max_sessions": (2, 1, 8),
              "buffer_bytes": (160, 32, 200)}
    values = {}
    for name, (default, minimum, maximum) in limits.items():
        value = settings.get(name, default)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"ping settings.{name} must be an integer from {minimum} to {maximum}")
        values[name] = value
    interval = settings.get("interval_seconds", 20)
    if type(interval) not in (int, float) or not math.isfinite(interval) or not 1 <= interval <= 3600:
        raise ValueError("ping settings.interval_seconds must be from 1 to 3600")
    for name, default in (("reply_privately", True), ("allow_channel_sequences", False)):
        values[name] = settings.get(name, default)
        if type(values[name]) is not bool:
            raise ValueError(f"ping settings.{name} must be a boolean")
    sessions = {}

    def response(text):
        return Response(text, "private" if values["reply_privately"] else "reply")

    def body(kind, message, label):
        text = {"ping": reply, "pong": "Ping.", "ack": "Acknowledged.",
                "test": "Testing, one, two, three.", "bell": "I can hear you.",
                "cq": f"CQ acknowledged. This is {clipped(message.node_name or 'Mesh Bot', 32)}."}[kind]
        info = diagnostics(message)
        tag = f"Tag: {label}" + ("" if label.endswith((".", "!", "?", "…")) else ".") if label else ""
        return " ".join(part for part in (text, info, tag) if part)

    async def handle(context):
        message = context.message
        key = (message.sender, message.interface, message.channel)
        arguments = context.arguments.strip()
        if context.command.endswith("?") or arguments.lower() in ("?", "help"):
            return response(HELP)
        if arguments.lower() == "stop":
            stopped = sessions.pop(key, None)
            return response("Sequence stopped." if stopped else "You have no active sequence here.")
        words = arguments.split(maxsplit=1)
        count, label = 1, ""
        if words:
            if words[0].isascii() and words[0].isdigit() and len(words[0]) <= 4:
                count = int(words[0])
                if count in (123, 1234):
                    count = 1
                arguments = words[1] if len(words) > 1 else ""
            if arguments:
                if not arguments.startswith(("#", "@")) or len(arguments) == 1:
                    return response("Invalid arguments. Use 'ping N', 'ping stop', or 'ping #tag'.")
                label = clipped(arguments)
        if not 1 <= count <= values["max_count"]:
            return response(f"Choose a count from 1 to {values['max_count']}.")
        kind = {"ping": "ping", "pong": "pong", "ack": "ack", "test": "test",
                "cq": "cq", "🔔": "bell"}[context.command]
        if count > 1:
            if not message.direct and not values["allow_channel_sequences"]:
                return response("Repeated replies are available by direct message only.")
            if key in sessions:
                return response("You already have an active sequence here. Use 'ping stop' first.")
            if len(sessions) >= values["max_sessions"]:
                return response("The sequence service is busy. Please try again later.")
            if kind == "test" and context.services.message_bytes < 32:
                return response("Buffer tests require a message limit of at least 32 bytes.")
        pending = Sequence(message, kind, count, label, monotonic() + interval) if count > 1 else None
        if pending:
            # Reserve capacity before an event emission can yield to another request.
            sessions[key] = pending
        try:
            if label.startswith("@"):
                await context.services.emit(Event("ping.mention_requested", {
                    "target": arguments.split()[0][1:], "sender": message.sender,
                    "channel": message.channel, "interface": message.interface}))
            context.services.set("requests", context.services.get("requests", 0) + 1)
        except BaseException:
            if pending and sessions.get(key) is pending:
                sessions.pop(key)
            raise
        if count > 1:
            if sessions.get(key) is not pending:
                return response("Sequence cancelled.")
            pending.next_due = monotonic() + interval
            pending.ready = True
            noun = "buffer-test messages" if kind == "test" else "replies"
            return response(f"Starting {count} {noun}, approximately {interval:g} seconds apart. "
                            "Use 'ping stop' to cancel.")
        return response(body(kind, message, label))

    async def tick(services):
        for key, session in list(sessions.items()):
            if sessions.get(key) is not session or not session.ready or monotonic() < session.next_due:
                continue
            session.index += 1
            if session.kind == "test":
                maximum = min(values["buffer_bytes"], services.message_bytes)
                size = 32 + (maximum - 32) * session.index // session.total
                header = f"Test {session.index}/{session.total} ({size} B): "
                text = header + ("01" * size)[:size - len(header)]
            else:
                text = f"Reply {session.index}/{session.total}. " + body(
                    session.kind, session.message, session.label)
            try:
                await services.reply(response(text), session.message)
                session.next_due = monotonic() + interval
            except BaseException:
                if sessions.get(key) is session:
                    sessions.pop(key)
                raise
            if session.index >= session.total and sessions.get(key) is session:
                sessions.pop(key)

    async def stop(services):
        sessions.clear()

    commands = []
    for name, aliases in (("ping", ("pinging",)), ("pong", ()), ("ack", ()),
                          ("test", ("testing",)), ("cq", ("cqcq", "cqcqcq")), ("🔔", ())):
        commands.append(Command(name, handle, aliases=aliases, help=HELP))
        commands.append(Command(name + "?", handle, aliases=tuple(a + "?" for a in aliases), help=HELP))
    return Registration(commands=tuple(commands), jobs=(Job("sequences", 1, tick),), stop=stop)
