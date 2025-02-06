#!/usr/bin/env python3
# This is a simple web server that serves up the content of the webRoot directory
# The reporting data is all that is currently being served up
# TODO - add interaction to mesh?
# to use this today run it seperately and open a browser to http://localhost:8420

import os
import http.server

# Set the desired IP address
server_ip = '127.0.0.1'

# Set the port for the server
PORT = 8420

# Generate with: openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
SSL = False

# Set to True to enable logging sdtout
webServerLogs = False

# Determine the directory where this script is located.
script_dir = os.path.dirname(os.path.realpath(__file__))

# Go up one level from the modules directory to the project root.
project_root = os.path.abspath(os.path.join(script_dir, ".."))

# Build the absolute path to the webRoot folder; to where index.html is located.
webRoot = os.path.join(project_root, "etc", "www")

if SSL:
    import ssl

# disable logging
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if webServerLogs:
            super().log_message(format, *args)

# Change the current working directory to webRoot
os.chdir(webRoot)

# boot up simple HTTP server
httpd = http.server.HTTPServer(('127.0.0.1', PORT), QuietHandler)

if SSL:
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    try:
        ctx.load_cert_chain(certfile='./server.pem')
    except FileNotFoundError:
        print("SSL certificate file not found. Please generate it using the command provided in the comments.")
        exit(1)
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

# Create the HTTP server instance with the desired IP address
httpd = http.server.HTTPServer((server_ip, PORT), QuietHandler)

# Print out the URL using the IP address stored in server_ip
print(f"Serving reports at http://{server_ip}:{PORT} Press ^C to quit.\n\n")

if not webServerLogs:
    print("Server Logs are disabled")
# Serve forever, that is until the user interrupts the process
httpd.serve_forever()
exit(0)
