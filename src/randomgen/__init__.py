"""RandomGen — a Flask REST API for sampling discrete distributions."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('randomgen')
except PackageNotFoundError:  # package is not installed (e.g. running from src)
    __version__ = '0.0.0+unknown'

__all__ = ['__version__']
