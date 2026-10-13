
"""Local development server with fallback for GES SPA routes."""

import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

FRONTEND_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 5500


class GESRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _serve_spa_route(self):
        parsed = urlsplit(self.path)
        path = parsed.path.rstrip("/") or "/"

        is_information_page = path in {"/about", "/sources", "/legal"}
        is_species_page = re.fullmatch(
            r"/species/[^/]+", path, flags=re.IGNORECASE
        ) is not None

        if not (is_information_page or is_species_page):
            return

        self.path = "/index.html"
        if parsed.query:
            self.path += "?" + parsed.query

    def do_GET(self):
        self._serve_spa_route()
        super().do_GET()

    def do_HEAD(self):
        self._serve_spa_route()
        super().do_HEAD()


if __name__ == "__main__":
    with ThreadingHTTPServer((HOST, PORT), GESRequestHandler) as server:
        print(f"GES frontend running at http://{HOST}:{PORT}/", flush=True)
        print("Press Ctrl+C to stop.", flush=True)
        server.serve_forever()
