## Solution Journal

> **The project's solution journal.** Part I (steps 1–20) is the original kata
> design journal — the thinking during the initial build, written in the future
> tense of a work-in-progress. Some of those plans changed before release, so
> the inline **[Update]** notes flag the points that no longer match the shipped
> code. Part II picks up after the first tag and narrates, at a design level,
> how the kata prototype became a small deployable service. For authoritative
> detail see the OpenAPI contract (`src/randomgen/openapi.yaml`) and the arc42
> docs (`docs/arc42/`); each decision below links to its record in
> `docs/decisions/` (ADRs), and the session-by-session log lives in
> `docs/dev-journal.md`.

### 1. Define the development environment

| Category             | Details                   |
|----------------------|---------------------------|
| Programming Language | Python 3.12+              |
| Python IDE           | PyCharm Community Edition |
| Code style           | PEP-8, Google Doc Strings |
| Linting              | PyCharm built-in linter   |
| Testing              | Pytest                    |
| Version Control      | Git                       |
| Git Hosting          | GitHub                    |
| CI/CD                | GitHub Actions            |
| Documentation        | GitHub Pages, MkDocs      |


### 2. Validate the data from the problem statement

Let's first check if the given numbers are correct. As QA engineer, the data
given is never trusted ;)

1. Is the length of random_nums and probabilities equal?
2. Is the sum of probabilities equal to 1?
3. Are all probabilities positive?

A manual check is enough for this task. 

1. Yes, the length of random_nums and probabilities is equal.
2. Yes, the sum of probabilities is equal to 1.
3. Yes, all probabilities are positive.

We can proceed with the implementation.

### 3. Questions, questions and more questions

We don't have any information on how the data is generated, for example, how 
many samples were taken to get the given distribution. Typically, this may lead
to skewed results due to under-sampling. 

The given distribution doesn't seem to be a binomial distribution... 

![Binomial_Distribution.png](../assets/images/binomial_distribution.png)

... or a Poisson distribution.

![Poisson_Distribution.png](../assets/images/poisson_distribution.png)

Visually, our distribution looks like a skewed custom distribution.

![Custom_Distribution.png](../assets/images/custom_distribution.png)

We will assume that the given distribution is correct and proceed with the
implementation. We will test our implementation with a large number of samples
for fairness using the Chi-Squared test.

### 4. Proof of concept

```python
import random

class RandomGen(object):
    
  def __init__(self, random_nums, probabilities):
    self._random_nums = random_nums
    self._probabilities = probabilities
      
  def next_num(self):
    return random.choices(self._random_nums, self._probabilities)[0]
```

Questions:

1. Do we have constraints regarding the compatibility with older versions of 
   Python? -> use contaiers
2. Are we allowed to use external libraries for statistical tests and 
   visualization? -> yes, the Chi-Square CDF is very complex for this task

### 5. Brainstorm the system design

We will implement two classes, one using `random.choices` and the other using
`random.random`. We will provide an abstract class to be used as an 
interface for both classes. It will also decouple implementation from client 
code.

![system_design.png](../assets/drawio/system_design.drawio.png)

A sample of the API design is shown below:

```text
# Create a random number generator
rg = (
    RandomGenV1()
    .set_random_nums([-1, 0, 1, 2, 3])
    .set_probabilities([0.01, 0.3, 0.58, 0.1, 0.01])
    .validate_input()
)

# Get a random number
num = rg.next_num()
print("Random number is: ", num)
```

```text
 # Create a hypothesis test
 
 random_numbers = random.
 hypothesis = (
     ChiSquareTest()
     .set_random_numbers()
     .set_probabilities([0.01, 0.3, 0.58, 0.1, 0.01])
     .calc_chi()
     .calc_p()
     .test()
 )
 
 # Hypothesis is True if the distribution is fair
 print("Hypothesis is: ", hypothesis)
```

```text
 # Create a histogram object
 histogram = (
     Histogram()
     .set_random_numbers(random_numbers)
     .build()
     .plot()
 )
 
 # Print the histogram
 print(hist)
```

Typically, at this stage the client shall approve the design, and we can proceed with the 
prototype implementation.

### 6. Implement the core prototype

We will implement the following classes:

1. `RandomGenAbc`: An abstract class to be used as an interface.
2. `RandomGenV1`: A class using `random.choices`.
3. `RandomGenV2`: A class using `random.random`.
4. `Histogram`: A helper class that creates a simple histogram object.
5. `ChiSquaredTest`: A helper class to perform the Chi-Squared test.

### 7. Implement the REST API with Flask

We will implement a simple REST API using Flask to access the solution. The API
will have the following endpoints:

