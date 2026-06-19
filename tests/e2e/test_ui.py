"""End-to-end test: drive the Jinja home-page UI in a real browser.

Uses pytest-playwright's ``page`` fixture against the in-process ``live_server``
(see ``conftest.py``). Marked ``e2e`` automatically; run with ``pytest -m e2e``
after ``playwright install chromium``.
"""

import pytest

# Skip cleanly when Playwright is not installed (e.g. the default fast gate).
pytest.importorskip('playwright')

from playwright.sync_api import expect  # noqa: E402

DEFAULT_DIST = '-1:0.01,0:0.3,1:0.58,2:0.1,3:0.01'


def test_home_page_loads_with_defaults(page, live_server):
    """The page renders the form pre-filled with the built-in distribution."""

    page.goto(live_server)

    expect(page).to_have_title('RandomGen — discrete distribution sampler')
    expect(page.locator('#controls')).to_be_visible()
    expect(page.locator('#dist')).to_have_value(DEFAULT_DIST)
    # Results are hidden until the first generation.
    expect(page.locator('#results')).to_be_hidden()


def test_generate_renders_verdict_and_histogram(page, live_server):
    """Submitting the form calls the API and renders the verdict + bars."""

    page.goto(live_server)
    page.fill('#quantity', '300')
    page.click('#generate')

    # The results panel reveals once the API responds.
    expect(page.locator('#results')).to_be_visible()
    expect(page.locator('#verdict .badge')).to_be_visible()
    # Default distribution has 5 categories -> 5 rows x (expected + observed).
    expect(page.locator('.bar-fill')).to_have_count(10)


def test_v2_with_custom_distribution(page, live_server):
    """Switching to v2 and a 2-outcome distribution renders four bars."""

    page.goto(live_server)
    page.click("label[for='v2']")  # the radio itself is visually hidden
    page.fill('#dist', '1:0.5,2:0.5')
    page.fill('#quantity', '200')
    page.click('#generate')

    expect(page.locator('#results')).to_be_visible()
    expect(page.locator('.bar-fill')).to_have_count(4)


def test_preset_populates_distribution_and_generates(page, live_server):
    """Clicking a preset fills the distribution field, then generation works."""

    page.goto(live_server)
    page.click("button.preset:has-text('Uniform')")

    # The preset's distribution lands in the field and is marked active.
    expect(page.locator('#dist')).to_have_value('1:0.2,2:0.2,3:0.2,4:0.2,5:0.2')
    expect(page.locator("button.preset:has-text('Uniform')")).to_have_class('preset is-active')

    page.fill('#quantity', '300')
    page.click('#generate')

    expect(page.locator('#results')).to_be_visible()
    # The uniform preset has 5 categories -> 5 rows x (expected + observed).
    expect(page.locator('.bar-fill')).to_have_count(10)


def test_invalid_distribution_shows_error(page, live_server):
    """A malformed distribution surfaces the API error in the status line."""

    page.goto(live_server)
    page.fill('#dist', '1:0.5,2')  # missing the second probability
    page.click('#generate')

    expect(page.locator('#status.err')).to_be_visible()
    expect(page.locator('#results')).to_be_hidden()
