"""Adapters keep Meshtastic and console details outside plugins."""

import asyncio
import logging
import math
import sys

from .api import Event, Message

log = logging.getLogger(__name__)


def number(value):
    """Accept genuine finite radio measurements, including zero."""
    return value if type(value) in (int, float) and math.isfinite(value) else None


def radio_message(packet, local_node, node_name=None, noise_floor=None):
    decoded = packet.get("decoded", {})
    payload = decoded.get("payload", b"")
    text = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
    start, remaining = packet.get("hopStart"), packet.get("hopLimit")
    hops = start - remaining if (type(start) is int and type(remaining) is int
                                and 0 <= remaining <= start <= 7) else None
    mechanism = str(packet.get("transport_mechanism") or packet.get("transportMechanism")
                    or decoded.get("transport_mechanism") or decoded.get("transportMechanism") or "").lower()
    mqtt = packet.get("viaMqtt") is True or decoded.get("viaMqtt") is True or "mqtt" in mechanism
    transport = "mqtt" if mqtt else "gateway" if "udp" in mechanism else "rf" if "lora" in mechanism else None
    return Message(text, packet["from"], packet.get("channel", 0),
        direct=packet.get("to") == local_node, snr=number(packet.get("rxSnr")),
        rssi=number(packet.get("rxRssi")), hops=hops,
        via_mqtt=mqtt, transport=transport,
        node_name=node_name if isinstance(node_name, str) else None, noise_floor=number(noise_floor))


class ConsoleTransport:
    async def start(self, runtime):
        self.runtime = runtime

    async def send(self, text, destination, channel, interface):
        print(f"[{interface} channel={channel} to={destination or 'broadcast'}] {text}", flush=True)

    async def run(self):
        reader = asyncio.StreamReader()
        pipe, _ = await asyncio.get_running_loop().connect_read_pipe(
            lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)
        try:
            while line := await reader.readline():
                await self.runtime.dispatch(Message(line.decode("utf-8").rstrip("\r\n"),
                                                    sender=1, direct=True))
        finally:
            pipe.close()

    async def close(self):
        pass


class MeshtasticTransport:
    def __init__(self, settings):
        self.settings = settings
        self.interface = None
        self.accepting = False
        self.pending = set()

    async def start(self, runtime):
        from pubsub import pub
        self.runtime, self.loop = runtime, asyncio.get_running_loop()
        kind = self.settings.get("type")
        if kind == "tcp":
            from meshtastic.tcp_interface import TCPInterface
            self.interface = await asyncio.to_thread(TCPInterface,
                hostname=self.settings["hostname"], portNumber=self.settings.get("port", 4403))
        elif kind == "serial":
            from meshtastic.serial_interface import SerialInterface
            self.interface = await asyncio.to_thread(SerialInterface, self.settings.get("device"))
        else:
            raise ValueError("radio type must be serial or tcp")
        self.accepting = True
        pub.subscribe(self.receive, "meshtastic.receive")

    def receive(self, packet, interface):
        if not self.accepting or interface is not self.interface:
            return
        # Meshtastic invokes callbacks from a worker thread.
        self.loop.call_soon_threadsafe(self._enqueue, packet)

    def _enqueue(self, packet):
        if not self.accepting:
            return
        if len(self.pending) >= 256:
            log.warning("Dropping radio packet: receive queue full")
            return
        task = asyncio.create_task(self._handle(packet))
        self.pending.add(task)
        task.add_done_callback(self.pending.discard)

    async def _handle(self, packet):
        try:
            decoded = packet.get("decoded", {})
            if decoded.get("portnum") == "TEXT_MESSAGE_APP":
                nodes = getattr(self.interface, "nodes", {}) or {}
                local_node = self.interface.myInfo.my_node_num
                local_info = nodes.get(f"!{local_node:08x}", {})
                name = local_info.get("user", {}).get("shortName")
                noise = local_info.get("localStats", {}).get("noiseFloor")
                await self.runtime.dispatch(radio_message(packet, local_node, name, noise))
            else:
                await self.runtime.events.put(Event("radio.packet", packet))
        except Exception:
            log.exception("Unable to process radio packet")

    async def send(self, text, destination, channel, interface):
        if interface != "primary":
            raise ValueError("unknown radio interface")
        kwargs = {"channelIndex": channel}
        if destination is not None:
            kwargs["destinationId"] = destination
        await asyncio.to_thread(self.interface.sendText, text, **kwargs)

    async def run(self):
        await asyncio.Event().wait()

    async def close(self):
        from pubsub import pub
        self.accepting = False
        pub.unsubscribe(self.receive, "meshtastic.receive")
        for task in list(self.pending):
            task.cancel()
        await asyncio.gather(*self.pending, return_exceptions=True)
        if self.interface:
            await asyncio.to_thread(self.interface.close)
