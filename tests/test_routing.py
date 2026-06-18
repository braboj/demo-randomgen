# encoding: utf-8
import pytest
import requests
import threading

import randomgen.routing as routing


@pytest.fixture(autouse=True, scope='module')
def webserver():
    """Run the web server as a background thread."""

    app = threading.Thread(target=routing.app.run)
    app.daemon = True
    app.start()
    yield app


###############################################################################

class TestRestApiRouting(object):
    """ Test the REST API routing."""

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

        for num in (-1, 0, 10001,):
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

        for num in (-1, 0, 10001,):
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

    def test_endpoint_health(self):
        """The health check returns 200 with an ok status."""

        # Endpoint URL
        url = self.base_url + '/health'

        # Send a GET request
        response = requests.get(url)

        # Check the response
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


if __name__ == "__main__":
    pytest.main()
