"""The public plugin contract. No radio implementation belongs here."""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Mapping, Protocol


@dataclass(frozen=True)
class Message:
    text: str
    sender: int
    channel: int = 0
    interface: str = "primary"
    direct: bool = False
    snr: float | None = None
    rssi: float | None = None
    hops: int | None = None
    via_mqtt: bool = False
    node_name: str | None = None
    noise_floor: float | None = None
    transport: str | None = None


@dataclass(frozen=True)
class Response:
    text: str
    destination: str = "reply"  # reply, private, or channel
    channel: int | None = None
    interface: str | None = None


@dataclass(frozen=True)
class Event:
    name: str
    data: Mapping[str, Any] = field(default_factory=dict)


class Services(Protocol):
    @property
    def message_bytes(self) -> int: ...
    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    async def emit(self, event: Event) -> None: ...
    async def send(self, response: Response) -> None: ...
    async def reply(self, response: Response, message: Message) -> None: ...


@dataclass(frozen=True)
class Context:
    message: Message
    command: str
    arguments: str
    services: Services


Handler = Callable[[Context], Awaitable[Response | list[Response] | None]]
EventHandler = Callable[[Event, Services], Awaitable[None]]
JobHandler = Callable[[Services], Awaitable[None]]
Hook = Callable[[Services], Awaitable[None]]


@dataclass(frozen=True)
class Command:
    text: str
    handler: Handler
    aliases: tuple[str, ...] = ()
    help: str = ""
    admin_only: bool = False
    direct_only: bool = False


@dataclass(frozen=True)
class Subscription:
    event: str
    handler: EventHandler


@dataclass(frozen=True)
class Job:
    name: str
    interval: float
    handler: JobHandler


@dataclass(frozen=True)
class Registration:
    commands: tuple[Command, ...] = ()
    events: tuple[Subscription, ...] = ()
    jobs: tuple[Job, ...] = ()
    start: Hook | None = None
    stop: Hook | None = None
