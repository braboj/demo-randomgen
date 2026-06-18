from randomgen.hypothesis import ChiSquareTest
from randomgen.histogram import Histogram

from randomgen.errors import (
    RandomGenMinError,
    RandomGenMaxError,
    RandomGenTypeError,
    RandomGenEmptyError,
    RandomGenMismatchError,
    RandomGenProbabilitySumError,
    RandomGenProbabilityNegativeError,
)

DEFAULT_NUMBERS = [-1, 0, 1, 2, 3]
DEFAULT_PROBABILITIES = [0.01, 0.3, 0.58, 0.1, 0.01]
MAX_NUMBERS = 10000


class RandomGenRestApi(object):
    """Random Number Generator REST API.

    Stateless service logic for the RandomGen project, independent of the web
    framework. The distribution to sample from is supplied per request and
    defaults to the module-level ``DEFAULT_NUMBERS`` /
    ``DEFAULT_PROBABILITIES``. The instance holds no mutable state, so it is
    safe to share across requests, clients, and worker processes.

    """

    @staticmethod
    def validate_distribution(numbers, probabilities):
        """ Validate a caller-supplied discrete distribution.

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

        if not isinstance(numbers, (list, tuple)) \
                or not isinstance(probabilities, (list, tuple)):
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

    def generate_random_numbers(self, randomgen, quantity, numbers,
                                probabilities):
        """ Generate random numbers and score them against a distribution.

        Args:
            randomgen: The (already validated) random number generator.
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
        random_numbers = [randomgen.next_num() for _ in range(quantity)]

        # Expected distribution
        expected = dict(zip(numbers, probabilities))

        # Observed distribution
        observed = (
            Histogram()
            .set_numbers(random_numbers)
            .calc()
        )

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
            "quality": {
                "chi_square_test": {
                    'is_null': bool(hypothesis.is_null()),
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

    @staticmethod
    def home_endpoint():
        """ Home endpoint.

        Returns:
            str: The HTML body of the home page.
        """

        body = (
            """
            <h1>Random Number Generator API</h1>

            Author: Branimir Georgiev

            <p>
            The fairness of the random number generator is tested using the
            Chi-Square test. Larger numbers of generated random numbers will
            result in a more accurate test.
            </p>

            <p>
            Each request is self-contained. The distribution defaults to a
            built-in one and can be overridden per request, either with a
            single <code>dist</code> parameter of
            <code>value:probability</code> pairs or with repeated
            <code>value</code> and <code>probability</code> parameters; the
            service keeps no configuration between requests.
            </p>

            <p>Endpoints:</p>

            <ul>
                <li> GET /api/v1/randomgen?numbers=1000 </li>
                <li> GET /api/v2/randomgen?numbers=1000 </li>
                <li> GET /api/v1/randomgen?numbers=1000&amp;dist=1:0.5,2:0.5 </li>
                <li> GET /api/v1/randomgen?numbers=1000&amp;value=1&amp;value=2&amp;probability=0.5&amp;probability=0.5 </li>
            </ul>

            """
        )

        return body

    def randomgen_endpoint(self, randomgen_type, quantity,
                           values=None, probabilities=None):
        """ Generate random numbers using the given version of RandomGen.

        Args:
            randomgen_type: The concrete class of RandomGen to use.
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
        rg = (
            randomgen_type()
            .set_numbers(values)
            .set_probabilities(probabilities)
            .validate()
        )

        # Generate random numbers
        return self.generate_random_numbers(
            randomgen=rg,
            quantity=quantity,
            numbers=values,
            probabilities=probabilities,
        )
