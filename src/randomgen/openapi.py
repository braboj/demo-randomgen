"""OpenAPI 3.1 description of the RandomGen HTTP API.

The specification is built in code from the same constants the service uses
(version, default quantity, maximum quantity), so it tracks the implementation
instead of being maintained as a separate document. It is served as JSON at
``/openapi.json`` and rendered interactively at ``/docs`` (see
:mod:`randomgen.routing`).

A unit test asserts that every ``/api`` route on the blueprint appears in the
spec, so a new or renamed endpoint cannot silently fall out of sync.
"""

from typing import Any

# Reusable component schemas, referenced from the operation responses.
_SCHEMAS: dict[str, Any] = {
    'Error': {
        'type': 'object',
        'description': 'The error envelope returned for any failed request.',
        'properties': {
            'error': {'type': 'string', 'description': 'Human-readable message.'},
        },
        'required': ['error'],
    },
    'ChiSquareTest': {
        'type': 'object',
        'description': 'Chi-Square goodness-of-fit result for the sample.',
        'properties': {
            'is_null': {
                'type': 'boolean',
                'description': (
                    'True when the null hypothesis (the sample matches the '
                    'distribution) is not rejected.'
                ),
            },
            'chi_square': {'type': 'number', 'description': 'The chi-square statistic.'},
            'p_value': {'type': 'number', 'description': 'The test p-value.'},
            'df': {'type': 'integer', 'description': 'Degrees of freedom.'},
        },
    },
    'Quality': {
        'type': 'object',
        'description': 'Quality report comparing the sample to the distribution.',
        'properties': {
            'chi_square_test': {'$ref': '#/components/schemas/ChiSquareTest'},
            'expected_histogram': {
                'type': 'object',
                'description': 'Expected value -> probability map.',
                'additionalProperties': {'type': 'number'},
            },
            'observed_histogram': {
                'type': 'object',
                'description': 'Observed value -> frequency map for the sample.',
                'additionalProperties': {'type': 'number'},
            },
        },
    },
    'RandomGenResponse': {
        'type': 'object',
        'description': 'A generated sample and its quality report.',
        'properties': {
            'numbers': {
                'type': 'array',
                'description': 'The generated sample.',
                'items': {'type': 'number'},
            },
            'quality': {'$ref': '#/components/schemas/Quality'},
        },
    },
    'Health': {
        'type': 'object',
        'properties': {'status': {'type': 'string', 'examples': ['ok']}},
    },
}


def _randomgen_parameters(default_quantity: int, max_numbers: int) -> list[dict[str, Any]]:
    """Build the shared query parameters for the randomgen operations.

    Args:
        default_quantity: Quantity generated when ``numbers`` is omitted.
        max_numbers: The maximum quantity accepted in a single request.

    Returns:
        list: A fresh list of OpenAPI parameter objects.

    """

    return [
        {
            'name': 'numbers',
            'in': 'query',
            'required': False,
            'description': (
                f'How many numbers to generate (1..{max_numbers}). '
                f'Defaults to {default_quantity} when omitted.'
            ),
            'schema': {
                'type': 'integer',
                'default': default_quantity,
                'minimum': 1,
                'maximum': max_numbers,
            },
        },
        {
            'name': 'dist',
            'in': 'query',
            'required': False,
            'description': (
                'Distribution as comma-separated value:probability pairs, e.g. '
                '`-1:0.01,0:0.3,1:0.58,2:0.1,3:0.01`. Takes precedence over the '
                '`value`/`probability` parameters; probabilities must sum to 1.'
            ),
            'schema': {'type': 'string'},
            'example': '1:0.2,2:0.2,3:0.6',
        },
        {
            'name': 'value',
            'in': 'query',
            'required': False,
            'description': 'Legacy: repeated outcomes, paired by position with `probability`.',
            'schema': {'type': 'array', 'items': {'type': 'number'}},
            'style': 'form',
            'explode': True,
        },
        {
            'name': 'probability',
            'in': 'query',
            'required': False,
            'description': 'Legacy: repeated weights, paired by position with `value`.',
            'schema': {'type': 'array', 'items': {'type': 'number'}},
            'style': 'form',
            'explode': True,
        },
    ]


def _randomgen_operation(
    summary: str, description: str, default_quantity: int, max_numbers: int
) -> dict[str, Any]:
    """Build the GET operation object for one randomgen endpoint.

    Args:
        summary: Short operation summary.
        description: Longer description (the sampling algorithm).
        default_quantity: Quantity generated when ``numbers`` is omitted.
        max_numbers: The maximum quantity accepted in a single request.

    Returns:
        dict: An OpenAPI operation object.

    """

    return {
        'summary': summary,
        'description': description,
        'parameters': _randomgen_parameters(default_quantity, max_numbers),
        'responses': {
            '200': {
                'description': 'A generated sample and its Chi-Square quality report.',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/RandomGenResponse'},
                    },
                },
            },
            '400': {
                'description': 'Invalid quantity or malformed distribution.',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'},
                    },
                },
            },
        },
    }


def build_spec(version: str, default_quantity: int, max_numbers: int) -> dict[str, Any]:
    """Build the OpenAPI 3.1 document for the RandomGen API.

    Args:
        version: The package version, used as the spec ``info.version``.
        default_quantity: Quantity generated when ``numbers`` is omitted.
        max_numbers: The maximum quantity accepted in a single request.

    Returns:
        dict: The OpenAPI document, ready to serialize as JSON.

    """

    return {
        'openapi': '3.1.0',
        'info': {
            'title': 'RandomGen API',
            'version': version,
            'description': (
                'Generate random numbers from a configurable discrete distribution '
                'and score the sample with a Chi-Square goodness-of-fit test. '
                '`/api/v1` and `/api/v2` are interchangeable and differ only in the '
                'sampling algorithm.'
            ),
        },
        'paths': {
            '/api/v1/randomgen': {
                'get': _randomgen_operation(
                    'Generate numbers (v1)',
                    'Sampling via manual inverse-CDF over `random.random()`.',
                    default_quantity,
                    max_numbers,
                ),
            },
            '/api/v2/randomgen': {
                'get': _randomgen_operation(
                    'Generate numbers (v2)',
                    'Sampling via `random.choices`.',
                    default_quantity,
                    max_numbers,
                ),
            },
            '/health': {
                'get': {
                    'summary': 'Liveness check',
                    'description': 'Returns 200 when the service can handle requests.',
                    'responses': {
                        '200': {
                            'description': 'The service is healthy.',
                            'content': {
                                'application/json': {
                                    'schema': {'$ref': '#/components/schemas/Health'},
                                },
                            },
                        },
                    },
                },
            },
        },
        'components': {'schemas': _SCHEMAS},
    }
