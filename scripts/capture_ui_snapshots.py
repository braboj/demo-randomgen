"""Capture the home-page UI snapshots used in docs/ui-snapshots.md.

Runs the real Flask app in-process on an ephemeral port and drives it with
Playwright (Chromium), writing one PNG per UI state into docs/assets/images/ui/.
Keeps the documentation screenshots reproducible instead of hand-captured.

Prerequisites (the e2e extra + the browser):

    pip install -e ".[e2e]"
    playwright install chromium

Run from anywhere:

    python scripts/capture_ui_snapshots.py
"""

from __future__ import annotations

import threading
from pathlib import Path

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from randomgen.app import create_app

OUT_DIR = Path(__file__).resolve().parent.parent / 'docs' / 'assets' / 'images' / 'ui'
DESKTOP = {'width': 1280, 'height': 900}
MOBILE = {'width': 390, 'height': 844}


def _serve():
    """Start the app on an ephemeral localhost port; return (base_url, server)."""

    server = make_server('127.0.0.1', 0, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f'http://127.0.0.1:{server.server_port}', server


def _generate(page):
    """Click Generate and wait for the results panel and bars to settle."""

    page.click('#generate')
    page.wait_for_selector('#results', state='visible')
    page.wait_for_selector('.bar-fill')
    page.wait_for_timeout(700)  # let the bar-fill width transition finish


def capture(base, browser):
    """Drive each UI state and write its screenshot."""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    page = browser.new_page(viewport=DESKTOP)

    # 01 — initial state (now showing the preset bar).
    page.goto(base)
    page.wait_for_selector('#controls')
    page.screenshot(path=str(OUT_DIR / '01_initial.png'))

    # 02 — v1 results with the built-in distribution.
    page.goto(base)
    page.fill('#quantity', '1000')
    _generate(page)
    page.screenshot(path=str(OUT_DIR / '02_v1_results.png'))

    # 03 — v2 with a custom 2-outcome distribution.
    page.goto(base)
    page.click("label[for='v2']")
    page.fill('#dist', '1:0.5,2:0.5')
    page.fill('#quantity', '500')
    _generate(page)
    page.screenshot(path=str(OUT_DIR / '03_v2_custom.png'))

    # 04 — error state from a malformed distribution.
    page.goto(base)
    page.fill('#dist', '1:0.5,2')
    page.click('#generate')
    page.wait_for_selector('#status.err', state='visible')
    page.screenshot(path=str(OUT_DIR / '04_error.png'))

    # 06 — a preset selected (the v0.9.0 feature): Bimodal active, dist filled.
    page.goto(base)
    page.click("button.preset:has-text('Bimodal')")
    page.wait_for_selector('button.preset.is-active')
    page.screenshot(path=str(OUT_DIR / '06_presets.png'))

    # 07 — dark theme (the v0.11.0 toggle), initial state.
    page.goto(base)
    page.click('#theme-toggle')
    page.wait_for_selector('html[data-theme="dark"]')
    page.wait_for_timeout(300)  # let the surface cross-fade settle
    page.screenshot(path=str(OUT_DIR / '07_dark.png'))

    # 05 — mobile / responsive layout (initial state).
    mobile = browser.new_page(viewport=MOBILE)
    mobile.goto(base)
    mobile.wait_for_selector('#controls')
    mobile.screenshot(path=str(OUT_DIR / '05_mobile.png'))


def main():
    """Serve the app, capture every snapshot, then shut down."""

    base, server = _serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                capture(base, browser)
            finally:
                browser.close()
    finally:
        server.shutdown()

    print(f'Wrote snapshots to {OUT_DIR}')


if __name__ == '__main__':
    main()
