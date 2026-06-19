"""Contract tests: the running service must conform to the OpenAPI contract.

Schemathesis loads the served spec (the hand-authored ``openapi.yaml``) and
drives generated requests against the in-process app, checking every response
against the documented status codes and schemas. This is what keeps the
design-first contract honest: the implementation cannot quietly diverge from
the spec without a test failing.

Only the conformance checks are enabled — responses must not be server errors
and must match the documented status code, content type, and schema. The more
opinionated HTTP-hygiene checks (e.g. ``Allow`` headers on unsupported methods)
are out of scope for a contract test.
"""

import pytest

# Contract tests need schemathesis (in the `test`/`dev` extras, not `e2e`).
# Skip the whole module when it is absent so the e2e job — which collects
# every test module before deselecting by marker — does not error on import.
schemathesis = pytest.importorskip('schemathesis')

from hypothesis import settings
from schemathesis.checks import not_a_server_error
from schemathesis.specs.openapi.checks import (
    content_type_conformance,
    response_schema_conformance,
    status_code_conformance,
)

from randomgen.app import create_app

schema = schemathesis.openapi.from_wsgi('/openapi.json', create_app())

CONTRACT_CHECKS = [
    not_a_server_error,
    status_code_conformance,
    content_type_conformance,
    response_schema_conformance,
]


@schema.parametrize()
@settings(max_examples=25, deadline=None)
def test_app_conforms_to_contract(case):
    """Every generated request gets a documented, schema-valid response."""

    case.call_and_validate(checks=CONTRACT_CHECKS)
