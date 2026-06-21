"""Access to the RandomGen OpenAPI contract.

The contract is hand-authored in ``openapi.yaml`` next to this module and is the
single source of truth (design-first): the service serves it verbatim at
``/openapi.json`` and renders it as ReDoc at ``/docs`` (see
:mod:`randomgen.routing`). See ``docs/decisions/016-design-first-openapi.md``.

A unit test pins the spec's quantity limits to the live code constants and
asserts every ``/api`` route is documented; the version is injected from the
installed package (see :func:`load_spec`). Together these stop the contract and
the implementation from silently drifting.
"""

from functools import lru_cache
from importlib import resources
from typing import Any

import yaml

from randomgen import __version__


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    """Load and parse the bundled OpenAPI contract.

    The ``info.version`` field is overwritten with the installed package version
    (:data:`randomgen.__version__`), so the served contract always matches the
    release and ``pyproject.toml`` stays the single source of the version — no
    hand-edited copy in the YAML.

    Returns:
        dict: The parsed OpenAPI 3.1 document. Cached after the first call;
        callers must treat the returned dict as read-only.

    """

    text = resources.files('randomgen').joinpath('openapi.yaml').read_text(encoding='utf-8')
    spec: dict[str, Any] = yaml.safe_load(text)
    spec['info']['version'] = __version__
    return spec
