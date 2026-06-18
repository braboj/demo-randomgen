# How to contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

First, read these guidelines. Before you begin making changes, state your 
intent to do so in an Issue. Then, fork the project. Make changes in your 
copy of the repository. Then open a pull request once your changes are ready.
A discussion about your change will follow, and if accepted, your contribution
will be incorporated into the project codebase.

## Code reviews

All submissions, including submissions by project members, require review.
Consult [GitHub Help] for more information on using pull requests.

[GitHub Help]: https://help.github.com/articles/about-pull-requests/

## Code style

In general, the project follows the guidelines in the
[Google Python Style Guide].

In addition, the project follows a convention of:
- Maximum line length: 80 characters
- Indentation: 4 spaces
- PascalCase for function and method names.
- No type hints, as described in [PEP 484], to maintain compatibility with
Python versions < 3.5.
- Single quotes around strings, three double quotes around docstrings.

[Google Python Style Guide]: http://google.github.io/styleguide/pyguide.html
[PEP 484]: https://www.python.org/dev/peps/pep-0484

## Testing

Use [GitHub Actions] to run tests on each pull request. You can run these 
tests yourself as well. To do this, first install the project with its
test dependencies:

[GitHub Actions]: https://github.com/braboj/randomgen/actions

```bash
pip install -e ".[test]"
```

And then run the tests:

```bash
pytest
```

## Linting

Please lint and type-check your pull requests to make accepting them
easier. From the repository root:

```bash
pip install -e ".[dev]"   # installs ruff + mypy
ruff check .
ruff format --check .
mypy
```

Note that even if these pass, additional style changes to your
submission may be made during merging.

## References

- [Google Python Fire Project](https://github.com/google/python-fire)