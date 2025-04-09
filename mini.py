def app(environ, start_response):
    data = b"Hello from raw WSGI app!"
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [data]
