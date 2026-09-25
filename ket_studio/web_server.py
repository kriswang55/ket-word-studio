"""Serve the same static site as GitHub Pages for offline/local preview."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote
import argparse
import threading
import webbrowser
from .paths import PACKAGE_DIR

SITE_DIR = PACKAGE_DIR.parent / "site"
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        try:
            relative = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
            target = (SITE_DIR / relative).resolve()
            if (
                not target.is_relative_to(SITE_DIR.resolve())
                or target.suffix not in TYPES
            ):
                self.send_error(404)
                return
            body = target.read_bytes()
        except (OSError, ValueError):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", TYPES[target.suffix])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0):
        super().__init__(("127.0.0.1", port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Preview the KET Word Studio static website"
    )
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)
    try:
        server = LocalServer(args.port)
    except OSError as exc:
        parser.exit(1, f"Cannot start preview: {exc}. Choose another --port.\n")
    url = f"http://127.0.0.1:{server.server_port}/"
    print(
        f"KET Word Studio: {url}\nKeep this window open. Press Ctrl+C to stop.",
        flush=True,
    )
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
