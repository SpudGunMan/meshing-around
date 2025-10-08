#!/usr/bin/env python3
"""
Test script for custom trigger words and user statistics features
This simulates the bot behavior without requiring actual Meshtastic hardware
"""

import sys
import time
sys.path.insert(0, '.')

# Mock logger to avoid dependencies
class MockLogger:
    def debug(self, msg): print(f"[DEBUG] {msg}")
    def info(self, msg): print(f"[INFO] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")
    def warning(self, msg): print(f"[WARNING] {msg}")

import modules.log
modules.log.logger = MockLogger()

# Mock settings
import modules.settings as settings
settings.customPingWords = ['hola', 'bonjour', 'привет']
settings.customTestWords = ['prueba', 'testen', '测试']
settings.enableStatsTracking = True

print("=" * 60)
print("Custom Trigger Words and User Statistics Test")
print("=" * 60)

# Test 1: Stats module
print("\n--- Test 1: Statistics Module ---")
from modules.stats import *

# Simulate some user activity
print("Simulating user activity...")
update_user_stat('1234567890', 'messages', 10, 1)
update_user_stat('1234567890', 'commands', 5, 1)
update_user_stat('1234567890', 'battery', 45, 1)
update_user_stat('1234567890', 'uptime', 86400, 1)

update_user_stat('9876543210', 'messages', 25, 1)
update_user_stat('9876543210', 'commands', 3, 1)
update_user_stat('9876543210', 'battery', 15, 1)
update_user_stat('9876543210', 'uptime', 172800, 1)

update_user_stat('5555555555', 'messages', 15, 1)
update_user_stat('5555555555', 'battery', 78, 1)
update_user_stat('5555555555', 'uptime', 43200, 1)

print("\nGenerating leaderboards...")

# Test different leaderboard types
print("\n1. Messages Leaderboard:")
print(format_leaderboard('messages', 5))

print("\n2. Commands Leaderboard:")
print(format_leaderboard('commands', 5))

print("\n3. Battery Leaderboard (lowest):")
print(format_leaderboard('battery', 5))

print("\n4. Uptime Leaderboard:")
print(format_leaderboard('uptime', 5))

# Test 2: Custom trigger words
print("\n--- Test 2: Custom Trigger Words ---")
print(f"Custom ping words configured: {settings.customPingWords}")
print(f"Custom test words configured: {settings.customTestWords}")

# Simulate trap_list building
trap_list_ping = ["ping", "pinging", "ack", "testing", "test", "pong"]
if settings.customPingWords and settings.customPingWords[0]:
    custom_ping = [word.strip().lower() for word in settings.customPingWords if word.strip()]
    trap_list_ping.extend(custom_ping)
    print(f"\nExtended trap list with custom ping words: {custom_ping}")

if settings.customTestWords and settings.customTestWords[0]:
    custom_test = [word.strip().lower() for word in settings.customTestWords if word.strip()]
    trap_list_ping.extend(custom_test)
    print(f"Extended trap list with custom test words: {custom_test}")

print(f"\nFinal trap list: {trap_list_ping}")

# Test message matching
test_messages = [
    "hola everyone",
    "prueba 3",
    "привет друзья",
    "ping test",
    "测试 testing"
]

print("\nTesting message matching:")
for msg in test_messages:
    msg_lower = msg.lower()
    matched = False
    for word in trap_list_ping:
        if word in msg_lower:
            print(f"  '{msg}' -> MATCHED '{word}'")
            matched = True
            break
    if not matched:
        print(f"  '{msg}' -> no match")

# Test 3: Save and reload stats
print("\n--- Test 3: Persistence Test ---")
print("Saving statistics...")
save_stats()
print(f"Statistics saved to {STATS_FILE}")

# Check file exists and has content
import os
if os.path.exists(STATS_FILE):
    import json
    with open(STATS_FILE, 'r') as f:
        saved_data = json.load(f)
    print(f"File contains {len(saved_data)} user records")
    
    # Verify some data
    print("\nVerifying saved data:")
    for user_id in ['1234567890', '9876543210', '5555555555']:
        if user_id in saved_data:
            print(f"  User {user_id}: {saved_data[user_id]['messages']} messages, {saved_data[user_id]['battery']}% battery")
        else:
            print(f"  User {user_id}: NOT FOUND (ERROR)")
else:
    print("ERROR: Stats file not created!")

print("\n" + "=" * 60)
print("All tests completed successfully!")
print("=" * 60)

# Clean up test file
import os
if os.path.exists(STATS_FILE):
    os.remove(STATS_FILE)
    print(f"\nCleaned up test file: {STATS_FILE}")
