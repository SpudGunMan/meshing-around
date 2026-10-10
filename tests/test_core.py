import asyncio
import tempfile
import unittest
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path

from botcore.api import Command, Event, Job, Message, Registration, Response, Subscription
from botcore.loader import load_plugins
from botcore.runtime import PluginServices, Policy, Runtime, chunks
from botcore.transport import MeshtasticTransport


class RecordingTransport:
    def __init__(self):
        self.sent = []

    async def send(self, text, destination, channel, interface):
        self.sent.append((text, destination, channel, interface))


class CoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        self.transport = RecordingTransport()
        self.runtime = Runtime(self.transport, self.directory / "state.db", send_delay=0, byte_limit=8)

    async def asyncTearDown(self):
        await self.runtime.close()
        self.tmp.cleanup()

    async def test_longest_command_alias_arguments_and_private_delivery(self):
        seen = []

        async def handler(context):
            seen.append((context.command, context.arguments))
            return Response("Hello 🌍 world")

        await self.runtime.activate("bbs", Registration(commands=(
            Command("bbs", handler), Command("bbs read", handler, aliases=("read",)))))
        self.assertTrue(await self.runtime.dispatch(Message("BBS READ 42", 99, 2, direct=True)))
        self.assertEqual(seen, [("bbs read", "42")])
        self.assertEqual("".join(item[0] for item in self.transport.sent), "Hello 🌍 world")
        self.assertTrue(all(len(item[0].encode()) <= 8 and item[1:] == (99, 2, "primary")
                            for item in self.transport.sent))
        self.assertFalse(await self.runtime.dispatch(Message("bbsread", 99)))

    async def test_policy_blocks_without_invoking_handler(self):
        calls = []

        async def handler(context):
            calls.append(context)
            return Response("ok")

        self.runtime.policy = Policy(admins=frozenset({1}), blocked=frozenset({3}))
        await self.runtime.activate("admin", Registration(commands=(Command("secret", handler,
                                    admin_only=True, direct_only=True),)))
        for message in (Message("secret", 2, direct=True), Message("secret", 1),
                        Message("secret", 3, direct=True)):
            self.assertFalse(await self.runtime.dispatch(message))
        self.assertEqual(calls, [])
        self.assertTrue(await self.runtime.dispatch(Message("secret", 1, direct=True)))

    async def test_conflict_has_no_partial_registration(self):
        async def handler(context):
            return Response("ok")

        await self.runtime.activate("first", Registration(commands=(Command("ping", handler),)))
        with self.assertRaisesRegex(ValueError, "conflict"):
            await self.runtime.activate("second", Registration(commands=(
                Command("other", handler), Command("ping", handler))))
        self.assertNotIn("other", self.runtime.commands)
        self.assertNotIn("second", self.runtime.plugins)

    async def test_start_failure_cleans_up_and_never_activates(self):
        cleaned = []

        async def start(services):
            raise RuntimeError("broken")

        async def stop(services):
            cleaned.append(True)

        async def handler(context):
            return Response("ok")

        with self.assertRaisesRegex(RuntimeError, "broken"):
            await self.runtime.activate("broken", Registration(commands=(Command("broken", handler),),
                                                               start=start, stop=stop))
        self.assertEqual(cleaned, [True])
        self.assertNotIn("broken", self.runtime.commands)
        self.assertEqual(self.runtime.health()["broken"]["status"], "failed")

    async def test_handler_failure_is_contained_and_reported(self):
        async def handler(context):
            raise ValueError("bad request")

        await self.runtime.activate("bad", Registration(commands=(Command("bad", handler),)))
        with self.assertLogs("botcore.runtime", level="ERROR"):
            await self.runtime.dispatch(Message("bad", 1))
        self.assertEqual(self.runtime.health()["bad"]["errors"], 1)
        self.assertEqual(self.transport.sent, [])

    async def test_broadcast_requires_explicit_permission(self):
        with self.assertRaises(PermissionError):
            await self.runtime.deliver("wx", Response("alert", "channel", 2))
        with self.assertRaises(PermissionError):
            await self.runtime.deliver("wx", Response("alert", "channel", 2), Message("wx", 1, direct=True))
        self.runtime.policy = Policy(broadcast_plugins=frozenset({"wx"}))
        await self.runtime.deliver("wx", Response("alert", "channel", 2))
        self.assertEqual(self.transport.sent, [("alert", None, 2, "primary")])

    async def test_state_is_namespaced_and_persistent(self):
        first, second = PluginServices(self.runtime, "first"), PluginServices(self.runtime, "second")
        first.set("count", 3)
        self.assertIsNone(second.get("count"))
        other = Runtime(self.transport, self.directory / "state.db", send_delay=0)
        try:
            self.assertEqual(PluginServices(other, "first").get("count"), 3)
        finally:
            await other.close()

    async def test_delayed_reply_preserves_recipient_and_rechecks_policy(self):
        await self.runtime.activate("diagnostics", Registration())
        services = PluginServices(self.runtime, "diagnostics")
        origin = Message("ping 2", 123, 2, "primary", direct=True)
        await services.reply(Response("Reply."), origin)
        self.assertEqual(self.transport.sent, [("Reply.", 123, 2, "primary")])
        self.runtime.policy = Policy(blocked=frozenset({123}))
        with self.assertRaises(PermissionError):
            await services.reply(Response("Reply."), origin)
        with self.assertRaises(PermissionError):
            await services.reply(Response("Reply.", "channel", 3), Message("ping", 456, direct=True))
        self.runtime.plugins["diagnostics"].status = "failed"
        with self.assertRaises(RuntimeError):
            await services.reply(Response("Reply."), origin)

    async def test_events_jobs_and_shutdown(self):
        fired, stopped = asyncio.Event(), []

        async def job(services):
            await services.emit(Event("tick", {"value": 42}))

        async def listener(event, services):
            self.assertEqual(event.data["value"], 42)
            fired.set()

        async def stop(services):
            stopped.append(True)

        await self.runtime.activate("clock", Registration(events=(Subscription("tick", listener),),
            jobs=(Job("tick", 0.01, job),), stop=stop))
        task = asyncio.create_task(self.runtime.event_loop())
        try:
            await asyncio.wait_for(fired.wait(), 1)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        # Stop once here and replace the runtime for teardown.
        old = self.runtime
        await old.close()
        self.assertEqual(stopped, [True])
        self.assertTrue(all(t.done() for t in old.plugins["clock"].tasks))
        self.runtime = Runtime(self.transport, ":memory:", send_delay=0)

    def plugin(self, name, source, metadata=None):
        (self.directory / f"{name}.py").write_text(source)
        (self.directory / f"{name}.toml").write_text(metadata or
            f'[plugin]\nid="{name}"\nversion="1"\napi_version=1\nenabled=true\n')

    async def test_loader_skips_disabled_before_import_and_rejects_invalid(self):
        self.plugin("disabled", "raise AssertionError('must not import')", '[plugin]\nenabled=false\n')
        self.plugin("invalid", "raise AssertionError('must not import')",
                    '[plugin]\nid="invalid"\nversion="1"\napi_version=99\nenabled=true\n')
        (self.directory / "orphan.py").write_text("")
        self.plugin("exit", "raise SystemExit(1)")
        self.plugin("valid", "from botcore.api import Registration\ndef register(settings): return Registration()\n")
        report = await load_plugins(self.runtime, self.directory)
        self.assertEqual(report["disabled"]["status"], "disabled")
        for name in ("invalid", "orphan", "exit"):
            self.assertEqual(report[name]["status"], "rejected")
        self.assertEqual(report["valid"]["status"], "active")

    async def test_real_ping_plugin(self):
        report = await load_plugins(self.runtime, Path(__file__).resolve().parents[1] / "plugins.d")
        self.assertEqual(report["ping"]["status"], "active")
        await self.runtime.dispatch(Message("ping", 123, direct=True))
        self.assertEqual("".join(item[0] for item in self.transport.sent), "🏓 Pong.")
        self.assertEqual(PluginServices(self.runtime, "ping").get("requests"), 1)

    async def test_radio_adapter_normalizes_packets_and_delivery(self):
        calls = []

        def send_text(text, **kwargs):
            calls.append((text, kwargs))

        radio = MeshtasticTransport({})
        radio.interface = SimpleNamespace(myInfo=SimpleNamespace(my_node_num=42), sendText=send_text)
        radio.runtime = self.runtime
        self.runtime.transport = radio
        await load_plugins(self.runtime, Path(__file__).resolve().parents[1] / "plugins.d")
        await radio._handle({"from": 123, "to": 42, "channel": 2,
                             "decoded": {"portnum": "TEXT_MESSAGE_APP", "payload": b"ping"}})
        self.assertEqual("".join(text for text, _ in calls), "🏓 Pong.")
        self.assertTrue(all(kwargs == {"channelIndex": 2, "destinationId": 123} for _, kwargs in calls))
        calls.clear()
        await radio._handle({"from": 123, "to": 0xffffffff, "channel": 2,
                             "decoded": {"portnum": "TEXT_MESSAGE_APP", "payload": b"ping"}})
        self.assertTrue(all(kwargs == {"channelIndex": 2, "destinationId": 123} for _, kwargs in calls))
        await radio._handle({"decoded": {"portnum": "POSITION_APP"}})
        event = self.runtime.events.get_nowait()
        self.assertEqual(event.name, "radio.packet")

    async def test_loader_supports_plugins_with_dataclasses(self):
        self.plugin("record", "from dataclasses import dataclass\n"
            "from botcore.api import Registration\n@dataclass\nclass Record:\n    value: int\n"
            "def register(settings): return Registration()\n")
        report = await load_plugins(self.runtime, self.directory)
        self.assertEqual(report["record"]["status"], "active")


