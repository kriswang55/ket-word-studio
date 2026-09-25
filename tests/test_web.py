from http.client import HTTPConnection
import json
import threading
from ket_studio.web_server import LocalServer


def test_static_server_assets_and_boundaries():
    server = LocalServer()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def request(path, method="GET"):
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        conn.request(method, path)
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    try:
        for path in (
            "/",
            "/app.js",
            "/engine.js",
            "/style.css",
            "/icon.svg",
            "/data/words.json",
        ):
            assert request(path)[0] == 200
        assert len(json.loads(request("/data/words.json")[1])) == 178
        assert request("/../ket_studio/service.py")[0] == 404
        assert request("/%2e%2e/README.md")[0] == 404
        assert request("/api/login", "POST")[0] == 501
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
