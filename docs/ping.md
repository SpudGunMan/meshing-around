# Ping plugin

Migrated from `handle_ping` in the original mesh/pong bots, their command maps,
and `handleMultiPing` in the original system module. It uses only `botcore.api`;
no original feature modules or installation changes are required.

| Command | Behavior |
| --- | --- |
| `ping`, `pinging` | Reply with “🏓 Pong.” and available link diagnostics. |
| `pong` | Reply with “Ping.” |
| `ack` | Reply with “Acknowledged.” |
| `test`, `testing` | Reply with “Testing, one, two, three.” |
| `cq`, `cqcq`, `cqcqcq` | Acknowledge CQ and identify the local node when known. |
| `🔔` | Reply with “I can hear you.” |
| `ping?`, `test?`, `ack?`, etc. | Display plugin help; `ping help` also works. |
| `ping N`, `ack N`, `cq N` | Schedule exactly N diagnostic replies after confirmation. |
| `test N` | Schedule N increasing, byte-sized buffer-test payloads. |
| `ping stop` | Cancel your sequence on this radio/channel; other command families accept `stop` too. |
| `ping #Field test` | Label the response; counted requests can also include a label. |
| `ping @ABCD` | Label the reply and emit `ping.mention_requested` for future integration. |

## Configuration

`plugins.d/ping.toml` supplies these settings:

- `reply`: configured ping response; default `🏓 Pong.`
- `reply_privately`: default true, including replies to public-channel requests.
- `interval_seconds`: default 20, permitted range 1–3600 seconds.
- `max_count`: default 50, permitted range 2–50 replies.
- `max_sessions`: default 2, permitted range 1–8 concurrent sequences.
- `allow_channel_sequences`: default false; repeated requests must arrive by DM.
- `buffer_bytes`: default 160, permitted range 32–200 bytes, capped by the core
  message byte limit so a buffer-test payload stays in one transmission.

Only valid booleans, finite timing values, and bounded integers are accepted.
Counts outside 1–`max_count` are rejected explicitly. The legacy spoken-test
shorthand `123` and `1234` produces one reply. Duplicate sequences are rejected
until the earlier sequence completes or is cancelled. Limits apply across all
users; a sender can cancel only their sequence on the originating interface and
channel. Restart and shutdown discard active sequences rather than resuming
radio traffic unexpectedly. Accepted request counts are stored in plugin state.

The core scheduler checks due sequences once per second. The first reply follows
the configured interval; later replies wait at least that interval after the
previous delivery. Core pacing and congestion can delay replies. `stop` prevents
future replies but cannot recall a packet already being transmitted. Delivery
failure removes the affected sequence and is reported in core health/logs.

Diagnostics use normalized transport metadata: SNR in dB, RSSI and noise floor
in dBm, hop count, MQTT route, and local short name. Missing measurements are
omitted; zero is a valid measurement. Hop count is derived only from valid
`hopStart`/`hopLimit` fields; it is not guessed when they are absent. Noise floor
is included only when provided by the transport's local node data. Console
requests have no invented radio readings.

## Text conventions and migration decisions

System-generated prose uses sentence case and punctuation. Standard radio terms
retain their conventional forms: CQ, RF, MQTT, SNR, RSSI, dB, dBm, and B (bytes).
An occasional emoji is allowed; emoji clusters, misspellings, unexplained legacy
shorthand, and repeated exclamation marks are avoided. Long user labels are
shortened at word boundaries to 80 UTF-8 bytes and marked with an ellipsis.
An oversized single-word label becomes an ellipsis rather than a broken word.
Buffer-test payloads intentionally contain ASCII binary test data rather than
prose. Normal responses still pass through core chunking.

The old `ping @node` path called BBS storage and a joke provider directly. Those
features belong to future BBS/joke plugins, so ping emits an event with sender,
target, channel, and interface instead of importing them or pretending delivery
occurred. This event does not currently deliver a joke. Echo, MOTD, node lists,
system information, and automatic banning are separate features/policy and are
not adopted by ping. Excessive counts are rejected without modifying a ban list.

Physical Meshtastic radio operation remains unverified; tests exercise metadata
normalization, routing, formatting, sequence timing, byte sizes, cancellation,
limits, lifecycle cleanup, and delivery policy without hardware.
