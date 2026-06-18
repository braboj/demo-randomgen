import threading

import pytest
import requests

import randomgen.routing as routing
from randomgen.app import create_app
from randomgen.errors import RandomGenDistFormatError


@pytest.fixture(autouse=True, scope='module')
def webserver():
    """Run the web server as a background thread."""

    app = threading.Thread(target=create_app().run)
    app.daemon = True
    app.start()
    yield app


###############################################################################


class TestRestApiRouting:
    """Test the REST API routing."""

    @classmethod
    def setup_class(cls):
        """Set up the base URL."""

        cls.base_url = 'http://127.0.0.1:5000'

    def test_endpoint_api_v1_randomgen_pos(self):
        """Test the /api/v1/randomgen endpoint with positive numbers."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        for num in (1, 1000, 10000):
            # Query parameters
            params = {'numbers': num}

            # Send a GET request
            response = requests.get(url, params=params)

            # Check the response
            assert response.status_code == 200

    def test_endpoint_api_v1_randomgen_neg(self):
        """Test the /api/v1/randomgen endpoint with negative numbers."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        for num in (
            -1,
            0,
            10001,
        ):
            # Query parameters
            params = {'numbers': num}

            # Send a GET request
            response = requests.get(url, params=params)

            # Check the response
            assert response.status_code == 400

    def test_endpoint_api_v2_randomgen_pos(self):
        """Test the /api/v2/randomgen endpoint with positive numbers."""

        # Endpoint URL
        url = self.base_url + '/api/v2/randomgen'

        for num in (1, 10000):
            # Query parameters
            params = {'numbers': num}

            # Send a GET request
            response = requests.get(url, params=params)

            # Check the response
            assert response.status_code == 200

    def test_endpoint_api_v2_randomgen_neg(self):
        """Test the /api/v2/randomgen endpoint with negative numbers."""

        # Endpoint URL
        url = self.base_url + '/api/v2/randomgen'

        for num in (
            -1,
            0,
            10001,
        ):
            # Query parameters
            params = {'numbers': num}

            # Send a GET request
            response = requests.get(url, params=params)

            # Check the response
            assert response.status_code == 400

    def test_endpoint_api_v1_randomgen_custom_distribution(self):
        """A per-request distribution is honored via query parameters."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        # Quantity plus a custom distribution over {1, 2, 3}
        params = {
            'numbers': 1000,
            'value': [1, 2, 3],
            'probability': [0.2, 0.2, 0.6],
        }

        # Send a GET request
        response = requests.get(url, params=params)
        response_json = response.json()

        # Check the response
        assert response.status_code == 200
        assert set(response_json['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_api_v1_randomgen_custom_distribution_invalid(self):
        """A malformed per-request distribution returns 400."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        # Mismatched lengths between values and probabilities
        params = {
            'numbers': 100,
            'value': [1, 2, 3],
            'probability': [0.2, 0.2],
        }

        # Send a GET request
        response = requests.get(url, params=params)

        # Check the response
        assert response.status_code == 400

    def test_endpoint_api_v1_randomgen_invalid_quantity(self):
        """A non-integer `numbers` parameter returns 400, not a coerced 200."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        # Send a GET request with a non-integer quantity
        response = requests.get(url, params={'numbers': 'abc'})

        # Check the response
        assert response.status_code == 400

    def test_endpoint_v1_dist_pairs_valid_returns_200(self):
        """The `dist` value:probability shorthand is honored on v1."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        # Custom distribution over {1, 2, 3} as value:probability pairs
        params = {'numbers': 1000, 'dist': '1:0.2,2:0.2,3:0.6'}

        # Send a GET request
        response = requests.get(url, params=params)
        response_json = response.json()

        # Check the response
        assert response.status_code == 200
        assert set(response_json['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_v2_dist_pairs_valid_returns_200(self):
        """The `dist` shorthand works on v2 the same way as on v1."""

        # Endpoint URL
        url = self.base_url + '/api/v2/randomgen'

        # Custom distribution over {1, 2, 3} as value:probability pairs
        params = {'numbers': 1000, 'dist': '1:0.2,2:0.2,3:0.6'}

        # Send a GET request
        response = requests.get(url, params=params)
        response_json = response.json()

        # Check the response
        assert response.status_code == 200
        assert set(response_json['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_v1_dist_malformed_returns_400(self):
        """A `dist` item without a value:probability separator returns 400."""

        # Endpoint URL
        url = self.base_url + '/api/v1/randomgen'

        # The second item is missing its ':' separator
        params = {'numbers': 100, 'dist': '1:0.5,2'}

        # Send a GET request
        response = requests.get(url, params=params)

        # Check the response
        assert response.status_code == 400

    def test_endpoint_health(self):
        """The health check returns 200 with an ok status."""

        # Endpoint URL
        url = self.base_url + '/health'

        # Send a GET request
        response = requests.get(url)

        # Check the response
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


def test_parse_dist_pairs_valid_unzips_to_lists():
    """A well-formed `dist` string parses into parallel float lists."""

    values, probabilities = routing.parse_dist_pairs('-1:0.01,0:0.3,1:0.69')

    assert values == [-1.0, 0.0, 1.0]
    assert probabilities == [0.01, 0.3, 0.69]


def test_parse_dist_pairs_missing_separator_raises():
    """A `dist` item without a ':' separator raises a format error."""

    with pytest.raises(RandomGenDistFormatError):
        routing.parse_dist_pairs('1:0.5,2')


def test_parse_dist_pairs_non_numeric_raises():
    """A `dist` item with a non-numeric side raises a format error."""

    with pytest.raises(RandomGenDistFormatError):
        routing.parse_dist_pairs('1:half,2:0.5')


if __name__ == '__main__':
    pytest.main()
