import pytest

from randomgen.domain.errors import (
    RandomGenEmptyError,
    RandomGenMismatchError,
    RandomGenTypeError,
)
from randomgen.domain.hypothesis import ChiSquareTest

variations = [
    ChiSquareTest,
]


# #############################################################################
@pytest.fixture(scope='class')
def hypothesis(request):
    if hasattr(request, 'param'):
        return request.param()
    return ChiSquareTest()  # Default version if none specified


###############################################################################


@pytest.mark.parametrize('hypothesis', variations, indirect=True)
class TestChiSquareParamObservedNums:
    """Test the `observed_numbers` parameter."""

    def test_none(self, hypothesis):
        """Test the `observed_numbers` parameter with None."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers(None)
            hypothesis.validate_observed_numbers()

    def test_empty(self, hypothesis):
        """Test the `observed_numbers` parameter with an empty list."""

        with pytest.raises(RandomGenEmptyError):
            hypothesis.set_observed_numbers([])
            hypothesis.validate_observed_numbers()

    def test_int(self, hypothesis):
        """Test the `observed_numbers` parameter with an integer."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers(123)
            hypothesis.validate_observed_numbers()

    def test_int_list(self, hypothesis):
        """Test the `observed_numbers` parameter with an integer list."""

        hypothesis.set_observed_numbers([-1, 0, 1, 2, 3])
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == [-1, 0, 1, 2, 3]

    def test_int_tuple(self, hypothesis):
        """Test the `observed_numbers` parameter with an integer tuple."""

        hypothesis.set_observed_numbers((-1, 0, 1, 2, 3))
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == (-1, 0, 1, 2, 3)

    def test_int_set(self, hypothesis):
        """Test the `observed_numbers` parameter with an integer set."""

        hypothesis.set_observed_numbers({-1, 0, 1, 2, 3})
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == {-1, 0, 1, 2, 3}

    def test_float(self, hypothesis):
        """Test the `observed_numbers` parameter with a float."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers(123.45)
            hypothesis.validate_observed_numbers()

    def test_float_list(self, hypothesis):
        """Test the `observed_numbers` parameter with a float list."""

        hypothesis.set_observed_numbers([-1.0, 0.0, 1.0, 2.0, 3.0])
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == [-1.0, 0.0, 1.0, 2.0, 3.0]

    def test_float_tuple(self, hypothesis):
        """Test the `observed_numbers` parameter with a float tuple."""

        hypothesis.set_observed_numbers((-1.0, 0.0, 1.0, 2.0, 3.0))
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == (-1.0, 0.0, 1.0, 2.0, 3.0)

    def test_float_set(self, hypothesis):
        """Test the `observed_numbers` parameter with a float set."""

        hypothesis.set_observed_numbers({-1.0, 0.0, 1.0, 2.0, 3.0})
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == {-1.0, 0.0, 1.0, 2.0, 3.0}

    def test_string(self, hypothesis):
        """Test the `observed_numbers` parameter with a string."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers('123')
            hypothesis.validate_observed_numbers()

    def test_string_list(self, hypothesis):
        """Test the `observed_numbers` parameter with a string list."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers(['-1', '0', '1', '2', '3'])
            hypothesis.validate_observed_numbers()

    def test_dict(self, hypothesis):
        """Test the `observed_numbers` parameter with a dictionary."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers({-1: 1, 0: 1, 1: 1, 2: 1, 3: 1})
            hypothesis.validate_observed_numbers()

    def test_mixed_types(self, hypothesis):
        """Test the `observed_numbers` parameter with mixed types."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_observed_numbers([-1, 0.0, '1', 2.0, 3])
            hypothesis.validate_observed_numbers()

    def test_mixed_numbers(self, hypothesis):
        """Test the `observed_numbers` parameter with mixed numbers."""

        hypothesis.set_observed_numbers([-1, 0, 1, 2.0, 3])
        hypothesis.validate_observed_numbers()
        assert hypothesis.numbers == [-1, 0, 1, 2.0, 3]


##############################################################################


@pytest.mark.parametrize('hypothesis', variations, indirect=True)
class TestChiSquareExpectedParamProbabilities:
    """Test the `expected_probabilities` parameter."""

    def test_none(self, hypothesis):
        """Test the `expected_probabilities` parameter with None."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities(None)
            hypothesis.validate_expected_probabilities()

    def test_empty(self, hypothesis):
        """Test the `expected_probabilities` parameter with an empty list."""

        with pytest.raises(RandomGenEmptyError):
            hypothesis.set_expected_probabilities([])
            hypothesis.validate_expected_probabilities()

    def test_int(self, hypothesis):
        """Test the `expected_probabilities` parameter with an integer."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities(123)
            hypothesis.validate_expected_probabilities()

    def test_int_list(self, hypothesis):
        """Test the `expected_probabilities` parameter with an integer list."""

        hypothesis.set_expected_probabilities([-1, 0, 1, 2, 3])
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == [-1, 0, 1, 2, 3]

    def test_int_tuple(self, hypothesis):
        """Test the `expected_probabilities` parameter with an integer tuple."""

        hypothesis.set_expected_probabilities((-1, 0, 1, 2, 3))
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == (-1, 0, 1, 2, 3)

    def test_int_set(self, hypothesis):
        """Test the `expected_probabilities` parameter with an integer set."""

        hypothesis.set_expected_probabilities({-1, 0, 1, 2, 3})
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == {-1, 0, 1, 2, 3}

    def test_float(self, hypothesis):
        """Test the `expected_probabilities` parameter with a float."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities(123.45)
            hypothesis.validate_expected_probabilities()

    def test_float_list(self, hypothesis):
        """Test the `expected_probabilities` parameter with a float list."""

        hypothesis.set_expected_probabilities([-1.0, 0.0, 1.0, 2.0, 3.0])
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == [-1.0, 0.0, 1.0, 2.0, 3.0]

    def test_float_tuple(self, hypothesis):
        """Test the `expected_probabilities` parameter with a float tuple."""

        hypothesis.set_expected_probabilities((-1.0, 0.0, 1.0, 2.0, 3.0))
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == (-1.0, 0.0, 1.0, 2.0, 3.0)

    def test_float_set(self, hypothesis):
        """Test the `expected_probabilities` parameter with a float set."""

        hypothesis.set_expected_probabilities({-1.0, 0.0, 1.0, 2.0, 3.0})
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == {-1.0, 0.0, 1.0, 2.0, 3.0}

    def test_string(self, hypothesis):
        """Test the `expected_probabilities` parameter with a string."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities('123')
            hypothesis.validate_expected_probabilities()

    def test_string_list(self, hypothesis):
        """Test the `expected_probabilities` parameter with a string list."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities(['-1', '0', '1', '2', '3'])
            hypothesis.validate_expected_probabilities()

    def test_dict(self, hypothesis):
        """Test the `expected_probabilities` parameter with a dictionary."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities({-1: 1, 0: 1, 1: 1, 2: 1, 3: 1})
            hypothesis.validate_expected_probabilities()

    def test_mixed_types(self, hypothesis):
        """Test the `expected_probabilities` parameter with mixed types."""

        with pytest.raises(RandomGenTypeError):
            hypothesis.set_expected_probabilities([-1, 0.0, '1', 2.0, 3])
            hypothesis.validate_expected_probabilities()

    def test_mixed_numbers(self, hypothesis):
        """Test the `expected_probabilities` parameter with mixed numbers."""

        hypothesis.set_expected_probabilities([-1, 0, 1, 2.0, 3])
        hypothesis.validate_expected_probabilities()
        assert hypothesis.probabilities == [-1, 0, 1, 2.0, 3]


##############################################################################


@pytest.mark.parametrize('hypothesis', variations, indirect=True)
class TestChiSquareFunctional:
    """Test the functional aspects of the ChiSquareTest class."""

    def test_chi_square_pass(self, hypothesis):
        """Test the ChiSquareTest class with a passing test."""

        (
            hypothesis.set_observed_numbers([1, 1, 1, 2, 2, 2])
            .set_expected_probabilities([0.5, 0.5])
            .calc()
        )

        assert hypothesis.is_null() is True

    def test_chi_square_fail(self, hypothesis):
        """Test the ChiSquareTest class with a failing test."""

        (
            hypothesis.set_observed_numbers([1, 1, 1, 2, 2, 2])
            .set_expected_probabilities([0.1, 0.9])
            .calc()
        )

        assert hypothesis.is_null() is False

    def test_str_summarises_result(self, hypothesis):
        """__str__ summarises the chi-square statistic, df, and verdict."""

        hypothesis.set_observed_numbers([1, 1, 2, 2]).set_expected_probabilities([0.5, 0.5]).calc()

        assert 'Chi-square' in str(hypothesis)


##############################################################################


class TestChiSquareExpectedDomain:
    """Regression: the chi-square test must be computed over the full
    expected category domain, not only the observed values (#30).
    """

    def test_df_spans_full_domain_when_categories_unobserved(self):
        """With one observation over five declared categories, the degrees
        of freedom are 4 (categories - 1), not a degenerate 0."""

        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers([0])
            .set_expected_numbers([-1, 0, 1, 2, 3])
            .set_expected_probabilities([0.01, 0.3, 0.58, 0.1, 0.01])
            .calc()
        )

        assert hypothesis.df == 4

    def test_expected_counts_align_to_declared_numbers(self):
        """Each probability maps to its declared category even when some
        categories are unobserved (no positional misalignment)."""

        # Observe only categories 0 and 2 of the five-category domain.
        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers([0, 0, 2])
            .set_expected_numbers([-1, 0, 1, 2, 3])
            .set_expected_probabilities([0.1, 0.2, 0.3, 0.3, 0.1])
            .calc()
        )

        total = 3
        assert hypothesis.df == 4
        assert hypothesis._expected[0] == pytest.approx(0.2 * total)
        assert hypothesis._expected[2] == pytest.approx(0.3 * total)

    def test_falls_back_to_observed_categories_without_domain(self):
        """Without set_expected_numbers, categories are inferred from the
        observed values (preserves the original contract)."""

        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers([1, 1, 1, 2, 2, 2])
            .set_expected_probabilities([0.5, 0.5])
            .calc()
        )

        assert hypothesis.df == 1
        assert hypothesis.is_null() is True


##############################################################################


class TestChiSquareGuards:
    """Regression: calc() must fail loudly on empty input or a category/
    probability length mismatch instead of dividing by zero or silently
    truncating with zip (finding C5).
    """

    def test_calc_empty_observed_raises(self):
        """An empty observed sample raises instead of dividing by zero."""

        with pytest.raises(RandomGenEmptyError):
            (ChiSquareTest().set_observed_numbers([]).set_expected_probabilities([0.5, 0.5]).calc())

    def test_calc_category_probability_mismatch_raises(self):
        """More categories than probabilities raises, not truncates."""

        with pytest.raises(RandomGenMismatchError):
            (
                ChiSquareTest()
                .set_observed_numbers([1, 2, 3])
                .set_expected_numbers([1, 2, 3])
                .set_expected_probabilities([0.5, 0.5])
                .calc()
            )


##############################################################################


class TestChiSquareDegenerateDomain:
    """Regression (#233): a single-category distribution has df = 0, for which
    the goodness-of-fit p-value is mathematically undefined. calc() must report
    it as undefined (None) rather than the non-JSON NaN that chi2.cdf(0, 0)
    yields, and is_null() must return None (no verdict) rather than False.
    """

    def test_single_category_with_domain_reports_undefined_p_value(self):
        """An explicit single-category domain leaves p_value undefined."""

        hypothesis = (
            ChiSquareTest()
            .set_observed_numbers([5, 5, 5, 5, 5])
            .set_expected_numbers([5])
            .set_expected_probabilities([1.0])
            .calc()
        )

        assert hypothesis.df == 0
        assert hypothesis.chi_square == 0.0
        assert hypothesis.p_value is None
        assert hypothesis.is_null() is None

    def test_single_category_inferred_reports_undefined_p_value(self):
        """The same holds when the lone category is inferred from observations
        (no set_expected_numbers)."""

        hypothesis = (
            ChiSquareTest().set_observed_numbers([5, 5, 5]).set_expected_probabilities([1.0]).calc()
        )

        assert hypothesis.df == 0
        assert hypothesis.p_value is None
        assert hypothesis.is_null() is None


if __name__ == '__main__':
    pytest.main()
