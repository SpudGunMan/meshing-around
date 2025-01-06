#!/usr/bin/env python3
# This is a simple web server that serves up the content of the webRoot directory
# The reporting data is all that is currently being served up
# TODO - add interaction to mesh?
# to use this today run it seperately and open a browser to http://localhost:8420

import os
import http.server

# Set the port for the server
PORT = 8420

# set webRoot index.html location
webRoot = "../etc/www"

# Set to True to enable logging sdtout
webServerLogs = False

# Generate with: openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
SSL = False

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

httpd.serve_forever()