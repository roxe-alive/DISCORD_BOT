"""Tiny Flask server to keep the process alive.

Expose a couple of lightweight endpoints that an uptime monitor
can ping periodically. The server runs in a background thread
so the Discord bot can start normally.

Environment variables:
- PORT: Port to bind the HTTP server (default: 8080)
"""

from __future__ import annotations

import os
from threading import Thread
from typing import Optional

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def root():
    return "OK", 200


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


def _run() -> None:
    port = int(os.environ.get("PORT", "5000"))
    # 0.0.0.0 to be reachable from outside (e.g., hosting provider)
    app.run(host="0.0.0.0", port=port)


def keep_alive() -> Thread:
    """Start the Flask server in a daemon thread and return the thread.

    The thread is marked daemon=True so it won't block process exit.
    """
    t = Thread(target=_run, daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    # Allow running directly for local testing
    _run()
