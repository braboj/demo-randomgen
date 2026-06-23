import pytest

from randomgen.domain.core import RandomGenV1, RandomGenV2
from randomgen.domain.errors import (
    RandomGenEmptyError,
    RandomGenMaxError,
    RandomGenMinError,
    RandomGenMismatchError,
    RandomGenProbabilityNegativeError,
    RandomGenProbabilitySumError,
    RandomGenTypeError,
)
from randomgen.service import (
    DEFAULT_NUMBERS,
    DEFAULT_PROBABILITIES,
    RandomGenService,
)


class TestRandomGenService:
    """Test the RandomGen service."""

    @classmethod
    def setup_class(cls):
        cls.api = RandomGenService()

    def test_endpoint_api_v1_randomgen_pos(self):
        """Test the randomgen v1 endpoint with positive scenarios."""

        for num in (1, 1000, 10000):
            self.api.generate(RandomGenV1, num)

    def test_endpoint_api_v1_randomgen_neg(self):
        """Test the randomgen v1 endpoint with negative scenarios."""

        # Test the RandomGenMinError exception
        with pytest.raises(RandomGenMinError):
            for num in (-1, 0):
                self.api.generate(RandomGenV1, num)

        # Test the RandomGenMaxError exception
        with pytest.raises(RandomGenMaxError):
            for num in (10001,):
                self.api.generate(RandomGenV1, num)

    def test_endpoint_v2_randomgen_pos(self):
        """Test the randomgen v2 endpoint with positive scenarios."""

        for num in (1, 1000, 10000):
            self.api.generate(RandomGenV2, num)

    def test_endpoint_api_v2_randomgen_neg(self):
        """Test the randomgen v2 endpoint with negative scenarios."""

        # Test the RandomGenMinError exception
        with pytest.raises(RandomGenMinError):
            for num in (-1, 0):
                self.api.generate(RandomGenV2, num)

        # Test the RandomGenMaxError exception
        with pytest.raises(RandomGenMaxError):
            for num in (10001,):
                self.api.generate(RandomGenV2, num)

    def test_endpoint_randomgen_default_distribution_pos(self):
        """Omitting the distribution falls back to the built-in default."""

        response = self.api.generate(RandomGenV1, 100)

        assert response['quality']['expected_histogram'] == dict(
            zip(DEFAULT_NUMBERS, DEFAULT_PROBABILITIES, strict=False)
        )

    def test_endpoint_randomgen_custom_distribution_pos(self):
        """A caller-supplied distribution is sampled and scored per request."""

        response = self.api.generate(
            RandomGenV1,
            100,
            values=[1, 2, 3],
            probabilities=[0.2, 0.2, 0.6],
        )

        assert set(response['numbers']) <= {1, 2, 3}
        assert response['quality']['expected_histogram'] == {1: 0.2, 2: 0.2, 3: 0.6}

        # is_null is serialized as a JSON boolean, not an integer
        assert isinstance(response['quality']['chi_square_test']['is_null'], bool)

    def test_validate_distribution_neg(self):
        """Malformed distributions raise the matching domain error."""

        with pytest.raises(RandomGenMismatchError):
            self.api.validate_distribution([1, 2, 3], [0.2, 0.2, 0.6, 0.1])

        with pytest.raises(RandomGenMismatchError):
            self.api.validate_distribution([1, 2, 3], [0.2, 0.2])

        with pytest.raises(RandomGenEmptyError):
            self.api.validate_distribution([], [])

        with pytest.raises(RandomGenProbabilityNegativeError):
            self.api.validate_distribution([1, 2, 3], [0.2, 0.2, -0.6])

        with pytest.raises(RandomGenProbabilitySumError):
            self.api.validate_distribution([1, 2, 3], [0.2, 0.2, 0.5])

        with pytest.raises(RandomGenTypeError):
            self.api.validate_distribution(1, 0.2)

        with pytest.raises(RandomGenTypeError):
            self.api.validate_distribution([1, 2, 3], 0.2)

        with pytest.raises(RandomGenTypeError):
            self.api.validate_distribution(1, [0.2, 0.2, 0.6])


if __name__ == '__main__':
    pytest.main()
