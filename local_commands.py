#!/usr/bin/python3
# Locally defined command dictionary
# K7MHI Kelly Keeton 2025

from modules.filemon import read_file

local_commands = {
    # "hornet": lambda: read_file("hornet.txt", True),
}

# Bash example to emit list of files as meshing-around command fragments,
# in this case you might have a directory of files with text for 
# each county:
# ls | awk '{ printf "\"%s\": lambda: read_file(\"datafiles/counties/%s\", False),\n", $1, $1 }' >out.txt

