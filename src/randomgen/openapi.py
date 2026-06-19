"""Access to the RandomGen OpenAPI contract.

The contract is hand-authored in ``openapi.yaml`` next to this module and is the
single source of truth (design-first): the service serves it verbatim at
``/openapi.json`` and renders it as ReDoc at ``/docs`` (see
:mod:`randomgen.routing`). See ``docs/decisions/016-design-first-openapi.md``.

A unit test pins the spec's quantity limits and version to the live code
constants, and asserts every ``/api`` route is documented, so the contract and
the implementation cannot silently drift.
"""

from functools import lru_cache
from importlib import resources
from typing import Any

import yaml


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    """Load and parse the bundled OpenAPI contract.

    Returns:
        dict: The parsed OpenAPI 3.1 document. Cached after the first call;
        callers must treat the returned dict as read-only.

    """

    text = resources.files('randomgen').joinpath('openapi.yaml').read_text(encoding='utf-8')
    return yaml.safe_load(text)
