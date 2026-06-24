from randomgen.domain.errors import (
    RandomGenEmptyError,
    RandomGenMaxError,
    RandomGenMinError,
    RandomGenMismatchError,
    RandomGenProbabilityNegativeError,
    RandomGenProbabilitySumError,
    RandomGenTypeError,
)
from randomgen.domain.histogram import Histogram
from randomgen.domain.hypothesis import ChiSquareTest

DEFAULT_NUMBERS = [-1, 0, 1, 2, 3]
DEFAULT_PROBABILITIES = [0.01, 0.3, 0.58, 0.1, 0.01]
MAX_NUMBERS = 10000

# Quantity generated when the `numbers` query parameter is omitted. A large
# default makes the Chi-Square quality report meaningful out of the box.
DEFAULT_QUANTITY = 1000


class RandomGenService:
    """Stateless RandomGen service.

    Stateless service logic for the RandomGen project, independent of the web
    framework. The distribution to sample from is supplied per request and
    defaults to the module-level ``DEFAULT_NUMBERS`` /
    ``DEFAULT_PROBABILITIES``. The instance holds no mutable state, so it is
    safe to share across requests, clients, and worker processes.

    """

    @staticmethod
    def validate_distribution(numbers, probabilities):
        """Validate a caller-supplied discrete distribution.

        Args:
            numbers: The distribution's outcomes (list or tuple).
            probabilities: The matching probabilities (list or tuple).

        Returns:
            tuple: The validated ``(numbers, probabilities)`` pair.

        Raises:
            RandomGenError: If the distribution is malformed (wrong type,
            empty, length mismatch, negative weight, or weights that do not
            sum to 1).

        """

        if not isinstance(numbers, (list, tuple)) or not isinstance(probabilities, (list, tuple)):
            raise RandomGenTypeError()

        elif not numbers or not probabilities:
            raise RandomGenEmptyError()

        elif len(numbers) != len(probabilities):
            raise RandomGenMismatchError()

        elif any(p < 0 for p in probabilities):
            raise RandomGenProbabilityNegativeError()

        elif round(sum(probabilities), 3) != 1:
            raise RandomGenProbabilitySumError()

        return numbers, probabilities

    def _draw_and_score(self, generator, quantity, numbers, probabilities):
        """Draw a sample from a built generator and score how well it fits.

        Args:
            generator: The (already validated) random number generator.
            quantity: The quantity of random numbers to generate.
            numbers: The distribution's outcomes, used for the expected
                histogram and the Chi-Square test.
            probabilities: The matching probabilities.

        Returns:
            dict: A dictionary containing the generated random numbers and the
            results of the Chi-Square test.

        """

        # Check if the amount is negative or zero
        if quantity <= 0:
            raise RandomGenMinError()

        # Check if the amount exceeds the maximum limit
        elif quantity > MAX_NUMBERS:
            raise RandomGenMaxError()

        # Generate random numbers
        random_numbers = [generator.next_num() for _ in range(quantity)]

        # Expected distribution
        expected = dict(zip(numbers, probabilities, strict=False))

        # Observed distribution
        observed = Histogram().set_numbers(random_numbers).calc()

        # Chi-Square test to check the quality of the random number generator
        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers(random_numbers)
            .set_expected_numbers(numbers)
            .set_expected_probabilities(probabilities)
            .validate()
            .calc()
        )

        # Prepare the response
        response = {
            'numbers': random_numbers,
            'quality': {
                'chi_square_test': {
                    # is_null() already returns a plain bool (or None when the
                    # test does not apply); pass it through so None serialises
                    # as JSON null rather than collapsing to False.
                    'is_null': hypothesis.is_null(),
                    'chi_square': hypothesis.chi_square,
                    'p_value': hypothesis.p_value,
                    'df': hypothesis.df,
                },
                'expected_histogram': expected,
                'observed_histogram': observed,
            },
        }

        # Return the response
        return response

    def generate(self, generator, quantity, values=None, probabilities=None):
        """Generate a scored sample using the given generator.

        Args:
            generator: The generator class to sample with (instantiated fresh
                per request, so the service stays stateless).
            quantity: The quantity of random numbers to generate.
            values: Optional distribution outcomes. Defaults to
                ``DEFAULT_NUMBERS`` when neither values nor probabilities are
                supplied.
            probabilities: Optional distribution weights. Defaults to
                ``DEFAULT_PROBABILITIES``.

        Returns:
            dict: A dictionary containing the generated random numbers and the
            results of the Chi-Square test.

        """

        # Use the built-in distribution unless the caller supplies one
        if values is None and probabilities is None:
            values = DEFAULT_NUMBERS
            probabilities = DEFAULT_PROBABILITIES

        # Otherwise validate the caller-supplied distribution
        else:
            values, probabilities = self.validate_distribution(
                values if values is not None else [],
                probabilities if probabilities is not None else [],
            )

        # Create the random number generator for this request
        rg = generator()
        rg.set_numbers(values)
        rg.set_probabilities(probabilities)
        rg.validate()

        # Draw the sample and score how well it fits
        return self._draw_and_score(
            generator=rg,
            quantity=quantity,
            numbers=values,
            probabilities=probabilities,
        )
