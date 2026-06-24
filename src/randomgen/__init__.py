"""RandomGen — a Flask REST API for sampling discrete distributions."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version('randomgen')
except PackageNotFoundError:  # pragma: no cover - only when running uninstalled
    __version__ = '0.0.0+unknown'

__all__ = ['__version__']
