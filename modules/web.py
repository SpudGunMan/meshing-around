#!/usr/bin/env python3

SSL = False
PORT = 8008 # python3 -m http.server 8008

import http.server
if SSL:
    import ssl

# boot up simple HTTP server
httpd = http.server.HTTPServer(('127.0.0.1', PORT), http.server.SimpleHTTPRequestHandler)

if SSL:
    # Generate with: openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    try:
        ctx.load_cert_chain(certfile='./server.pem')
    except FileNotFoundError:
        print("SSL certificate file not found. Please generate it using the command provided in the comments.")
        exit(1)
    #ctx.load_cert_chain(certfile='server.crt', keyfile='server.key')
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)


httpd.serve_forever()