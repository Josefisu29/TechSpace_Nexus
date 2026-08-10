from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

import uvicorn


def open_frontend(frontend_path: Path) -> None:
    time.sleep(1.0)
    webbrowser.open(frontend_path.resolve().as_uri())


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    frontend_url = base / "frontend" / "index.html"

    browser_thread = threading.Thread(target=open_frontend, args=(frontend_url,), daemon=True)
    browser_thread.start()

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
