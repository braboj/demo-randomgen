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

Rate limiting is disabled for the app under test: schemathesis fires many
generated requests at the same endpoint, which would otherwise trip the limit
and make conformance depend on request timing. The limit itself is proven in
``test_rate_limit.py``; here the contract is what matters.
"""

import os

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


def _app_without_rate_limiting():
    """Build the app with the rate limiter disabled, leaving the env untouched.

    ``Config`` reads ``RANDOMGEN_RATELIMIT_ENABLED`` when ``create_app`` runs, so
    the flag is set only around that call and then restored — other test modules
    (which need limiting on) see the original environment.
    """

    key = 'RANDOMGEN_RATELIMIT_ENABLED'
    previous = os.environ.get(key)
    os.environ[key] = 'false'
    try:
        return create_app()
    finally:
        if previous is None:
            del os.environ[key]
        else:
            os.environ[key] = previous


schema = schemathesis.openapi.from_wsgi('/openapi.json', _app_without_rate_limiting())

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
