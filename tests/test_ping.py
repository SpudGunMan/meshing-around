import importlib.util
import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from botcore.api import Context, Message
from botcore.transport import radio_message

spec = importlib.util.spec_from_file_location('ping_tests_plugin',
    Path(__file__).resolve().parents[1] / 'plugins.d/ping.py')
ping = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ping
spec.loader.exec_module(ping)


class Services:
    message_bytes = 160

    def __init__(self):
        self.state, self.sent, self.events = {}, [], []

    def get(self, key, default=None):
        return self.state.get(key, default)

    def set(self, key, value):
        self.state[key] = value

    async def reply(self, response, message):
        self.sent.append((response, message))

    async def emit(self, event):
        self.events.append(event)


class PingTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.registration = ping.register({})
        self.services = Services()
        self.clock = patch.object(ping, 'monotonic', return_value=0)
        self.now = self.clock.start()
        self.addCleanup(self.clock.stop)

    async def request(self, command='ping', arguments='', **kwargs):
        message = Message(command + (' ' + arguments if arguments else ''),
            kwargs.pop('sender', 123), direct=kwargs.pop('direct', True), **kwargs)
        registered = next(c for c in self.registration.commands if command in (c.text, *c.aliases))
        return await registered.handler(Context(message, registered.text, arguments, self.services))

    async def tick(self, when):
        self.now.return_value = when
        await self.registration.jobs[0].handler(self.services)

    async def test_command_family_and_help(self):
        for command, expected in [('ping', '🏓 Pong.'), ('pinging', '🏓 Pong.'),
            ('pong', 'Ping.'), ('ack', 'Acknowledged.'), ('test', 'Testing, one, two, three.'),
            ('testing', 'Testing, one, two, three.'), ('cq', 'CQ acknowledged.'),
            ('cqcq', 'CQ acknowledged.'), ('cqcqcq', 'CQ acknowledged.'), ('🔔', 'I can hear you.')]:
            with self.subTest(command=command):
                self.assertTrue((await self.request(command)).text.startswith(expected))
        for command in ['ping?', 'pinging?', 'test?', 'ack?', 'cq?']:
            self.assertEqual((await self.request(command)).text, ping.HELP)
        self.assertEqual((await self.request('ping', 'help')).text, ping.HELP)

    async def test_diagnostics_have_units_and_keep_zero(self):
        text = (await self.request(snr=0, rssi=-85, noise_floor=-110, hops=1)).text
        self.assertIn('Route: 1 hop.', text)
        self.assertIn('SNR: 0 dB.', text)
        self.assertIn('RSSI: -85 dBm.', text)
        self.assertIn('Noise floor: -110 dBm.', text)
        self.assertIn('Route: direct RF.', (await self.request(hops=0)).text)
        self.assertIn('Route: MQTT.', (await self.request(hops=2, via_mqtt=True)).text)
        self.assertIn('Route: gateway.', (await self.request(transport='gateway')).text)
        self.assertNotIn('SNR', (await self.request(snr=float('nan'))).text)
        self.assertIn('This is K7MHI.', (await self.request('cq', node_name='K7MHI')).text)

    async def test_repeat_count_timing_completion_and_origin(self):
        result = await self.request(arguments='3 #Road test', channel=2, interface='secondary')
        self.assertIn('Starting 3 replies', result.text)
        await self.tick(19)
        self.assertEqual(self.services.sent, [])
        for moment in [20, 40, 60, 80]:
            await self.tick(moment)
        self.assertEqual(len(self.services.sent), 3)
        for index, (response, message) in enumerate(self.services.sent, 1):
            self.assertIn(f'Reply {index}/3.', response.text)
            self.assertIn('Tag: #Road test.', response.text)
            self.assertEqual(response.destination, 'private')
            self.assertEqual((message.sender, message.channel, message.interface), (123, 2, 'secondary'))
        self.assertEqual(self.services.state['requests'], 1)

    async def test_stop_is_scoped_and_cancels_future_replies(self):
        await self.request(arguments='3')
        self.assertEqual((await self.request(arguments='stop', sender=456)).text,
                         'You have no active sequence here.')
        await self.tick(20)
        self.assertEqual((await self.request('ack', 'stop')).text, 'Sequence stopped.')
        await self.tick(100)
        self.assertEqual(len(self.services.sent), 1)

    async def test_limits_busy_duplicate_and_public_requests(self):
        for count in ['0', '51', '800']:
            self.assertEqual((await self.request(arguments=count)).text, 'Choose a count from 1 to 50.')
        self.assertIn('Invalid arguments.', (await self.request(arguments='-1')).text)
        self.assertIn('direct message only.', (await self.request(arguments='3', direct=False)).text)
        await self.request(arguments='2')
        self.assertIn('already have', (await self.request(arguments='2')).text)
        await self.request(arguments='2', sender=456)
        self.assertIn('busy', (await self.request(arguments='2', sender=789)).text)
        self.assertIn('Pong.', (await self.request(arguments='123')).text)

    async def test_buffer_sizes_grow_and_never_exceed_core_limit(self):
        self.services.message_bytes = 100
        result = await self.request('testing', '4')
        self.assertIn('Starting 4 buffer-test messages', result.text)
        for when in [20, 40, 60, 80]:
            await self.tick(when)
        sizes = [len(response.text.encode()) for response, _ in self.services.sent]
        self.assertEqual(sizes, [49, 66, 83, 100])
        for index, (response, _) in enumerate(self.services.sent, 1):
            self.assertTrue(response.text.startswith(f'Test {index}/4 ({sizes[index-1]} B): '))
        await self.tick(100)
        self.assertEqual(len(self.services.sent), 4)

    async def test_channel_sequences_are_explicitly_enabled(self):
        self.registration = ping.register({'allow_channel_sequences': True, 'reply_privately': False})
        await self.request(arguments='2', direct=False, channel=3)
        await self.tick(20)
        response, message = self.services.sent[0]
        self.assertEqual(response.destination, 'reply')
        self.assertFalse(message.direct)
        self.assertEqual(message.channel, 3)

    async def test_tags_and_future_bbs_event(self):
        self.assertIn('Tag: #Field test.', (await self.request(arguments='#Field test')).text)
        await self.request(arguments='@ABCD')
        event = self.services.events[0]
        self.assertEqual(event.name, 'ping.mention_requested')
        self.assertEqual(event.data['target'], 'ABCD')
        self.assertEqual(event.data['sender'], 123)
        self.assertLessEqual(len(ping.clipped('long label ' * 100).encode()), 80)
        self.assertTrue(ping.clipped('long label ' * 100).endswith('…'))

    async def test_shutdown_and_send_failure_remove_sequences(self):
        await self.request(arguments='2')
        await self.registration.stop(self.services)
        await self.tick(20)
        self.assertEqual(self.services.sent, [])
        await self.request(arguments='2')

        async def failed(response, message):
            raise OSError('radio unavailable')

        self.services.reply = failed
        with self.assertRaises(OSError):
            await self.tick(40)
        self.assertEqual((await self.request(arguments='stop')).text, 'You have no active sequence here.')

    async def test_pending_event_reserves_capacity_and_can_be_cancelled(self):
        entered, release = asyncio.Event(), asyncio.Event()

        async def emit(event):
            entered.set()
            await release.wait()

        self.services.emit = emit
        task = asyncio.create_task(self.request(arguments='2 @ABCD'))
        await entered.wait()
        try:
            self.assertIn('already have', (await self.request(arguments='2')).text)
            await self.tick(20)
            self.assertEqual(self.services.sent, [])
            self.assertEqual((await self.request(arguments='stop')).text, 'Sequence stopped.')
            release.set()
            self.assertEqual((await task).text, 'Sequence cancelled.')
            await self.tick(40)
            self.assertEqual(self.services.sent, [])
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def test_event_failure_releases_reserved_sequence(self):
        async def emit(event):
            raise RuntimeError('event unavailable')

        self.services.emit = emit
        with self.assertRaises(RuntimeError):
            await self.request(arguments='2 @ABCD')
        self.assertIn('Starting 2 replies', (await self.request(arguments='2')).text)

    def test_settings_reject_invalid_values(self):
        for settings in [{'max_count': True}, {'max_count': 51}, {'max_sessions': 0},
                         {'buffer_bytes': 10}, {'interval_seconds': float('nan')},
                         {'interval_seconds': 0}, {'reply_privately': 'true'}, {'reply': ''}]:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                ping.register(settings)


class RadioMetadataTests(unittest.TestCase):
    def test_normalizes_link_metadata_and_missing_measurements(self):
        packet = {'from': 123, 'to': 42, 'channel': 2, 'rxSnr': 0, 'rxRssi': -70,
                  'hopStart': 3, 'hopLimit': 2, 'viaMqtt': True,
                  'decoded': {'payload': b'ping'}}
        message = radio_message(packet, 42, 'BOT', -100)
        self.assertEqual((message.snr, message.rssi, message.hops), (0, -70, 1))
        self.assertTrue(message.direct and message.via_mqtt)
        self.assertEqual(message.node_name, 'BOT')
        packet.update(hopLimit=4, rxSnr=float('inf'), rxRssi=True)
        message = radio_message(packet, 42)
        self.assertIsNone(message.hops)
        self.assertIsNone(message.snr)
        self.assertIsNone(message.rssi)
        packet.update(viaMqtt=False, transportMechanism='UDP')
        self.assertEqual(radio_message(packet, 42).transport, 'gateway')
        packet.update(transportMechanism='MQTT')
        self.assertTrue(radio_message(packet, 42).via_mqtt)
