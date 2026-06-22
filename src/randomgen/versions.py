"""The API version registry.

Maps each API generation to the generator class it samples with. This is the
single place a new generation is registered: the application factory builds one
blueprint per entry (see :func:`randomgen.blueprints.api.make_api_blueprint`).

Keeping the mapping here — rather than importing the generator classes in the
route layer — keeps version selection an API-layer concern while leaving the
blueprints free of any dependency on :mod:`randomgen.core`.
"""

from randomgen.core import RandomGenABC, RandomGenV1, RandomGenV2

# Each generation shares one contract (identical parameters, validation, and
# response shape) and differs only by the generator. Adding a generation is a
# one-line edit here; a generation whose *contract* diverges instead graduates
# to its own blueprint module (see docs/decisions/022).
API_VERSIONS: dict[str, type[RandomGenABC]] = {
    'v1': RandomGenV1,
    'v2': RandomGenV2,
}
