#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Configuration Merge Script
# Merges user configuration with default settings
# 2025 Kelly Keeton K7MHI mesh-around and its meshtastic
import shutil
import configparser
import os


def merge_configs(default_config_path, user_config_path, output_config_path):
    # Load default configuration (INI)
    default_config = configparser.ConfigParser()
    default_config.read(default_config_path)

    # Load user configuration (INI)
    user_config = configparser.ConfigParser()
    user_config.read(user_config_path)

    # Merge configurations
    for section in user_config.sections():
        if not default_config.has_section(section):
            default_config.add_section(section)
        for key, value in user_config.items(section):
            default_config.set(section, key, value)

    # Save merged configuration as INI
    with open(output_config_path, 'w', encoding='utf-8') as f:
        default_config.write(f)

def backup_config(config_path, backup_path):
    shutil.copyfile(config_path, backup_path)

def show_config_changes(user_config_path, merged_config_path):
    if not os.path.exists(merged_config_path) or os.path.getsize(merged_config_path) == 0:
        print(f"Error: {merged_config_path} is empty or missing!")
        return

    # Load user config (as dict)
    user_config = configparser.ConfigParser()
    user_config.read(user_config_path)
    user_dict = {s: dict(user_config.items(s)) for s in user_config.sections()}

    # Load merged config (as dict)
    merged_config = configparser.ConfigParser()
    merged_config.read(merged_config_path)
    merged_dict = {s: dict(merged_config.items(s)) for s in merged_config.sections()}

    print("\n--- Changes in merged configuration ---")
    for section in merged_dict:
        if section not in user_dict:
            print(f"[{section}] (new section)")
            for k, v in merged_dict[section].items():
                print(f"  {k} = {v} (added)")
        else:
            for k, v in merged_dict[section].items():
                if k not in user_dict[section]:
                    print(f"[{section}] {k} = {v} (added)")
                elif user_dict[section][k] != v:
                    print(f"[{section}] {k}: {user_dict[section][k]} -> {v} (changed)")
    print("--- End of changes ---\n")

if __name__ == "__main__":
    print("MESHING-AROUND: Configuration Merge Script for config.ini checking updates from config.template")
    print("---------------------------------------------------------------")
    master_config_path = 'config.template'
    user_config_path = 'config.ini'
    output_config = 'config_new.ini'
    backup_config_path = 'config.bak'
    try:
        backup_config(user_config_path, backup_config_path)
        print(f"Backup of user config created at {backup_config_path}")
        merge_configs(master_config_path, user_config_path, output_config)
        print(f"Merged configuration saved to {output_config}")
        show_config_changes(user_config_path, output_config)
        print("Please review the new configuration and replace your existing config.ini if needed.")
        print(" cp config_new.ini config.ini")
    except Exception as e:
        print(f"Error during configuration merge: {e}")
