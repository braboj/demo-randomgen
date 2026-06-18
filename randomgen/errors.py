# encoding: utf-8

class RandomGenError(Exception):
    """Base class for randomgen errors.

    Args:
        message (str): The error message.

    """

    def __init__(self, message):
        super().__init__(message)

    @classmethod
    def set_message(cls, message):
        cls.message = message


class RandomGenTypeError(RandomGenError):
    """Error for invalid types of numbers and probabilities."""

    MESSAGE = "The numbers and probabilities must be a list of numbers."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenEmptyError(RandomGenError):
    """Error for empty lists of numbers and probabilities. """

    MESSAGE = "The numbers and probabilities lists must not be empty."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenMismatchError(RandomGenError):
    """Error for mismatched lengths of numbers and probabilities."""

    MESSAGE = "The numbers and probabilities lists must have the same length."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenProbabilitySumError(RandomGenError):
    """Error for probabilities that do not sum to 1."""

    MESSAGE = "Probabilities must sum to 1."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenProbabilityNegativeError(RandomGenError):
    """Error for negative probabilities."""

    MESSAGE = "Probabilities must be non-negative."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenMaxError(RandomGenError):
    """Error for exceeding the maximum limit of random numbers."""

    MESSAGE = "The quantity of random numbers exceeds the maximum limit."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenMinError(RandomGenError):
    """Error for exceeding the minimum limit of random numbers."""

    MESSAGE = "The quantity of random numbers must be positive."

    def __init__(self):
        super().__init__(message=self.MESSAGE)


class RandomGenQuantityError(RandomGenError):
    """Error for a non-integer requested quantity."""

    MESSAGE = "The 'numbers' query parameter must be an integer."

    def __init__(self):
        super().__init__(message=self.MESSAGE)
