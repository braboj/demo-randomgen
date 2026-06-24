from randomgen.domain.core import RandomGenV1, RandomGenV2
from randomgen.domain.histogram import Histogram
from randomgen.domain.hypothesis import ChiSquareTest


def main(randomgen):
    """ Random generator application

    Args:
        randomgen (RandomGenABC): Random generator class to use

    """

    print(f"Using random generator: {randomgen.__name__}")

    # Data to test the random generator
    n = 10000
    nums = (-1, 0, 1, 2, 3)
    prob = (0.01, 0.3, 0.58, 0.1, 0.01)
    # prob = (0.2, 0.2, 0.2, 0.2, 0.2)

    # Example usage using a fluent interface
    rg = (
        randomgen()
        .set_numbers(nums)
        .set_probabilities(prob)
        .validate()
    )

    # Generate N random numbers
    randoms = [rg.next_num() for _ in range(n)]

    # Print the expected histogram and the actual histogram
    expected = (
        Histogram()
        .from_dict(dict(zip(nums, prob)))
    )
    print(f"Expected histogram: {expected}")

    # Calculate the frequency and probability of each number
    observed = (
        Histogram()
        .set_numbers(randoms)
        .calc()
        # .plot()
    )
    print(f"Observed histogram: {observed}")

    # Test the distribution of random numbers
    hypothesis = (
        ChiSquareTest()
        .set_observed_numbers(randoms)
        .set_expected_probabilities(prob)
        .calc()
    )
    print("Hypothesis is: ", hypothesis.is_null())


if __name__ == "__main__":
    main(RandomGenV1)
    main(RandomGenV2)
