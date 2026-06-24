"""Shared validation primitives for the domain layer.

The generators, the histogram, and the hypothesis test all require the same
shape for their numeric inputs: a non-empty iterable of real numbers. This
module holds that single check so the rule lives in one place instead of being
re-implemented (with subtle ordering drift) in each ``validate_*`` method.
"""

from randomgen.domain.errors import RandomGenEmptyError, RandomGenTypeError


def validate_number_iterable(values):
    """Validate that ``values`` is a non-empty iterable of real numbers.

    A ``dict`` is rejected because iterating it yields keys, not the intended
    values; a ``set`` is accepted (the callers that forbid it apply that rule
    themselves). ``bool`` is a subclass of ``int`` and is accepted, matching the
    historical behaviour.

    Args:
        values: The candidate iterable of numbers.

    Returns:
        The validated ``values``, unchanged, for call chaining.

    Raises:
        RandomGenTypeError: If ``values`` is ``None``, a ``dict``, not iterable,
            or contains a non-numeric element.
        RandomGenEmptyError: If ``values`` is an empty iterable.

    """

    if (
        values is None
        or isinstance(values, dict)
        or not hasattr(values, '__iter__')
        or not all(isinstance(value, (int, float)) for value in values)
    ):
        raise RandomGenTypeError()

    if not values:
        raise RandomGenEmptyError()

    return values
