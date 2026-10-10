"""Composition root: configuration, startup, health, and orderly shutdown."""

import argparse
import asyncio
import json
import logging
import signal
import tomllib
from pathlib import Path

from .loader import load_plugins
from .runtime import Policy, Runtime
from .transport import ConsoleTransport, MeshtasticTransport


async def run(config_path, check=False):
    with config_path.open("rb") as stream:
        config = tomllib.load(stream)
    root = config_path.resolve().parent
    core, radio = config.get("core", {}), config.get("radio", {})
    database = root / core.get("database", "data/core.db")
    database.parent.mkdir(parents=True, exist_ok=True)
    kind = radio.get("type", "console")
    if kind not in ("console", "tcp", "serial"):
        raise ValueError("radio.type must be console, tcp, or serial")
    transport = ConsoleTransport() if kind == "console" else MeshtasticTransport(radio)
    policy_config = config.get("policy", {})
    runtime = Runtime(transport, database, policy=Policy(
        frozenset(policy_config.get("admins", [])),
        frozenset(policy_config.get("blocked", [])),
        frozenset(policy_config.get("broadcast_plugins", []))),
        byte_limit=core.get("message_bytes", 160), send_delay=core.get("send_delay", 0.7))
    tasks = []
    started = False
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    installed_signals = []
    try:
        report = await load_plugins(runtime, root / core.get("plugins", "plugins.d"))
        print(json.dumps({"plugins": report}, indent=2), flush=True)
        if not any(item["status"] == "active" for item in report.values()):
            raise RuntimeError("no active plugins")
        if check:
            return
        await transport.start(runtime)
        started = True
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
            installed_signals.append(sig)
        tasks = [asyncio.create_task(transport.run()), asyncio.create_task(runtime.event_loop()),
                 asyncio.create_task(stop.wait())]
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            task.result()
    finally:
        for sig in installed_signals:
            loop.remove_signal_handler(sig)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if started:
            try:
                await transport.close()
            finally:
                await runtime.close()
        else:
            await runtime.close()


def main():
    parser = argparse.ArgumentParser(description="Plugin-driven Meshtastic bot")
    parser.add_argument("--config", type=Path, default=Path("bot.toml"))
    parser.add_argument("--check", action="store_true", help="load, initialize, report health, then shut down")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run(args.config, args.check))
    except (OSError, ValueError, RuntimeError, tomllib.TOMLDecodeError) as error:
        parser.exit(1, f"Bot startup failed: {error}\n")
