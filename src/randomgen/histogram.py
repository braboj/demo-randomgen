from collections import Counter

from randomgen.errors import RandomGenEmptyError, RandomGenTypeError


class Histogram(dict):
    """Helper class to build a histogram from a list of numbers

    Attributes:
        _numbers: A list of numbers.
        _counter: A Counter object to count the occurrences of each number.
        _total: The total number of elements in the list.
        _probabilities: A list of probabilities for each number.

    """

    def __init__(self):
        super().__init__()
        self._numbers = ()
        self._counter = Counter()
        self._total = 0
        self._probabilities = ()

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

        # Check if the numbers is None
        if (
            self._numbers is None
            or isinstance(self._numbers, dict)
            or not hasattr(self._numbers, '__iter__')
            or not all(isinstance(n, (int, float)) for n in self._numbers)
        ):
            raise RandomGenTypeError()

        # Check if the number list is empty
        elif not self._numbers:
            raise RandomGenEmptyError()

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


###############################################################################
# Examples
###############################################################################

if __name__ == '__main__':
    import random

    # Generate 1000 random numbers
    random_numbers = [random.randint(-1, 3) for _ in range(10000)]

    # Create a histogram object
    h1 = Histogram().set_numbers(random_numbers).validate_numbers().calc()
    print(h1)

    h2 = Histogram().from_dict(h1)
    print(h2)
