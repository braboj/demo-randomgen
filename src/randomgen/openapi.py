"""Access to the RandomGen OpenAPI contract.

The contract is hand-authored in ``openapi.yaml`` next to this module and is the
single source of truth (design-first): the service serves it verbatim at
``/openapi.json`` and renders it as ReDoc at ``/docs`` (see
:mod:`randomgen.blueprints.web`). See ``docs/decisions/016-design-first-openapi.md``.

A unit test pins the spec's quantity limits to the live code constants and
asserts every ``/api`` route is documented, so the contract and the
implementation cannot silently drift.
"""

from functools import lru_cache
from importlib import resources
from typing import Any

import yaml


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    """Load and parse the bundled OpenAPI contract.

    ``info.version`` is the contract's own version (the API generation), set by
    hand in ``openapi.yaml`` and maintained independently of the package version
    in ``pyproject.toml`` — see ``docs/decisions/021-openapi-contract-version.md``.

    Returns:
        dict: The parsed OpenAPI 3.1 document. Cached after the first call;
        callers must treat the returned dict as read-only.

    """

    text = resources.files('randomgen').joinpath('openapi.yaml').read_text(encoding='utf-8')
    spec: dict[str, Any] = yaml.safe_load(text)
    return spec
