import time
import pytest

from randomgen.core import RandomGenV1, RandomGenV2
from randomgen.hypothesis import ChiSquareTest
from randomgen.errors import (
    RandomGenTypeError,
    RandomGenEmptyError,
    RandomGenMismatchError,
    RandomGenProbabilitySumError,

)

versions = [RandomGenV1, RandomGenV2]


# #############################################################################
@pytest.fixture(scope="class")
def randomgen(request):
    if hasattr(request, 'param'):
        return request.param()
    return RandomGenV1()  # Default version if none specified


###############################################################################

@pytest.mark.parametrize("randomgen", versions, indirect=True)
class TestRandomGenParamNumbers(object):
    """ Test the `numbers` parameter."""

    def test_none(self, randomgen):
        """ Test the `numbers` parameter with None."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers(None)
            randomgen.validate()

    def test_empty(self, randomgen):
        """ Test the `numbers` parameter with an empty list."""

        with pytest.raises(RandomGenEmptyError):
            randomgen.set_numbers([])
            randomgen.validate_numbers()

    def test_int(self, randomgen):
        """ Test the `numbers` parameter with an integer."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers(123)
            randomgen.validate_numbers()

    def test_int_list(self, randomgen):
        """ Test the `numbers` parameter with an integer list."""

        randomgen.set_numbers([-1, 0, 1, 2, 3])
        randomgen.validate_numbers()
        assert randomgen._numbers == [-1, 0, 1, 2, 3]

    def test_int_tuple(self, randomgen):
        """ Test the `numbers` parameter with an integer tuple."""

        randomgen.set_numbers((-1, 0, 1, 2, 3))
        randomgen.validate_numbers()
        assert randomgen._numbers == (-1, 0, 1, 2, 3)

    def test_int_set(self, randomgen):
        """ Test the `numbers` parameter with an integer set."""

        randomgen.set_numbers({-1, 0, 1, 2, 3})
        randomgen.validate_numbers()
        assert randomgen._numbers == {-1, 0, 1, 2, 3}

    def test_float(self, randomgen):
        """ Test the `numbers` parameter with a float."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers(123.45)
            randomgen.validate_numbers()

    def test_float_list(self, randomgen):
        """ Test the `numbers` parameter with a float list."""

        randomgen.set_numbers([-1.0, 0.0, 1.0, 2.0, 3.0])
        randomgen.validate_numbers()
        assert randomgen._numbers == [-1.0, 0.0, 1.0, 2.0, 3.0]

    def test_float_tuple(self, randomgen):
        """ Test the `numbers` parameter with a float tuple."""

        randomgen.set_numbers((-1.0, 0.0, 1.0, 2.0, 3.0))
        randomgen.validate_numbers()
        assert randomgen._numbers == (-1.0, 0.0, 1.0, 2.0, 3.0)

    def test_float_set(self, randomgen):
        """ Test the `numbers` parameter with a float set."""

        randomgen.set_numbers({-1.0, 0.0, 1.0, 2.0, 3.0})
        randomgen.validate_numbers()
        assert randomgen._numbers == {-1.0, 0.0, 1.0, 2.0, 3.0}

    def test_string(self, randomgen):
        """ Test the `numbers` parameter with a string."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers("123")
            randomgen.validate_numbers()

    def test_string_list(self, randomgen):
        """ Test the `numbers` parameter with a string list."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers(["-1", "0", "1", "2", "3"])
            randomgen.validate_numbers()

    def test_dict(self, randomgen):
        """ Test the `numbers` parameter with a dictionary."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers({-1: 1, 0: 1, 1: 1, 2: 1, 3: 1})
            randomgen.validate_numbers()

    def test_mixed_types(self, randomgen):
        """ Test the `numbers` parameter with mixed types."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_numbers([-1, 0.0, "1", 2.0, 3])
            randomgen.validate_numbers()

    def test_mixed_numbers(self, randomgen):
        """ Test the `numbers` parameter with mixed numbers."""

        randomgen.set_numbers([-1, 0, 1, 2.0, 3])
        randomgen.validate_numbers()
        assert randomgen._numbers == [-1, 0, 1, 2.0, 3]


###############################################################################

@pytest.mark.parametrize("randomgen", versions, indirect=True)
class TestRandomGenParamProbabilities(object):
    """ Test the `probabilities` parameter."""

    def test_none(self, randomgen):
        """ Test the `probabilities` parameter with None."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities(None)
            randomgen.validate_probabilities()

    def test_empty(self, randomgen):
        """ Test the `probabilities` parameter with an empty list."""

        with pytest.raises(RandomGenEmptyError):
            randomgen.set_probabilities([])
            randomgen.validate_probabilities()

    def test_int(self, randomgen):
        """ Test the `probabilities` parameter with an integer."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities(123)
            randomgen.validate_probabilities()

    def test_int_list(self, randomgen):
        """ Test the `probabilities` parameter with an integer list."""

        randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.2])
        randomgen.validate_probabilities()
        assert randomgen._probabilities == [0.2, 0.2, 0.2, 0.2, 0.2]

    def test_int_tuple(self, randomgen):
        """ Test the `probabilities` parameter with an integer tuple."""

        randomgen.set_probabilities((0.2, 0.2, 0.2, 0.2, 0.2))
        randomgen.validate_probabilities()
        assert randomgen._probabilities == (0.2, 0.2, 0.2, 0.2, 0.2)

    def test_int_set(self, randomgen):
        """ Test the `probabilities` parameter with an integer set."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities({0.2, 0.2, 0.2, 0.2, 0.2})
            randomgen.validate_probabilities()

    def test_float(self, randomgen):
        """ Test the `probabilities` parameter with a float."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities(123.45)
            randomgen.validate_probabilities()

    def test_float_list(self, randomgen):
        """ Test the `probabilities` parameter with a float list."""

        randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.2])
        randomgen.validate_probabilities()
        assert randomgen._probabilities == [0.2, 0.2, 0.2, 0.2, 0.2]

    def test_float_tuple(self, randomgen):
        """ Test the `probabilities` parameter with a float tuple."""

        randomgen.set_probabilities((0.2, 0.2, 0.2, 0.2, 0.2))
        randomgen.validate_probabilities()
        assert randomgen._probabilities == (0.2, 0.2, 0.2, 0.2, 0.2)

    def test_float_set(self, randomgen):
        """ Test the `probabilities` parameter with a float set."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities({0.2, 0.2, 0.2, 0.2, 0.2})
            randomgen.validate_probabilities()

    def test_string(self, randomgen):
        """ Test the `probabilities` parameter with a string."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities("123")
            randomgen.validate_probabilities()

    def test_string_list(self, randomgen):
        """ Test the `probabilities` parameter with a string list."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities(["-1", "0", "1", "2", "3"])
            randomgen.validate_probabilities()

    def test_dict(self, randomgen):
        """ Test the `probabilities` parameter with a dictionary."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities({-1: 1, 0: 1, 1: 1, 2: 1, 3: 1})
            randomgen.validate_probabilities()

    def test_mixed_types(self, randomgen):
        """ Test the `probabilities` parameter with mixed types."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities([-1, 0.0, "1", 2.0, 3])
            randomgen.validate_probabilities()

    def test_mixed_numbers(self, randomgen):
        """ Test the `probabilities` parameter with mixed numbers."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities([-0.2, 0.4, 0.2, 0.2, 0.4])
            randomgen.validate_probabilities()

    def test_is_negative(self, randomgen):
        """ Test the `probabilities` parameter with negative numbers."""

        with pytest.raises(RandomGenTypeError):
            randomgen.set_probabilities([0.2, 0.2, 0.2, -0.2, 0.2])
            randomgen.validate_probabilities()

    def test_size_mismatch(self, randomgen):
        """ Test the `probabilities` parameter with a size mismatch."""

        with pytest.raises(RandomGenMismatchError):
            randomgen.set_numbers([1, 2, 3, 4, 5])
            randomgen.set_probabilities([0.1, 0.2, 0.3, 0.4])
            randomgen.validate()

    def test_sum_is_one(self, randomgen):
        """ Test the `probabilities` parameter with a sum of one."""

        randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.2])
        randomgen.validate_probabilities()
        assert sum(randomgen._probabilities) == 1

    def test_sum_is_zero(self, randomgen):
        """ Test the `probabilities` parameter with a sum of zero."""

        with pytest.raises(RandomGenProbabilitySumError):
            randomgen.set_probabilities([0.0, 0.0, 0.0, 0.0, 0.0])
            randomgen.validate_probabilities()

    def test_sum_is_greater_than_one(self, randomgen):
        """ Test the `probabilities` parameter with a sum greater than one."""

        with pytest.raises(RandomGenProbabilitySumError):
            randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.3])
            randomgen.validate()

    def test_sum_is_less_than_one(self, randomgen):
        """ Test the `probabilities` parameter with a sum less than one."""

        with pytest.raises(RandomGenProbabilitySumError):
            randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.1])
            randomgen.validate()


@pytest.mark.parametrize("randomgen", versions, indirect=True)
class TestRandomGenDistribution(object):
    """ Test the distribution quality of random numbers."""

    def test_fit_pass(self, randomgen):
        """ Test that the distribution fits on big sample size."""

        custom_probabilities = [0.5, 0.5]

        # Prepare the random generator
        randomgen.set_numbers([1, 2])
        randomgen.set_probabilities(custom_probabilities)
        randomgen.validate()

        # Generate the maximum number of random numbers
        random_numbers = [1] * 200 + [2] * 200

        # Perform the Chi-Square test
        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers(random_numbers)
            .set_expected_probabilities(custom_probabilities)
            .calc()
        )

        # Test if the hypothesis is valid
        assert hypothesis.is_null() is True

    def test_fit_fail(self, randomgen):
        """ Test that the distribution fits on big sample size. """

        custom_probabilities = [0.5, 0.5]

        # Prepare the random generator
        randomgen.set_numbers([1, 2])
        randomgen.set_probabilities(custom_probabilities)
        randomgen.validate()

        # Generate the maximum number of random numbers
        random_numbers = [1] * 10 + [2] * 100

        # Perform the Chi-Square test
        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers(random_numbers)
            .set_expected_probabilities(custom_probabilities)
            .calc()
        )

        # Test if the hypothesis is valid
        assert hypothesis.is_null() is False


@pytest.mark.parametrize("randomgen", versions, indirect=True)
class TestRandomGenPerformance(object):
    """ Test that the distribution fits on high sample size."""

    def test_time(self, randomgen):
        """ Test that the time execution is below 50ms. """

        randomgen.set_numbers([1, 2, 3, 4, 5])
        randomgen.set_probabilities([0.2, 0.2, 0.2, 0.2, 0.2])
        randomgen.validate()

        # Start measuring the time
        timestamp_1 = time.time_ns()

        # Generate the maximum number of random numbers
        randomgen.generate(amount=1000)

        # Stop measuring the time
        timestamp_2 = time.time_ns()

        # Test if the time is less than 25 msec
        delta = timestamp_2 - timestamp_1
        assert delta < 50e7


###############################################################################

class TestRandomGenV1NoneLeak(object):
    """ Regression: RandomGenV1.next_num must never return None.

    The inverse-CDF loop could fall through when random() landed in the
    floating-point tail above the last cumulative probability (#30).
    """

    def test_next_num_falls_back_to_last_in_float_tail(self, monkeypatch):
        """ A draw above the final cumulative probability (the float-error
        tail just below 1.0) returns the last number, not None. """

        rg = RandomGenV1().set_numbers([1, 2, 3])

        # Simulate a CDF whose final value is just below 1.0 due to float
        # rounding, then force random() into that tiny tail.
        rg._cumulative_probabilities = [0.2, 0.4, 0.9999999999999998]
        monkeypatch.setattr("random.random", lambda: 0.9999999999999999)

        assert rg.next_num() == 3

    def test_next_num_never_none_over_large_sample(self):
        """ Normal operation never yields None and stays within the set. """

        rg = (
            RandomGenV1()
            .set_numbers([1, 2, 3])
            .set_probabilities([0.2, 0.2, 0.6])
            .validate()
        )

        results = rg.generate(50000)

        assert None not in results
        assert set(results) <= {1, 2, 3}


###############################################################################

class TestRandomGenFromDict(object):
    """ Regression: from_dict must call keys()/values() and store indexable
    lists, not the bound methods (#30).
    """

    def test_from_dict_round_trips_to_dict(self):
        """ to_dict() returns the same mapping passed to from_dict(). """

        data = {1: 0.2, 2: 0.2, 3: 0.6}

        rg = RandomGenV1().from_dict(data)

        assert rg.to_dict() == data

    def test_from_dict_result_validates_and_generates(self):
        """ A generator built via from_dict validates and generates. """

        rg = RandomGenV1().from_dict({1: 0.2, 2: 0.2, 3: 0.6}).validate()

        assert rg.next_num() in (1, 2, 3)


if __name__ == "__main__":
    pytest.main()
