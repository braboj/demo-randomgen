import pytest

import randomgen.routing as routing
from randomgen.app import create_app
from randomgen.errors import RandomGenDistFormatError

###############################################################################


class TestRestApiRouting:
    """Test the REST API routing via the in-process Flask test client.

    Driving the app with ``test_client()`` exercises the full WSGI stack
    (routing, handlers, error boundary) without binding a real socket, so the
    suite cannot race a background server coming up or collide on a fixed port.
    """

    @classmethod
    def setup_class(cls):
        """Build a test client over the application factory.

        The service holds no mutable state, so a single client shared across
        the class is safe.
        """

        cls.client = create_app().test_client()

    def test_endpoint_api_v1_randomgen_pos(self):
        """Test the /api/v1/randomgen endpoint with positive numbers."""

        for num in (1, 1000, 10000):
            response = self.client.get('/api/v1/randomgen', query_string={'numbers': num})
            assert response.status_code == 200

    def test_endpoint_api_v1_randomgen_neg(self):
        """Test the /api/v1/randomgen endpoint with negative numbers."""

        for num in (-1, 0, 10001):
            response = self.client.get('/api/v1/randomgen', query_string={'numbers': num})
            assert response.status_code == 400

    def test_endpoint_api_v2_randomgen_pos(self):
        """Test the /api/v2/randomgen endpoint with positive numbers."""

        for num in (1, 10000):
            response = self.client.get('/api/v2/randomgen', query_string={'numbers': num})
            assert response.status_code == 200

    def test_endpoint_api_v2_randomgen_neg(self):
        """Test the /api/v2/randomgen endpoint with negative numbers."""

        for num in (-1, 0, 10001):
            response = self.client.get('/api/v2/randomgen', query_string={'numbers': num})
            assert response.status_code == 400

    def test_endpoint_api_v1_randomgen_custom_distribution(self):
        """A per-request distribution is honored via query parameters."""

        # Quantity plus a custom distribution over {1, 2, 3}
        params = {
            'numbers': 1000,
            'value': [1, 2, 3],
            'probability': [0.2, 0.2, 0.6],
        }

        response = self.client.get('/api/v1/randomgen', query_string=params)

        assert response.status_code == 200
        assert set(response.get_json()['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_api_v1_randomgen_custom_distribution_invalid(self):
        """A malformed per-request distribution returns 400."""

        # Mismatched lengths between values and probabilities
        params = {
            'numbers': 100,
            'value': [1, 2, 3],
            'probability': [0.2, 0.2],
        }

        response = self.client.get('/api/v1/randomgen', query_string=params)

        assert response.status_code == 400

    def test_endpoint_api_v1_randomgen_invalid_quantity(self):
        """A non-integer `numbers` parameter returns 400, not a coerced 200."""

        response = self.client.get('/api/v1/randomgen', query_string={'numbers': 'abc'})

        assert response.status_code == 400

    def test_endpoint_v1_dist_pairs_valid_returns_200(self):
        """The `dist` value:probability shorthand is honored on v1."""

        # Custom distribution over {1, 2, 3} as value:probability pairs
        params = {'numbers': 1000, 'dist': '1:0.2,2:0.2,3:0.6'}

        response = self.client.get('/api/v1/randomgen', query_string=params)

        assert response.status_code == 200
        assert set(response.get_json()['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_v2_dist_pairs_valid_returns_200(self):
        """The `dist` shorthand works on v2 the same way as on v1."""

        # Custom distribution over {1, 2, 3} as value:probability pairs
        params = {'numbers': 1000, 'dist': '1:0.2,2:0.2,3:0.6'}

        response = self.client.get('/api/v2/randomgen', query_string=params)

        assert response.status_code == 200
        assert set(response.get_json()['numbers']) <= {1.0, 2.0, 3.0}

    def test_endpoint_v1_dist_malformed_returns_400(self):
        """A `dist` item without a value:probability separator returns 400."""

        # The second item is missing its ':' separator
        params = {'numbers': 100, 'dist': '1:0.5,2'}

        response = self.client.get('/api/v1/randomgen', query_string=params)

        assert response.status_code == 400

    def test_endpoint_health(self):
        """The health check returns 200 with an ok status."""

        response = self.client.get('/health')

        assert response.status_code == 200
        assert response.get_json() == {'status': 'ok'}


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


def test_home_page_renders_template():
    """The home route renders the UI template with the expected anchors."""

    client = create_app().test_client()
    response = client.get('/')
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'text/html' in response.content_type
    assert '<form id="controls"' in body
    assert 'id="chart"' in body
    # The built-in distribution is injected so the page works out of the box.
    assert '-1:0.01,0:0.3,1:0.58,2:0.1,3:0.01' in body
    # Jinja must have rendered url_for(), not left it literal.
    assert 'url_for' not in body
    assert '/static/css/style.css' in body
    assert '/static/js/app.js' in body


def test_home_page_serves_static_assets():
    """The CSS and JS the page references are served by the app."""

    client = create_app().test_client()

    assert client.get('/static/css/style.css').status_code == 200
    assert client.get('/static/js/app.js').status_code == 200


def test_home_page_offers_distribution_presets():
    """The home page exposes one-click preset distributions on the form."""

    client = create_app().test_client()
    body = client.get('/').get_data(as_text=True)

    assert 'class="presets"' in body
    # Five labelled presets, each carrying a data-dist the JS applies.
    assert body.count('class="preset"') == 5
    for label in ('Uniform', 'Normal', 'Skewed', 'Bimodal', 'Near-degenerate'):
        assert f'>{label}</button>' in body
    # The uniform preset is a well-formed value:probability distribution.
    assert 'data-dist="1:0.2,2:0.2,3:0.2,4:0.2,5:0.2"' in body
    # Normal = symmetric binomial B(4, 0.5), the discrete bell; weights sum to 1.
    assert 'data-dist="1:0.0625,2:0.25,3:0.375,4:0.25,5:0.0625"' in body


def test_home_page_offers_a_theme_toggle():
    """The home page ships a theme toggle and seeds the theme before paint."""

    client = create_app().test_client()
    body = client.get('/').get_data(as_text=True)

    assert 'id="theme-toggle"' in body
    # The no-flash head script picks the theme from storage or the OS setting.
    assert "localStorage.getItem('randomgen-theme')" in body
    assert 'prefers-color-scheme: dark' in body


def test_home_page_offers_a_csv_download():
    """The results section offers a CSV download of the generated sample."""

    client = create_app().test_client()
    body = client.get('/').get_data(as_text=True)

    assert 'id="download-csv"' in body


def test_home_page_footer_links_to_api_docs():
    """The footer links to the interactive API docs (ReDoc) page."""

    client = create_app().test_client()
    body = client.get('/').get_data(as_text=True)

    assert '>API docs</a>' in body
    assert 'href="/docs"' in body


if __name__ == '__main__':
    pytest.main()
