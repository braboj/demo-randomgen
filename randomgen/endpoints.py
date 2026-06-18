from randomgen.core import RandomGenV1, RandomGenV2
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

    This class implements the REST API logic for the RandomGen project. The
    implementation is not aware of the web framework that is being used. It
    performs the business logic and some checks before returning the results
    to the web framework.

    Attributes:
        config (dict): The configuration dict used by the API.

    """

    def __init__(self):

        self.config = {}

        # Set the configuration
        self.setup_config()

    def setup_config(self):
        """ Configure the Flask application using the default values.

        Returns:
            dict: The configuration dict after the change.

        """

        self.config['MAX_NUMBERS'] = MAX_NUMBERS
        self.config['NUMBERS'] = DEFAULT_NUMBERS
        self.config['PROBABILITIES'] = DEFAULT_PROBABILITIES

    def generate_random_numbers(self, randomgen, quantity):
        """ Generate random numbers using the given random number generator.

        Args:
            randomgen: The random number generator object.
            quantity: The quantity of random numbers to generate.

        Returns:
            dict: A dictionary containing the generated random numbers and the
            results of the Chi-Square test.
        """

        # Check if the amount is negative or zero
        if quantity <= 0:
            raise RandomGenMinError()

        # Check if the amount exceeds the maximum limit
        elif quantity > self.config['MAX_NUMBERS']:
            raise RandomGenMaxError()

        # Generate random numbers
        random_numbers = [randomgen.next_num() for _ in range(quantity)]

        # Expected distribution
        expected = dict(zip(
            self.config['NUMBERS'],
            self.config['PROBABILITIES'])
        )

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
            .set_expected_numbers(self.config['NUMBERS'])
            .set_expected_probabilities(self.config['PROBABILITIES'])
            .calc()
        )

        # Prepare the response
        response = {
            'numbers': random_numbers,
            "quality": {
                "chi_square_test": {
                    'is_null': int(hypothesis.is_null()),
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

            <p>Endpoints:</p>

            <ul>
                <li> GET /api/v1/randomgen?numbers=1000 </li>
                <li> GET /api/v2/randomgen?numbers=1000 </li>
                <li> POST /api/config {"numbers":[1, 2], "probabilities":[0.5, 0.5]}</li>
                <li> POST /api/reset </li>
            </ul>

            """
        )

        return body

    def randomgen_endpoint(self, randomgen_type, numbers):
        """ Generate random numbers using the given version of RandomGen.

        Args:
            randomgen_type: The concrete class of RandomGen to use.
            numbers: The quantity of random numbers to generate.

        Returns:
            dict: A dictionary containing the generated random numbers and the
            results of the Chi-Square test.
        """

        # Create the random number generator
        rg = (
            randomgen_type()
            .set_numbers(self.config['NUMBERS'])
            .set_probabilities(self.config['PROBABILITIES'])
            .validate()
        )

        # Generate random numbers
        return self.generate_random_numbers(randomgen=rg, quantity=numbers)

    def config_endpoint(self, numbers, probabilities):
        """ Configure the numbers and probabilities.

        Returns:
            dict: A dictionary containing the new numbers and probabilities.

        """

        if not isinstance(numbers, list) or not isinstance(probabilities, list):
            raise RandomGenTypeError()

        elif not numbers or not probabilities:
            raise RandomGenEmptyError()

        elif len(numbers) != len(probabilities):
            raise RandomGenMismatchError()

        elif any(p < 0 for p in probabilities):
            raise RandomGenProbabilityNegativeError()

        elif round(sum(probabilities), 3) != 1:
            raise RandomGenProbabilitySumError()

        self.config['NUMBERS'] = numbers
        self.config['PROBABILITIES'] = probabilities

        return {
            'numbers': self.config['NUMBERS'],
            'probabilities': self.config['PROBABILITIES']
        }

    def reset_endpoint(self):
        """ Reset the configuration to the default values.

        Returns:
            dict: A dictionary containing the default numbers and probabilities.

        """

        self.setup_config()

        return {
            'numbers': self.config['NUMBERS'],
            'probabilities': self.config['PROBABILITIES']
        }


###############################################################################
# Example
###############################################################################

if __name__ == "__main__":

    from flask import Flask, jsonify, request

    # Create the RandomGen REST API
    api = RandomGenRestApi()

    # Create the Flask application
    app = Flask(__name__)

    # Home endpoint
    @app.route('/')
    def home():
        return api.home_endpoint()

    # RandomGen V1 endpoint
    @app.get('/api/v1/randomgen')
    def randomgen_v1():
        numbers = int(request.args.get('numbers', 1000))
        return jsonify(api.randomgen_endpoint(RandomGenV1, numbers))

    # RandomGen V2 endpoint
    @app.get('/api/v2/randomgen')
    def randomgen_v2():
        numbers = int(request.args.get('numbers', 1000))
        return jsonify(api.randomgen_endpoint(RandomGenV2, numbers))

    # Config endpoint
    @app.post('/api/config')
    def config():
        data = request.get_json()
        numbers = data.get('numbers')
        probabilities = data.get('probabilities')
        return jsonify(api.config_endpoint(numbers, probabilities))

    # Reset endpoint
    @app.post('/api/reset')
    def reset():
        return jsonify(api.reset_endpoint())

    # Run the application
    app.run(host='localhost', port=8080)
