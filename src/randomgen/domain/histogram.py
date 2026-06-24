from collections import Counter

from randomgen.domain.errors import RandomGenEmptyError
from randomgen.domain.validation import validate_number_iterable


class Histogram(dict):
    """Helper class to build a histogram from a list of numbers

    Attributes:
        _numbers: A list of numbers.
        _counter: A Counter object to count the occurrences of each number.
        _total: The total number of elements in the list.

    """

    def __init__(self):
        super().__init__()
        self._numbers = ()
        self._counter = Counter()
        self._total = 0

    def from_dict(self, histogram):
        """Set the histogram from a dictionary.

        Args:
            histogram: A dictionary of numbers and probabilities.

        Returns:
            self: The instance of the class.

        """

        self.update(histogram)
        return self

    def set_numbers(self, numbers):
        """Set the numbers to build the histogram.

        Args:
            numbers: A list of numbers.

        Returns:
            self: The instance of the class.

        """

        self._numbers = numbers
        return self

    def validate_numbers(self):
        """Validate the numbers.

        Returns:
            self: The instance of the class.

        """

        validate_number_iterable(self._numbers)
        return self

    def validate(self):
        """Validate the numbers and probabilities.

        Returns:
            self: The instance of the class.

        """

        self.validate_numbers()
        return self

    def calc(self):
        """Calculate the histogram.

        Returns:
            self: The instance of the class.

        """

        # Count the occurrences of each number
        self._counter = Counter(self._numbers)

        # Calculate the total number of elements
        self._total = sum(self._counter.values())

        # An empty input has no histogram and would divide by zero
        if self._total == 0:
            raise RandomGenEmptyError()

        # Update self with the histogram parameters
        self.update({num: count / self._total for num, count in self._counter.items()})

        return self