class FormattingTests(unittest.TestCase):
    def test_word_boundaries_keep_punctuation_with_words(self):
        text = "Please stop the sequence. Try again later."
        parts = chunks(text, 16)
        self.assertEqual("".join(parts), text)
        self.assertTrue(all(len(part.encode()) <= 16 for part in parts))
        self.assertTrue(any("sequence." in part for part in parts))
        self.assertEqual(chunks("supercalifragilistic", 8), ["supercal", "ifragili", "stic"])

    def test_utf8_and_empty_text(self):
        text = "a🌍é\n" * 50
        parts = chunks(text, 7)
        self.assertEqual("".join(parts), text)
        self.assertTrue(all(len(part.encode("utf-8")) <= 7 for part in parts))
        self.assertEqual(chunks("", 7), [])
        with self.assertRaises(ValueError):
            chunks(text, 3)


class ControllerTests(unittest.TestCase):
    def test_console_pipeline_and_clean_eof_shutdown(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "bot.toml"
            plugins = Path(__file__).resolve().parents[1] / "plugins.d"
            config.write_text(f'[core]\nplugins="{plugins}"\nsend_delay=0\n[radio]\ntype="console"\n')
            result = subprocess.run([sys.executable, "mesh_bot.py", "--config", str(config)],
                input="ping\nPING\nunknown\n", text=True, capture_output=True, timeout=5,
                cwd=plugins.parent)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count("🏓 Pong."), 2)
            self.assertIn('"status": "active"', result.stdout)