1. `/api/v1/randomgen?number`: Returns a number of random numbers based on
   the random.random method.
2. `/api/v2/randomgen?number`: Returns a number of random numbers based on
   the random.choice method.
3. `/api/v1/config`: An optional endpoint to configure the random numbers and
   probabilities.

> **[Update]** The `/api/v1/config` endpoint was never shipped. Configuration
> is per-request: the distribution is supplied as request parameters on each
> call, so the service stays stateless with no stored server-side config.

### 8. Manual Integration tests

The following problems arised during the manual's integration tests:

1. **Rounding errors**: Using older versions of Python yield rounding errors. Round the 
   probabilities to 3 decimal places.


1. **Fairness**: The Chi-Squared test is not fair in case the number of 
   samples is low. The distribution is fair when the number of random values is above 50.


3. **Interface** We need to simplify the ChiSquaredTest class to make it 
   more user-friendly. Define method calculate that will the chi-squared, 
   p-value and the degrees of freedom.


4. **Configuration**: We will allow the user to configure its own distribution 
   using the parameters `numbers` and `probabilities` as defined in the problem statement.


### 9. Refactor the backend after the manual tests

Randomgen classes API:

```python
from randomgen.core import RandomGenV1

# Create a random number generator
rg = (
   RandomGenV1()
   .set_numbers([-1, 0, 1, 2, 3])
   .set_expected_probabilities([0.01, 0.3, 0.58, 0.1, 0.01])
   .validate()
)

# Get a random number
num = rg.next_num()
print("Random number is: ", num)
```

ChiSquaredTest API:

```
from randomgen.hypothesis import ChiSquareTest

# Create a hypothesis test
random_numbers = random.
hypothesis = (
  ChiSquareTest()
  .set_numbers()
  .set_probabilities([0.01, 0.3, 0.58, 0.1, 0.01])
  .calculate()
)

# Hypothesis is True if it is accepted
print("Hypothesis is: ", hypothesis.test())
```

Histogram API:

```
from randomgen.helpers import Histogram

# Create a histogram object
histogram = (
     Histogram()
     .set_numbers(random_numbers)
     .build()
     .plot()
)
 
# Print the histogram
print(hist)
```

### 10. Implement unit tests for the backend

**Functional tests**

We will implement unit tests for the Backend using Pytest. We will cover each class
and method with unit tests to guarantee that the solution is working as expected. 

The testing discovered some bugs in the implementation that are related to the validation of the 
input parameters. 

**Performance tests**

We will implement performance tests to check the performance of the solution. We will use the
maximum number of random numbers to check the performance of the solution. Manual testing showed
that RandomGenV2 is around 3 times slower than RandomGenV1.

The task definition doesn't mention any performance requirements. We will assume that the solution
should be fast enough to generate random numbers in a reasonable time. A reasonable time for the 
backend is around 50 msec, bearing in mind that the REST API is going to stack on it and add
some latency.


### 11. Implement automated integration tests

The integration tests showed that we need to wrap the exceptions by the backend and return a 
well-defined HTTP status code. 

### 12. Refactor the webserver after the integration tests

First, we will refactor the webserver to return a well-defined HTTP status code. We will also
add a configuration endpoint to allow the user to configure the bins and 
probabilities of a custom distribution histogram.

The response format will be also improved for better readability.

```json
{
    "numbers": [1, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    "quality": {
      "chi_square_test": {
        "chi_square": 44.4333333333333,
        "df": 1,
        "is_fair": 0,
        "p_value": 2.63168375980172e-11
      },
      "expected_histogram": {
        "-1": 0.01,
        "0": 0.3,
        "1": 0.58,
        "2": 0.1,
        "3": 0.01
      },
      "observed_histogram": {
        "0": 0.2,
        "1": 0.8
      }
    },
    "version": 1
}
```

> **[Update]** The shipped response differs from this sketch: the fairness key
> is `is_null` (not `is_fair`), and there is no top-level `version` field. The
> current schema lives in `src/randomgen/openapi.yaml`.

### 13. Feedback from a beta tester

The beta tester found the solution to be working as expected. The tester was
happy we provided an interface to configure the app using the REST API. 

Some issues were found regarding the interface of the ChiSquaredTest class. The
tester recommended simplifying the interface to make it more user-friendly. 
The naming of the methods must also be improved. The tester recommended 
renaming the methods (e.g. `calc()` instead of `calculate()` or `test()`).

The tester had some difficulties understanding the method chaining This opens 
a new conceptional question about the design. 

As a thum of rule, we will use the method chaining for methods that initialize
the internal state and then just access the internal state using properties.
Producing or consuming methods shall not be chained.

