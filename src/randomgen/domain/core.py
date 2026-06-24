import random
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence
from itertools import accumulate
from typing import Self

from randomgen.domain.errors import (
    RandomGenEmptyError,
    RandomGenMismatchError,
    RandomGenProbabilityNegativeError,
    RandomGenProbabilitySumError,
    RandomGenTypeError,
)
from randomgen.domain.validation import validate_number_iterable


class RandomGenABC(metaclass=ABCMeta):
    """Abstract base class for random number generators.

    Attributes:
        _numbers: A list of numbers.
        _probabilities: A list of probabilities.

    """

    def __init__(self) -> None:
        self._numbers: Sequence[float] = ()
        self._probabilities: Sequence[float] = ()

    def __str__(self) -> str:
        return f'Numbers: {self._numbers}, Probabilities: {self._probabilities}'

    def from_dict(self, dict_obj: dict) -> Self:
        """Set the numbers and probabilities from a dictionary.

        Args:
            dict_obj: A dictionary of numbers and probabilities.

        Returns:
            self: The instance of the class.

        """

        self._numbers = list(dict_obj.keys())
        self._probabilities = list(dict_obj.values())

        return self

    def to_dict(self) -> dict[float, float]:
        """Return the numbers and probabilities as a dictionary.

        Returns:
            A dictionary of numbers and respective probabilities.

        """

        return dict(zip(self._numbers, self._probabilities, strict=False))

    def set_numbers(self, values: Sequence[float]) -> Self:
        """Set the numbers (similar to the categories in a histogram).

        Args:
            values: A list of numbers.

        Returns:
            self: The instance of the class.

        """

        self._numbers = values
        return self

    def validate_numbers(self) -> Self:
        """Validate the numbers.

        Returns:
            self: The instance of the class.

        """

        validate_number_iterable(self._numbers)
        return self

    def set_probabilities(self, values: Sequence[float]) -> Self:
        """Set the probabilities.

        Args:
            values: A list of probabilities.

        Returns:
            self: The instance of the class.

        """

        self._probabilities = values
        return self

    def validate_probabilities(self) -> Self:
        """Validate the probabilities.

        Returns:
            self: The instance of the class.

        """

        # Check if the probabilities is None
        if self._probabilities is None or not hasattr(self._probabilities, '__iter__'):
            raise RandomGenTypeError()

        # Check if empty
        elif not self._probabilities:
            raise RandomGenEmptyError()

        # Probabilities are an ordered sequence: a set or dict would lose the
        # positional alignment with the numbers, so they are rejected here even
        # though validate_numbers accepts a set.
        elif isinstance(self._probabilities, (set, dict)) or not all(
            isinstance(prob, (int, float)) for prob in self._probabilities
        ):
            raise RandomGenTypeError()

        # A negative weight is a distinct, well-classified error — not a type
        # error — so the domain and the service agree on its classification.
        elif any(probability < 0 for probability in self._probabilities):
            raise RandomGenProbabilityNegativeError()

        # Check if the probabilities sum to 1
        elif round(sum(self._probabilities), 3) != 1:
            raise RandomGenProbabilitySumError()

        return self

    def validate(self) -> Self:
        """Validate all the attributes of the class.

        Returns:
            self: The instance of the class.

        """

        # Validate the numbers and probabilities
        self.validate_numbers()
        self.validate_probabilities()

        # Check if the numbers and probabilities' lists have the same length
        if len(self._numbers) != len(self._probabilities):
            raise RandomGenMismatchError()

        return self

    def generate(self, amount: int) -> list[float]:
        """Generate random numbers based on the probabilities.

        Args:
            amount: The number of random numbers to generate.

        Returns:
            A list of random numbers.

        """

        return [self.next_num() for _ in range(amount)]

    @abstractmethod
    def next_num(self) -> float:
        """Abstract method to generate the next random number.

        Returns:
            A random number.

        """
        raise NotImplementedError


class RandomGenV1(RandomGenABC):
    """Inverse-transform sampler.

    Precomputes the cumulative distribution once in ``validate()`` and draws
    each number by locating ``random.random()`` within it.
    """

    def __init__(self) -> None:
        super().__init__()
        self._cumulative_probabilities: list[float] = []

    def calc_cdf(self) -> None:
        """Calculate the cumulative probabilities.

        Returns:
            self: The instance of the class.

        """

        # Running total in a single pass — O(n). The previous comprehension
        # re-summed the prefix each step, which is O(n^2) and made a large
        # category count disproportionately expensive. accumulate adds left to
        # right, so the resulting cumulative values are identical.
        self._cumulative_probabilities = list(accumulate(self._probabilities))

    def validate(self) -> Self:
        """Validate, then precompute the CDF this sampler draws against.

        Returns:
            self: The instance of the class.

        """

        super().validate()
        self.calc_cdf()
        return self

    def next_num(self) -> float:
        """Generate a random number using the random.random() function.

        Returns:
            A random number.
        """

        rand = random.random()
        for i, cum_prob in enumerate(self._cumulative_probabilities):
            if rand <= cum_prob:
                return self._numbers[i]

        # Floating-point guard: the final cumulative probability can be
        # marginally below 1.0, so rand may exceed it. Fall back to the
        # last number instead of implicitly returning None.
        return self._numbers[-1]


class RandomGenV2(RandomGenABC):
    """Direct weighted sampler.

    Delegates to ``random.choices`` with the raw probabilities, so it needs no
    precomputed CDF.
    """

    def next_num(self) -> float:
        """Generate a random number using the random.choice() function.

        Returns:
            A random number.
        """

        return random.choices(self._numbers, self._probabilities, k=1)[0]
