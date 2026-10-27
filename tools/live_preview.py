"""Live browser preview for development.

Runs the game in a hidden window, streams frames to http://localhost:8765 and forwards
clicks and keys back. Restarts itself whenever a .py file in the project changes.

    venv/bin/python tools/live_preview.py
"""
import io
import json
import os
import queue
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PORT = int(os.environ.get("PORT", 8765))
FPS = 30

frame = b""
frame_ready = threading.Condition()
events = queue.Queue()
status = {"started": time.time(), "error": None, "size": [462, 768]}

KEYS = {"Enter": "ENTER", " ": "SPACE", "Escape": "ESCAPE", "ArrowLeft": "LEFT", "ArrowRight": "RIGHT",
        "r": "R", "R": "R", **{str(d): f"KEY_{d}" for d in range(10)}}


def sources():
    return {p: p.stat().st_mtime for p in ROOT.glob("**/*.py") if "venv" not in p.parts}


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT).stdout.rstrip()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send((Path(__file__).parent / "live_preview.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/status":
            info = {**status, "branch": git("branch", "--show-current"), "commit": git("log", "-1", "--format=%h %s"),
                    "changes": git("status", "--short").splitlines()}
            self.send(json.dumps(info).encode(), "application/json")
        elif self.path.startswith("/stream"):
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                while True:
                    with frame_ready:
                        frame_ready.wait()
                        jpeg = frame
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/input":
            events.put(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            self.send(b"{}", "application/json")
        else:
            self.send_error(404)


def start_game():
    import arcade
    from constants import BACKGROUND, SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
    from menu_view import MenuView

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, visible=False)
    window.background_color = BACKGROUND
    window._enable_event_queue = False  # pyglet's event loop does this; we drive the loop ourselves
    window.show_view(MenuView())
    status["size"] = [SCREEN_WIDTH, SCREEN_HEIGHT]
    return window


def dispatch(window, event):
    import arcade
    x, y = event.get("x", 0), event.get("y", 0)
    if event["type"] == "move":
        window.dispatch_event("on_mouse_motion", x, y, 0, 0)
    elif event["type"] == "click":
        window.dispatch_event("on_mouse_press", x, y, arcade.MOUSE_BUTTON_LEFT, 0)
        window.dispatch_event("on_mouse_release", x, y, arcade.MOUSE_BUTTON_LEFT, 0)
    elif event["type"] == "key" and event.get("key") in KEYS:
        window.dispatch_event("on_key_press", getattr(arcade.key, KEYS[event["key"]]), 0)


def publish(jpeg):
    global frame
    with frame_ready:
        frame = jpeg
        frame_ready.notify_all()


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Live preview on http://localhost:{PORT}", flush=True)

    mtimes, checked = sources(), time.time()
    try:
        window = start_game()
    except Exception:
        status["error"], window = traceback.format_exc(), None

    last = time.time()
    while True:
        now = time.time()
        if now - checked > 0.5:
            checked = now
            if sources() != mtimes:
                print("Change detected, restarting", flush=True)
                while not Path(__file__).exists():  # e.g. mid branch switch
                    time.sleep(0.5)
                os.execv(sys.executable, [sys.executable, *sys.argv])  # server socket is closed on exec
        if window:
            try:
                import arcade
                while not events.empty():
                    dispatch(window, events.get())
                window.dispatch_event("on_update", now - last)  # reaches the view and its GUI widgets
                window.current_view.on_draw()
                buffer = io.BytesIO()
                arcade.get_image().convert("RGB").save(buffer, "JPEG", quality=85)
                publish(buffer.getvalue())
            except Exception:
                status["error"], window = traceback.format_exc(), None
        last = now
        time.sleep(max(0.0, 1 / FPS - (time.time() - now)))


if __name__ == "__main__":
    main()