### 14. Refactor the backend after the feedback

* We will refactor the ChiSquaredTest class to make it more user-friendly. 
* We will rename the test() method to calc() and remove some methods
* We need to replace `is fair` with `is null`
* Encapsulate the internal state of the class as per requirements

After the changes, the unittests showed that the solution is working as 
expected. The server was also tested manually and the results were as expected.

### 15. Docstrings

Now it is time to add docstrings to the classes and methods. We will use the
**_Google Docstring_** format. The docstrings will be used to generate the API 
manual.

### 16. Containerize the solution

We will distribute the solution as a container. The application will consist 
of a flask server that will implement a simple API to access the random 
generator. The container will guarantee that the solution will run on any
machine that has Docker installed.

Considerations:

- No dockerfile optimizations (e.g. multi-stage builds)
- No memory or cpu limits (with docker compose)
- No persistent storage required 
- Choose a base image that is small and secure (e.g. alpine)
- Use a `.dockerignore` file to exclude unnecessary files
- Use digests to guarantee the integrity of the image
- The application will run on port 8080
- The application is not exposed to the internet (no need for HTTPS)

> **[Update]** The shipped image listens on port 5000, not 8080 (the container
> `EXPOSE`s 5000 and a PaaS injects `$PORT`).
 

### 17. Final code review

The final code review showed that the solution is working as expected. The
solution is well-documented, and the code is clean and readable. The solution
is ready for deployment.


### 18. Documentation

We will use MkDocs to build the documentation. The documentation will be
deployed to GitHub Pages. The documentation will contain at least the following
sections:

1. Problem
2. Solution
3. Installation
4. Rest API
5. README.md

### 19. Create the CI/CD pipeline

We will create a GitHub Actions workflow to run the tests on every push to the
main branch. We will also create a GitHub Actions workflow to build and push the
Docker image to Docker Hub on every release.

What we want:

1. Run the tests on every push to the main branch.
3. Build and push the Docker image to Docker Hub on each push.
4. Build the documentation and deploy it to GitHub Pages on every release.

### 20. Tag the first increment

Till now, we were in the pre-development phase. After the tag, changes will be
tracked using concrete issues in the commit messages.

## Part II — From kata prototype to a deployable service

After the first tag the work shifted from "solve the kata" to "turn the
prototype into a small, well-engineered service someone can run, read, and
trust." This part records the design decisions of that phase as a narrative;
each links to its ADR in `docs/decisions/` for the full rationale.

### 21. Restructure the package and the toolchain

The single-module prototype became a proper package: a `src/` layout, an
application factory (`create_app()`), and route blueprints in place of a
module-level app, so the app can be built and tested in isolation (ADR-001).
The build moved to a PEP 621 `pyproject.toml`, and linting and typing moved from
the IDE linter to `ruff` and `mypy` running in CI (ADR-002).

### 22. Treat the API as a versioned contract

The configuration endpoint sketched in Part I was dropped: generation is
per-request and stateless, with the distribution passed on each call (ADR-003),
expressed as explicit value:probability pairs (ADR-004). The two generators were
placed behind versioned paths — `/api/v1`, `/api/v2` — treated as a public
contract that is never changed in place; a new version is added instead
(ADR-005), each wired up from a registry (ADR-022), with the endpoints given
clearer names (ADR-023). The contract itself became design-first: `openapi.yaml`
is the single source of truth, served at `/openapi.json` and rendered as docs
(ADR-016, ADR-013), and its version is tracked independently of the package
version (ADR-021).

### 23. Keep two generators behind one interface

The two implementations — one using `random.choices`, one drawing from a
cumulative-probability walk — were kept behind a single interface so callers are
decoupled from the strategy (ADR-006). Fairness is checked with a Chi-Square
goodness-of-fit test rather than by eyeballing a histogram (ADR-007).

### 24. Make it runnable and observable

The container moved to a digest-pinned, non-root image served by gunicorn
(ADR-008), deployed as a free Render demo through an image deploy hook (ADR-009,
ADR-017). Configuration became environment-driven (ADR-024), and request logging
was added so the running service is observable, with a generic 500 that does not
leak internals (ADR-025).

### 25. Make the engineering legible

The narrative documentation moved to arc42 with a dedicated ADR folder (ADR-010,
ADR-012, ADR-015); issues adopted a label standard and technical debt is tracked
as tickets rather than buried in prose (ADR-014, ADR-018); CI/CD was split one
gate per job with SAST and branch protection (ADR-020); and the end-of-session
checklist was inlined into the agent instructions to keep the process repeatable
(ADR-011).
