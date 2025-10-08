#!/usr/bin/env python3
# User Statistics Tracking Module for Leaderboard Feature
# K7MHI Kelly Keeton 2025

import time
import json
import os
from modules.log import *

# File to store user statistics
STATS_FILE = "data/user_stats.json"

# Global statistics dictionary
user_stats = {}

def load_stats():
    """Load user statistics from file"""
    global user_stats
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                user_stats = json.load(f)
                logger.debug(f"Loaded user stats: {len(user_stats)} users")
        else:
            user_stats = {}
            logger.info(f"No existing stats file found, starting fresh")
    except Exception as e:
        logger.error(f"Error loading user stats: {e}")
        user_stats = {}

def save_stats():
    """Save user statistics to file"""
    try:
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(user_stats, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving user stats: {e}")

def update_user_stat(user_id, stat_type, value=1, device_id=1):
    """
    Update a specific statistic for a user
    
    Args:
        user_id: User's node ID
        stat_type: Type of stat ('messages', 'commands', 'last_seen', 'battery', etc.)
        value: Value to add or set (default 1 for counters)
        device_id: Device interface ID
    """
    global user_stats
    
    user_id_str = str(user_id)
    
    if user_id_str not in user_stats:
        user_stats[user_id_str] = {
            'messages': 0,
            'commands': 0,
            'first_seen': time.time(),
            'last_seen': time.time(),
            'battery': 100,
            'uptime': 0,
            'device_id': device_id
        }
    
    # Update the specific stat
    if stat_type in ['messages', 'commands']:
        user_stats[user_id_str][stat_type] += value
    else:
        user_stats[user_id_str][stat_type] = value
    
    # Always update last_seen when any stat is updated
    user_stats[user_id_str]['last_seen'] = time.time()

def get_top_users(stat_type='messages', limit=10, timeframe=None):
    """
    Get top users for a specific statistic
    
    Args:
        stat_type: Type of stat to sort by
        limit: Number of top users to return
        timeframe: Optional time range in seconds (e.g., 86400 for last 24 hours)
    
    Returns:
        List of tuples: [(user_id, stat_value), ...]
    """
    global user_stats
    current_time = time.time()
    
    # Filter by timeframe if specified
    filtered_stats = user_stats
    if timeframe:
        filtered_stats = {
            uid: stats for uid, stats in user_stats.items()
            if current_time - stats.get('last_seen', 0) <= timeframe
        }
    
    # Sort by the requested stat
    if stat_type in ['messages', 'commands', 'uptime']:
        sorted_users = sorted(
            filtered_stats.items(),
            key=lambda x: x[1].get(stat_type, 0),
            reverse=True
        )
    elif stat_type == 'battery':
        # For battery, lower is "better" for the depleted leaderboard
        sorted_users = sorted(
            filtered_stats.items(),
            key=lambda x: x[1].get(stat_type, 100),
            reverse=False
        )
    elif stat_type == 'online':
        # Most recently seen
        sorted_users = sorted(
            filtered_stats.items(),
            key=lambda x: x[1].get('last_seen', 0),
            reverse=True
        )
    else:
        sorted_users = sorted(
            filtered_stats.items(),
            key=lambda x: x[1].get(stat_type, 0),
            reverse=True
        )
    
    return [(uid, stats.get(stat_type, 0)) for uid, stats in sorted_users[:limit]]

def format_leaderboard(stat_type, limit=10, timeframe=None):
    """
    Format a leaderboard message for display
    
    Args:
        stat_type: Type of stat to display
        limit: Number of users to show
        timeframe: Optional timeframe in seconds
    
    Returns:
        Formatted string for display
    """
    top_users = get_top_users(stat_type, limit, timeframe)
    
    if not top_users:
        return "No statistics available yet."
    
    # Stat type display names
    stat_names = {
        'messages': 'Most Messages',
        'commands': 'Most Commands',
        'battery': 'Lowest Battery',
        'online': 'Most Recently Active',
        'uptime': 'Highest Uptime'
    }
    
    title = stat_names.get(stat_type, f'Top {stat_type.title()}')
    timeframe_str = ""
    if timeframe == 86400:
        timeframe_str = " (24h)"
    elif timeframe == 604800:
        timeframe_str = " (7d)"
    
    msg = f"🏆 {title}{timeframe_str}:\n"
    
    for idx, (uid, value) in enumerate(top_users, start=1):
        if stat_type == 'battery':
            msg += f"{idx}. {uid}: {value}%\n"
        elif stat_type == 'online':
            # Show how long ago they were seen
            elapsed = time.time() - value
            if elapsed < 60:
                time_str = f"{int(elapsed)}s ago"
            elif elapsed < 3600:
                time_str = f"{int(elapsed/60)}m ago"
            else:
                time_str = f"{int(elapsed/3600)}h ago"
            msg += f"{idx}. {uid}: {time_str}\n"
        elif stat_type == 'uptime':
            # Convert seconds to hours
            hours = int(value / 3600)
            msg += f"{idx}. {uid}: {hours}h\n"
        else:
            msg += f"{idx}. {uid}: {value}\n"
    
    return msg

# Load stats on module import
load_stats()
