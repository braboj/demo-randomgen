from abc import ABCMeta, abstractmethod
from collections import Counter
from collections.abc import Sequence
from typing import Self

from scipy.stats import chi2

from randomgen.domain.errors import (
    RandomGenDomainError,
    RandomGenEmptyError,
    RandomGenMismatchError,
    RandomGenProbabilityNegativeError,
    RandomGenProbabilitySumError,
)
from randomgen.domain.validation import validate_number_iterable


class HypothesisTestAbc(metaclass=ABCMeta):
    """Abstract base class for hypothesis tests."""

    @abstractmethod
    def set_observed_numbers(self, values: Sequence[float]) -> Self:
        """Set the observed random numbers.

        Args:
            values: A list of random numbers.

        Returns:
            self: The instance of the class.

        """
        raise NotImplementedError

    @abstractmethod
    def validate_observed_numbers(self) -> Self:
        """Validate the observed random numbers.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def set_expected_probabilities(self, values: Sequence[float]) -> Self:
        """Set the expected probabilities.

        Args:
            values: A list of probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_expected_probabilities(self) -> Self:
        """Validate the expected probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> Self:
        """Validate the observed random numbers and expected probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def calc(self) -> Self:
        """Perform the hypothesis test.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def is_null(self, alpha: float = 0.05) -> bool | None:
        """Check if the null hypothesis is true.

        Args:
            alpha: The significance level.

        Returns:
            bool: True if the null hypothesis is true, False otherwise.
        """
        raise NotImplementedError


class ChiSquareTest(HypothesisTestAbc):
    """Perform the chi-square test for a given significance level.

    The Chi-square test is used to determine if there is a significant
    difference between the expected and observed frequencies of random
    numbers. It is used to test the null hypothesis that the observed
    distribution is the same as the expected distribution.

    Attributes:
        _counter: A Counter object to count the occurrences of each number.
        _total: The total number of elements in the list.
        _observed: A histogram of the observed random numbers.
        _expected: A histogram of the expected random numbers.
        chi_square: The chi-square value.
        df: The degrees of freedom.
        p_value: The p-value.
        numbers: The observed random numbers.
        probabilities: The expected probabilities.

    """

    def __init__(self) -> None:
        # Counter for the random numbers
        self._counter: Counter | None = None

        # Total number of random numbers
        self._total: int | None = None

        # Histogram of the random numbers
        self._observed: dict[float, float] | None = None

        # Expected histogram based on the probabilities
        self._expected: dict[float, float] | None = None

        # Chi-square value
        self.chi_square: float | None = None

        # Degrees of freedom
        self.df: int | None = None

        # P-value
        self.p_value: float | None = None

        # Observed random numbers
        self.numbers: Sequence[float] = ()

        # Given probabilities to test
        self.probabilities: Sequence[float] = ()

        # Optional expected category labels aligned with the probabilities
        self.expected_numbers: Sequence[float] = ()

    def __str__(self) -> str:
        message = (
            f'Chi-square: {self.chi_square} df: {self.df} P-value'
            f':{self.p_value} Null hypothesis: {self.is_null()}'
        )

        return message

    def set_observed_numbers(self, values: Sequence[float]) -> Self:
        """Set the observed random numbers.

        Args:
            values: A list of random numbers.

        Returns:
            self: The instance of the class.

        """

        self.numbers = values
        return self

    def validate_observed_numbers(self) -> Self:
        """Validate the observed random numbers.

        Returns:
            self: The instance of the class.

        """

        validate_number_iterable(self.numbers)
        return self

    def set_expected_probabilities(self, values: Sequence[float]) -> Self:
        """Set the expected probabilities.

        Args:
            values: A list of probabilities.

        Returns:
            self: The instance of the class.

        """

        self.probabilities = values
        return self

    def set_expected_numbers(self, values: Sequence[float]) -> Self:
        """Set the expected category labels (the test's domain).

        Optional. When provided, the chi-square test is computed over this
        full set of categories, so categories observed zero times still
        contribute to the statistic. When omitted, the categories are
        inferred from the sorted unique observed numbers.

        Args:
            values: Category labels aligned with the expected probabilities.

        Returns:
            self: The instance of the class.

        """

        self.expected_numbers = values
        return self

    def validate_expected_probabilities(self) -> Self:
        """Validate the expected probabilities.

        Beyond the shared numeric-iterable check, the expected probabilities
        must form a valid distribution: a goodness-of-fit test against weights
        that are negative or do not sum to 1 has no statistical meaning and
        would otherwise yield a negative ``df`` or an all-zero domain. The
        tolerance mirrors the generator's own check in ``core.py``.

        Returns:
            self: The instance of the class.

        Raises:
            RandomGenProbabilityNegativeError: If any weight is negative.
            RandomGenProbabilitySumError: If the weights do not sum to 1.

        """

        validate_number_iterable(self.probabilities)

        if any(probability < 0 for probability in self.probabilities):
            raise RandomGenProbabilityNegativeError()

        if round(sum(self.probabilities), 3) != 1:
            raise RandomGenProbabilitySumError()

        return self

    def validate(self) -> Self:
        """Validate the observed random numbers and expected probabilities.

        Returns:
            self: The instance of the class.

        """

        self.validate_observed_numbers()
        self.validate_expected_probabilities()
        return self

    def calc(self) -> Self:
        """Perform the chi-square test for the given significance level

        It tells us how likely it is that the null hypothesis is true. The
        null hypothesis is that the observed distribution is the same as the
        expected distribution.

        Returns:
            self: The instance of the class.

        """

        # Count the frequency of each observed number
        self._counter = Counter(self.numbers)

        # Total number of observed random numbers
        self._total = sum(self._counter.values())

        # An empty sample has no distribution to test
        if self._total == 0:
            raise RandomGenEmptyError()

        # Determine the category domain. Prefer the explicit expected
        # numbers so categories with zero observations still count toward
        # the statistic; otherwise fall back to the sorted unique observed
        # values (which cannot recover never-observed categories).
        if self.expected_numbers:
            categories = list(self.expected_numbers)
            # Observations outside the declared domain are counted in _total
            # but contribute no chi-square term, biasing the statistic toward
            # the null hypothesis. Reject them so the statistic stays
            # consistent with the domain being tested.
            domain = set(categories)
            if any(num not in domain for num in self._counter):
                raise RandomGenDomainError()
        else:
            categories = sorted(self._counter)

        # Each category must have a matching probability; a length mismatch
        # would otherwise be silently truncated by zip().
        if len(categories) != len(self.probabilities):
            raise RandomGenMismatchError()

        # Observed proportion per category over the full domain
        self._observed = {num: self._counter.get(num, 0) / self._total for num in categories}

        # Expected count per category: probability * total observations
        self._expected = {
            num: probability * self._total
            for num, probability in zip(categories, self.probabilities, strict=False)
        }

        # Only categories with a positive expected count contribute — a zero
        # expected frequency is undefined for the chi-square statistic.
        contributing = [num for num in categories if self._expected.get(num, 0) > 0]

        # Chi-square statistic: sum of (observed - expected)^2 / expected
        # over every contributing category, including those observed zero
        # times (which still contribute (0 - expected)^2 / expected).
        self.chi_square = sum(
            (self._counter.get(num, 0) - self._expected[num]) ** 2 / self._expected[num]
            for num in contributing
        )

        # Degrees of freedom: categories - 1. The probabilities are given,
        # not estimated from the data, so there is no extra reduction.
        self.df = len(contributing) - 1

        # The goodness-of-fit test needs at least two categories (df >= 1). For
        # a degenerate single-category distribution df is 0 and the p-value is
        # mathematically undefined: chi2.cdf(0.0, 0) is NaN, which serialises as
        # a bare `NaN` token that is not valid JSON (RFC 8259). Report the
        # statistic as undefined (None -> JSON null) instead.
        if self.df < 1:
            self.p_value = None
        else:
            self.p_value = 1 - chi2.cdf(self.chi_square, self.df)

        return self

    def is_null(self, alpha: float = 0.05) -> bool | None:
        """Check if the null hypothesis is true.

        Args:
            alpha: The significance level.

        Returns:
            bool: True if the null hypothesis is true, False otherwise, or
            ``None`` when the test does not apply (a degenerate single-category
            distribution has too few degrees of freedom for a verdict).

        Notes:
            Scipy/Numpy hijacks bool somehow, and it becomes a bool_ object.
            Unfortunately, this causes some problems when comparing the
            result using the is operator (e.g bool(0.05) is False).
        """

        # No p-value means the test was not computed (df < 1); there is no
        # verdict to report.
        if self.p_value is None:
            return None

        return bool(self.p_value > alpha)
