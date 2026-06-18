# encoding: utf-8

import random
from scipy.stats import chi2
from collections import Counter
from abc import ABCMeta, abstractmethod

from randomgen.errors import (
    RandomGenTypeError,
    RandomGenEmptyError,
    RandomGenMismatchError,
)


class HypothesisTestAbc(metaclass=ABCMeta):
    """ Abstract base class for hypothesis tests. """

    @abstractmethod
    def set_observed_numbers(self, values):
        """ Set the observed random numbers.

        Args:
            values: A list of random numbers.

        Returns:
            self: The instance of the class.

        """
        raise NotImplementedError

    @abstractmethod
    def validate_observed_numbers(self):
        """ Validate the observed random numbers.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def set_expected_probabilities(self, values):
        """ Set the expected probabilities.

        Args:
            values: A list of probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def validate_expected_probabilities(self):
        """ Validate the expected probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        """ Validate the observed random numbers and expected probabilities.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def calc(self):
        """ Perform the hypothesis test.

        Returns:
            self: The instance of the class.
        """
        raise NotImplementedError

    @abstractmethod
    def is_null(self, alpha=0.05):
        """ Check if the null hypothesis is true.

        Args:
            alpha: The significance level.

        Returns:
            bool: True if the null hypothesis is true, False otherwise.
        """
        raise NotImplementedError


class ChiSquareTest(HypothesisTestAbc):
    """ Perform the chi-square test for a given significance level.

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

    def __init__(self):
        # Counter for the random numbers
        self._counter = None

        # Total number of random numbers
        self._total = None

        # Histogram of the random numbers
        self._observed = None

        # Expected histogram based on the probabilities
        self._expected = None

        # Chi-square value
        self.chi_square = None

        # Degrees of freedom
        self.df = None

        # P-value
        self.p_value = None

        # Observed random numbers
        self.numbers = ()

        # Given probabilities to test
        self.probabilities = ()

        # Optional expected category labels aligned with the probabilities
        self.expected_numbers = ()

    def __str__(self):
        message = (f"Chi-square: {self.chi_square} df: {self.df} P-value"
                   f":{self.p_value} Null hypothesis: {self.is_null()}")

        return message

    def set_observed_numbers(self, values):
        """ Set the observed random numbers.

        Args:
            values: A list of random numbers.

        Returns:
            self: The instance of the class.

        """

        self.numbers = values
        return self

    def validate_observed_numbers(self):
        """ Validate the observed random numbers.

        Returns:
            self: The instance of the class.

        """

        # Check if the numbers is None
        if self.numbers is None:
            raise RandomGenTypeError()

        # Check if the numbers is a dictionary
        elif isinstance(self.numbers, dict):
            raise RandomGenTypeError()

        # Check if the numbers are iterable
        elif not hasattr(self.numbers, '__iter__'):
            raise RandomGenTypeError()

        # Check if the numbers are integers or floats
        elif not all(
                isinstance(num, (int, float)) for num in self.numbers):
            raise RandomGenTypeError()

        # Check if the number list is empty
        elif not self.numbers:
            raise RandomGenEmptyError()

        return self

    def set_expected_probabilities(self, values):
        """ Set the expected probabilities.

        Args:
            values: A list of probabilities.

        Returns:
            self: The instance of the class.

        """

        self.probabilities = values
        return self

    def set_expected_numbers(self, values):
        """ Set the expected category labels (the test's domain).

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

    def validate_expected_probabilities(self):
        """ Validate the expected probabilities.

        Returns:
            self: The instance of the class.

        """

        # Check if the probabilities is None
        if self.probabilities is None:
            raise RandomGenTypeError()

        # Check if the probabilities is a dictionary
        elif isinstance(self.probabilities, dict):
            raise RandomGenTypeError()

        # Check if the probabilities are iterable
        elif not hasattr(self.probabilities, '__iter__'):
            raise RandomGenTypeError()

        # Check if the probabilities are integers or floats
        elif not all(
                isinstance(num, (int, float)) for num in self.probabilities):
            raise RandomGenTypeError()

        # Check if the probability list is empty
        elif not self.probabilities:
            raise RandomGenEmptyError()

        return self

    def validate(self):
        """ Validate the observed random numbers and expected probabilities.

        Returns:
            self: The instance of the class.

        """

        self.validate_observed_numbers()
        self.validate_expected_probabilities()
        return self

    def calc(self):
        """ Perform the chi-square test for the given significance level

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
        else:
            categories = sorted(self._counter)

        # Each category must have a matching probability; a length mismatch
        # would otherwise be silently truncated by zip().
        if len(categories) != len(self.probabilities):
            raise RandomGenMismatchError()

        # Observed proportion per category over the full domain
        self._observed = {
            num: self._counter.get(num, 0) / self._total
            for num in categories
        }

        # Expected count per category: probability * total observations
        self._expected = {
            num: probability * self._total
            for num, probability
            in zip(categories, self.probabilities)
        }

        # Only categories with a positive expected count contribute — a zero
        # expected frequency is undefined for the chi-square statistic.
        contributing = [
            num for num in categories if self._expected.get(num, 0) > 0
        ]

        # Chi-square statistic: sum of (observed - expected)^2 / expected
        # over every contributing category, including those observed zero
        # times (which still contribute (0 - expected)^2 / expected).
        self.chi_square = sum(
            (self._counter.get(num, 0) - self._expected[num]) ** 2
            / self._expected[num]
            for num in contributing
        )

        # Degrees of freedom: categories - 1. The probabilities are given,
        # not estimated from the data, so there is no extra reduction.
        self.df = len(contributing) - 1

        # P-value corresponding to the chi-square statistic
        self.p_value = 1 - chi2.cdf(self.chi_square, self.df)

        return self

    def is_null(self, alpha=0.05):
        """ Check if the null hypothesis is true.

        Args:
            alpha: The significance level.

        Returns:
            bool: True if the null hypothesis is true, False otherwise.

        Notes:
            Scipy/Numpy hijacks bool somehow, and it becomes a bool_ object.
            Unfortunately, this causes some problems when comparing the
            result using the is operator (e.g bool(0.05) is False).
        """

        return bool(self.p_value > alpha)


###############################################################################
# Examples
###############################################################################

if __name__ == "__main__":

    # Generate random numbers from -1 to 3 in a uniform distribution
    nums = [random.randint(-1, 3) for _ in range(10000)]
    probs = [0.2, 0.2, 0.2, 0.2, 0.2]

    # Create the chi-square test object for a uniform distribution
    # The result should be True
    hypothesis = (
        ChiSquareTest()
        .set_observed_numbers(nums)
        .set_expected_probabilities(probs)
        .calc()
    )

    print("Hypothesis is: ", hypothesis.is_null())

    # Now change the probabilities to a different distribution
    # The result should be False
    probs = [0.01, 0.3, 0.58, 0.1, 0.01]

    hypothesis = (
        ChiSquareTest()
        .set_observed_numbers(nums)
        .set_expected_probabilities(probs)
        .calc()
    )

    print("Hypothesis is: ", hypothesis.is_null())
