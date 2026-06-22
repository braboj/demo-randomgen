"""Shared pytest configuration.

Tests are tiered by directory and marked automatically so the test commands
stay simple:

- ``tests/`` (top level)      -> ``unit``        (fast, isolated)
- ``tests/integration/``      -> ``integration`` (live in-process app)
- ``tests/e2e/``              -> ``e2e``         (real container / browser)

The default run excludes ``e2e`` (see ``addopts`` in ``pyproject.toml``); run
the end-to-end tier explicitly with ``pytest -m e2e``.
"""

import os
from pathlib import Path

# Rate limiting is an operational concern, not part of the routing/contract
# behaviour the suite exercises. Default it OFF for the whole test session so the
# endpoint tests are never throttled; tests/integration/test_rate_limit.py opts
# back in for its own app. setdefault leaves an explicit host value untouched.
os.environ.setdefault('RANDOMGEN_RATELIMIT_ENABLED', 'false')


def pytest_collection_modifyitems(config, items):
    """Tag each collected test with a tier marker based on its directory."""

    for item in items:
        parts = Path(str(item.fspath)).parts
        if 'e2e' in parts:
            item.add_marker('e2e')
        elif 'integration' in parts:
            item.add_marker('integration')
        else:
            item.add_marker('unit')
